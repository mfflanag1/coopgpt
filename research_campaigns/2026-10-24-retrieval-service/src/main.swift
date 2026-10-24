import Foundation
import Metal
import MetalPerformanceShaders
import Darwin

struct Request: Codable { let request_id: String; let query_id: Int }
struct Command: Decodable { let batch_id: Int; let requests: [Request] }
struct Answer: Encodable {
    let request_id: String, query_id: Int, passed: Bool, compared_distances: Int
    let mismatch_count: Int, invalid_dot_count: Int
    let top10: [Neighbor], distance_sha256: String
}
func emit(_ value: Any) throws {
    let data = try JSONSerialization.data(withJSONObject: value, options: [.sortedKeys])
    try FileHandle.standardOutput.write(contentsOf: data + Data([10]))
}
func jsonObject<T: Encodable>(_ value: T) throws -> Any {
    try JSONSerialization.jsonObject(with: JSONEncoder().encode(value))
}

// One engine owns one corpus and command queue for the complete window, including
// warmup. There is no answer cache: the oracle and full candidate run every time.
final class Engine {
    let synthetic: Bool, rows: Int, d: Int
    let base: [UInt8], queries: [UInt8], xn: [Int64], qn: [Int64]
    let device: MTLDevice?, queue: MTLCommandQueue?, baseBuffer: MTLBuffer?
    let baseDescriptor: MPSMatrixDescriptor?
    let baseSHA: String, querySHA: String
    // Conservative explicitly managed array/scratch/staging allowance, not RSS.
    let fixedBytes = 8 * 1024 * 1024 + 5_211_600 + 1_292_800 + 80_800

    init(dataPath: String?, synthetic: Bool) throws {
        self.synthetic = synthetic
        if synthetic {
            rows = 32; d = 3
            var b: [UInt8] = [], q: [UInt8] = []
            for i in 0..<96 { b.append(UInt8((i * 7 + i / 3) % 17)) }
            for i in 0..<300 { q.append(UInt8((i * 11 + 3) % 19)) }
            base = b; queries = q
            baseSHA = "synthetic"; querySHA = "synthetic"
        } else {
            rows = baseCount; d = dimension
            guard let path = dataPath else { throw Failure("Missing corpus path") }
            let b = try loadFvecs(path + "/siftsmall_base.fvecs", rows: baseCount)
            let q = try loadFvecs(path + "/siftsmall_query.fvecs", rows: queryCount)
            try require(b.sha == "1e90414a3254361aba48a0d58e461f7661fb135dabb3da985290e94de8f60fe0", "Base hash mismatch")
            try require(q.sha == "095af38bda2741be721447ba97e9286fa918ece946be92a9ae133276eddc1a10", "Query hash mismatch")
            base = b.values; queries = q.values; baseSHA = b.sha; querySHA = q.sha
        }
        xn = norms(base, rows: rows, d: d); qn = norms(queries, rows: queryCount, d: d)
        if synthetic {
            device = nil; queue = nil; baseBuffer = nil; baseDescriptor = nil
        } else {
            guard let dev = MTLCreateSystemDefaultDevice(), dev.hasUnifiedMemory,
                  let commandQueue = dev.makeCommandQueue() else { throw Failure("Unified-memory Metal device/queue required") }
            let rb = MPSMatrixDescriptor.rowBytes(fromColumns: d, dataType: .float32)
            try require(rb >= d*4 && rb%4 == 0 && rows*rb <= dev.maxBufferLength && fixedBytes+rows*rb <= byteCap, "Base size/cap")
            guard let buffer = dev.makeBuffer(length: rows*rb, options: .storageModeShared) else { throw Failure("Base allocation") }
            try require(fixedBytes+buffer.allocatedSize <= byteCap, "Base allocated cap")
            let p = buffer.contents().bindMemory(to: Float.self, capacity: rows*rb/4)
            p.initialize(repeating: 0, count: rows*rb/4)
            for i in 0..<rows { for j in 0..<d { p[i*rb/4+j] = Float(base[i*d+j]) } }
            device = dev; queue = commandQueue; baseBuffer = buffer
            baseDescriptor = MPSMatrixDescriptor(rows: rows, columns: d, rowBytes: rb, dataType: .float32)
        }
    }

    func solve(_ command: Command) throws -> [Answer] {
        try require((1...16).contains(command.requests.count), "Batch count outside 1...16")
        try require(Set(command.requests.map(\.request_id)).count == command.requests.count, "Duplicate request IDs")
        for r in command.requests { try require((0..<queryCount).contains(r.query_id) && !r.request_id.isEmpty, "Invalid query/request ID") }
        let count = command.requests.count
        if synthetic {
            // Exercises the same reconstruction, selection and independent oracle
            // on tiny artificial coordinates, without creating any Metal device.
            var dots = [Float](repeating: 0, count: count*rows)
            for (i,r) in command.requests.enumerated() {
                for j in 0..<rows { for k in 0..<d { dots[i*rows+j] += Float(queries[r.query_id*d+k]) * Float(base[j*d+k]) } }
            }
            return try dots.withUnsafeBufferPointer { try validate(command, dots: $0.baseAddress!, stride: rows) }
        }
        guard let dev = device, let queue = queue, let b = baseBuffer, let bd = baseDescriptor else { throw Failure("Engine not initialized") }
        let rb = MPSMatrixDescriptor.rowBytes(fromColumns: d, dataType: .float32)
        let cb = MPSMatrixDescriptor.rowBytes(fromColumns: rows, dataType: .float32)
        try require(rb >= d*4 && cb >= rows*4 && rb%4 == 0 && cb%4 == 0, "Invalid row strides")
        try require(count*rb <= dev.maxBufferLength && count*cb <= dev.maxBufferLength && fixedBytes+b.allocatedSize+count*(rb+cb) <= byteCap, "Batch size/cap")
        guard let q = dev.makeBuffer(length: count*rb, options: .storageModeShared),
              let dots = dev.makeBuffer(length: count*cb, options: .storageModeShared) else { throw Failure("Batch allocation") }
        try require(fixedBytes+b.allocatedSize+q.allocatedSize+dots.allocatedSize <= byteCap, "Allocated batch cap")
        let qp = q.contents().bindMemory(to: Float.self, capacity: count*rb/4)
        let cp = dots.contents().bindMemory(to: Float.self, capacity: count*cb/4)
        qp.initialize(repeating: 0, count: count*rb/4); cp.initialize(repeating: .nan, count: count*cb/4)
        for (i,r) in command.requests.enumerated() { for j in 0..<d { qp[i*rb/4+j] = Float(queries[r.query_id*d+j]) } }
        let qd = MPSMatrixDescriptor(rows: count, columns: d, rowBytes: rb, dataType: .float32)
        let cd = MPSMatrixDescriptor(rows: count, columns: rows, rowBytes: cb, dataType: .float32)
        let kernel = MPSMatrixMultiplication(device: dev, transposeLeft: false, transposeRight: true, resultRows: count,
            resultColumns: rows, interiorColumns: d, alpha: 1, beta: 0)
        kernel.options = .none
        guard let buffer = queue.makeCommandBuffer() else { throw Failure("Command buffer allocation") }
        kernel.encode(commandBuffer: buffer, leftMatrix: MPSMatrix(buffer: q, descriptor: qd),
                      rightMatrix: MPSMatrix(buffer: b, descriptor: bd), resultMatrix: MPSMatrix(buffer: dots, descriptor: cd))
        buffer.commit(); buffer.waitUntilCompleted()
        try require(buffer.status == .completed && buffer.error == nil, "GPU failure: \(buffer.error?.localizedDescription ?? "status")")
        return try validate(command, dots: cp, stride: cb/4)
    }

    func validate(_ command: Command, dots: UnsafePointer<Float>, stride: Int) throws -> [Answer] {
        var answers: [Answer] = []
        for (i,r) in command.requests.enumerated() {
            let (got, best, invalid) = gpuRow(dots, localRow: i, stride: stride, qNorm: qn[r.query_id], xNorms: xn, d: d, k: topK)
            let expected = oracle(queries[(r.query_id*d)..<((r.query_id+1)*d)], base, rows: rows, d: d)
            let check = got.withUnsafeBufferPointer { compare($0.baseAddress!, expected) }
            let ok = invalid == 0 && check.count == rows && check.mismatches == 0 && best == fullSortTop(expected, k: topK) && best.count == topK
            answers.append(Answer(request_id: r.request_id, query_id: r.query_id, passed: ok, compared_distances: check.count,
                mismatch_count: check.mismatches, invalid_dot_count: invalid, top10: best, distance_sha256: hashWords(got)))
        }
        return answers
    }
}

do {
    let args = Array(CommandLine.arguments.dropFirst())
    if args == ["--self-test"] {
        try selfTest()
        let e = try Engine(dataPath: nil, synthetic: true)
        let r = try e.solve(Command(batch_id: 0, requests: [Request(request_id: "a", query_id: 99), Request(request_id: "b", query_id: 0), Request(request_id: "c", query_id: 99)]))
        try require(r.allSatisfy(\.passed) && r[0].top10 == r[2].top10, "Synthetic arbitrary/repeated query failure")
        print("CPU_ONLY_SELF_TEST_PASS inherited arithmetic/parser/oracle plus persistent arbitrary-query batching")
    } else {
        let synthetic = args == ["--synthetic-service"]
        var dataPath: String? = nil
        if !synthetic {
            try require(args.count == 4 && args[0] == "--data" && args[2] == "--authorization", "Only --self-test, --synthetic-service, or --data PATH --authorization APPROVED_FREEZE.json")
            let approval = try JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: args[3]))) as? [String: Any]
            try require(approval?["authorized"] as? Bool == true && ["calibration","evaluation"].contains(approval?["stage"] as? String ?? ""), "Collection lacks explicit approved freeze")
            dataPath = args[1]
        }
        try selfTest()
        let engine = try Engine(dataPath: dataPath, synthetic: synthetic)
        try emit(["event":"ready", "synthetic":synthetic, "base_count":engine.rows, "query_count":queryCount,
                  "dimensions":engine.d, "base_sha256":engine.baseSHA, "query_sha256":engine.querySHA,
                  "device":engine.device?.name ?? "CPU synthetic only", "explicit_cap_bytes":byteCap,
                  "base_allocated_bytes":engine.baseBuffer?.allocatedSize ?? 0])
        while let line = readLine() {
            try require(line.utf8.count <= 65536, "Oversize command")
            let command = try JSONDecoder().decode(Command.self, from: Data(line.utf8))
            let start = DispatchTime.now().uptimeNanoseconds
            let answers = try autoreleasepool { try engine.solve(command) }
            try emit(["event":"response", "batch_id":command.batch_id, "answers":try jsonObject(answers),
                      "native_start_ns":start, "native_checked_ns":DispatchTime.now().uptimeNanoseconds])
        }
    }
} catch {
    try? emit(["event":"fatal", "error":String(describing:error)])
    fputs("retrieval-service: \(error)\n", stderr)
    exit(2)
}
