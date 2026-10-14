import Foundation
import Metal
import MetalPerformanceShaders
import CryptoKit
import Darwin

let baseCount = 10_000, queryCount = 100, dimension = 128, topK = 10, byteCap = 64 * 1024 * 1024
struct Failure: Error, CustomStringConvertible { let description: String; init(_ s: String) { description = s } }
func require(_ ok: Bool, _ message: String) throws { if !ok { throw Failure(message) } }
struct Clock {
    let epoch = DispatchTime.now().uptimeNanoseconds
    func now() -> Double { Double(DispatchTime.now().uptimeNanoseconds - epoch) / 1e9 }
}
func hashBytes(_ bytes: UnsafeRawBufferPointer) -> String {
    var hash = SHA256(); hash.update(bufferPointer: bytes)
    return hash.finalize().map { String(format: "%02x", $0) }.joined()
}
func hashWords(_ words: [UInt32]) -> String {
    let canonical = words.map(\.littleEndian)
    return canonical.withUnsafeBytes { hashBytes($0) }
}
func word(_ p: UnsafePointer<UInt8>, _ offset: Int) -> UInt32 {
    UInt32(p[offset]) | UInt32(p[offset+1]) << 8 | UInt32(p[offset+2]) << 16 | UInt32(p[offset+3]) << 24
}
func parseFvecs(_ data: Data, rows: Int, d: Int) throws -> [UInt8] {
    try require(rows > 0 && d > 0 && d <= dimension && data.count == rows * (d + 1) * 4, "Wrong fvecs byte length/dimension")
    var values = [UInt8](repeating: 0, count: rows * d)
    try data.withUnsafeBytes { raw in
        let p = raw.bindMemory(to: UInt8.self).baseAddress!
        for i in 0..<rows {
            let start = i * (d + 1) * 4
            try require(word(p, start) == UInt32(d), "Wrong dimension header at row \(i)")
            for j in 0..<d {
                let x = Float(bitPattern: word(p, start + 4 + j * 4))
                try require(x.isFinite && x >= 0 && x <= 255 && x.rounded(.towardZero) == x,
                            "Non-integral/out-of-range coordinate at row \(i), column \(j)")
                values[i * d + j] = UInt8(x)
            }
        }
    }
    return values
}
func loadFvecs(_ path: String, rows: Int) throws -> (values: [UInt8], sha: String) {
    let expected = rows * (dimension + 1) * 4, fd = open(path, O_RDONLY | O_NOFOLLOW)
    try require(fd >= 0, "Cannot open input: \(path)"); defer { close(fd) }
    var st = stat(); try require(fstat(fd, &st) == 0 && st.st_mode & S_IFMT == S_IFREG && st.st_size == expected, "Input must be regular with exact byte length")
    var data = Data(count: expected)
    try data.withUnsafeMutableBytes { bytes in
        var offset = 0
        while offset < expected {
            let n = read(fd, bytes.baseAddress!.advanced(by: offset), expected - offset)
            if n < 0 && errno == EINTR { continue }
            try require(n > 0, "Input read failed/truncated"); offset += n
        }
    }
    try require(fstat(fd, &st) == 0 && st.st_size == expected, "Input length changed while reading")
    let values = try parseFvecs(data, rows: rows, d: dimension)
    return (values, data.withUnsafeBytes { hashBytes($0) })
}
func norms(_ values: [UInt8], rows: Int, d: Int) -> [Int64] {
    (0..<rows).map { i in (0..<d).reduce(Int64(0)) { let x = Int64(values[i*d+$1]); return $0+x*x } }
}
struct Neighbor: Encodable, Equatable { let id: Int, distance: UInt32 }
func insert(_ candidate: Neighbor, into best: inout [Neighbor], k: Int) {
    let index = best.firstIndex { candidate.distance < $0.distance || (candidate.distance == $0.distance && candidate.id < $0.id) } ?? best.count
    if index < k { best.insert(candidate, at: index); if best.count > k { best.removeLast() } }
}
func reconstruct(_ dot: Float, qNorm: Int64, xNorm: Int64, d: Int) -> UInt32? {
    let bound = Int64(d) * 255 * 255
    guard dot.isFinite, dot >= 0, dot <= Float(bound), dot.rounded(.towardZero) == dot else { return nil }
    let distance = qNorm + xNorm - 2 * Int64(dot)
    guard distance >= 0 && distance <= bound else { return nil }
    return UInt32(distance)
}
func gpuRow(_ dots: UnsafePointer<Float>, localRow: Int, stride: Int, qNorm: Int64, xNorms: [Int64], d: Int, k: Int) -> ([UInt32], [Neighbor], Int) {
    var distances = [UInt32](repeating: .max, count: xNorms.count), best: [Neighbor] = [], invalid = 0
    best.reserveCapacity(k + 1)
    for j in xNorms.indices {
        if let distance = reconstruct(dots[localRow * stride + j], qNorm: qNorm, xNorm: xNorms[j], d: d) {
            distances[j] = distance; insert(Neighbor(id: j, distance: distance), into: &best, k: k)
        } else { invalid += 1 }
    }
    return (distances, best, invalid)
}
// Independent oracle: direct coordinate differences, with no dot products or norm identity.
func oracle(_ query: ArraySlice<UInt8>, _ base: [UInt8], rows: Int, d: Int) -> [UInt32] {
    var result = [UInt32](repeating: 0, count: rows)
    for i in 0..<rows {
        var sum: Int64 = 0
        for j in 0..<d { let delta = Int64(query[query.startIndex+j]) - Int64(base[i*d+j]); sum += delta*delta }
        result[i] = UInt32(sum)
    }
    return result
}
func fullSortTop(_ distances: [UInt32], k: Int) -> [Neighbor] {
    let ids = distances.indices.sorted { distances[$0] == distances[$1] ? $0 < $1 : distances[$0] < distances[$1] }
    return ids.prefix(k).map { Neighbor(id: $0, distance: distances[$0]) }
}
func compare(_ actual: UnsafePointer<UInt32>, _ expected: [UInt32]) -> (count: Int, mismatches: Int, maximum: Int64) {
    var mismatches = 0, maximum: Int64 = 0
    for i in expected.indices { let difference = abs(Int64(actual[i])-Int64(expected[i])); if difference != 0 { mismatches += 1 }; maximum = max(maximum, difference) }
    return (expected.count, mismatches, maximum)
}
struct Query: Encodable {
    let query_id: Int, batch_index: Int
    var status = "not_run", passed = false, compared_distances = 0, mismatch_count = 0, invalid_dot_count = 0
    var max_abs_error: Int64 = 0, top10: [Neighbor] = [], cpu_top10: [Neighbor] = [], top10_exact_match = false
    var gpu_distance_sha256: String?, cpu_distance_sha256: String?, failure: String?
    var reconstruction_selection_seconds: Double?, cpu_oracle_validation_seconds: Double?
}
struct Batch: Encodable {
    let index: Int, query_start: Int, query_count: Int
    var status = "not_run", passed = false, command_buffer_status: Int?, command_buffer_error: String?, failure: String?
    var preparation_start_s: Double?, submit_s: Double?, gpu_completion_observed_s: Double?
    var reconstruction_start_s: Double?, reconstruction_end_s: Double?, oracle_start_s: Double?, oracle_end_s: Double?, resource_release_s: Double?
    var preparation_seconds: Double?, gpu_submit_to_completion_seconds: Double?, reconstruction_selection_seconds: Double?, cpu_oracle_validation_seconds: Double?
    var gpu_start_time: Double?, gpu_end_time: Double?, gpu_interval_seconds: Double?
    var query_row_bytes = 0, dot_row_bytes = 0, query_buffer_payload_bytes = 0, dot_buffer_payload_bytes = 0
    var query_buffer_length_bytes = 0, dot_buffer_length_bytes = 0, query_buffer_allocated_bytes = 0, dot_buffer_allocated_bytes = 0
    var device_allocated_before_buffers_sample: Int?, device_allocated_with_buffers_sample: Int?, device_allocated_after_release_sample: Int?
    var explicit_bound_bytes = 0
}
struct Memory: Encodable {
    var cap_bytes = byteCap
    var input_file_staging_bound_bytes = (baseCount + queryCount) * (dimension + 1) * 4
    var input_vector_bytes = (baseCount + queryCount) * dimension, integer_norm_bytes = (baseCount + queryCount) * 8
    var distance_matrix_bytes = queryCount * baseCount * 4, distance_serialization_bytes = queryCount * baseCount * 4
    var cpu_selection_hash_scratch_bound_bytes = 512 * 1024, top10_storage_bound_bytes = queryCount * topK * 4 * MemoryLayout<Neighbor>.stride
    var base_buffer_payload_bytes = baseCount * dimension * 4, base_row_bytes = 0, base_buffer_length_bytes = 0, base_buffer_allocated_bytes = 0
    var maximum_batch_buffer_allocated_bytes = 0, conservative_explicit_bound_bytes = 0
    var device_allocated_before_base_sample: Int?, device_allocated_with_base_sample: Int?, device_allocated_before_retrieve_return_sample: Int?
    var fixed: Int { input_file_staging_bound_bytes + input_vector_bytes + integer_norm_bytes + distance_matrix_bytes + distance_serialization_bytes + cpu_selection_hash_scratch_bound_bytes + top10_storage_bound_bytes }
}
struct Report: Encodable {
    var schema_version = 1, protocol_id = "mac-sift10k-retrieval-v1"
    let batch_size: Int, base_count = baseCount, query_count = queryCount, dimensions = dimension, top_k = topK
    var started_at = ISO8601DateFormatter().string(from: Date())
    var completed_at: String? = nil
    var clock_origin_uptime_ns: UInt64
    var input_base_sha256: String?, input_query_sha256: String?, inputs_validated = false, cpu_self_test_passed = false
    var device_name: String?, has_unified_memory: Bool?, max_buffer_length: Int?, recommended_max_working_set_size: UInt64?
    var queries: [Query], batches: [Batch], memory = Memory(), gate_passed = false
    var failure: String? = nil
    var input_read_validate_seconds: Double?, index_prepare_seconds: Double?, distances_write_seconds: Double?, processing_through_distance_output_seconds: Double?
    var distance_file = "distances.u32le", distance_file_bytes = queryCount * baseCount * 4, distance_file_sha256: String?
    var encoding = "Query-major UInt32 little-endian squared L2; UInt32.max marks invalid/unrun. Row hashes use the same encoding. Top ten order is (distance, original row ID)."
    var interpretation = "GPU computes dots; CPU reconstructs and selects. Descriptive times only; RAW JSON serialization excluded, outer process interval includes it. Explicit memory bound includes conservatively simultaneous input staging and output serialization; excludes framework allocations, metadata and file caches. Device counters are global samples, not peaks or free RAM."
}
func runBatch(_ initial: Batch, device: MTLDevice, queue: MTLCommandQueue, baseBuffer: MTLBuffer, baseDescriptor: MPSMatrixDescriptor,
              base: [UInt8], queries: [UInt8], xNorms: [Int64], qNorms: [Int64], clock: Clock,
              fixedBytes: Int, reportRows: inout [Query], output: inout [UInt32]) -> Batch {
    var batch = initial; batch.preparation_start_s = clock.now(); batch.status = "started"
    do {
        let count = batch.query_count, rb = MPSMatrixDescriptor.rowBytes(fromColumns: dimension, dataType: .float32)
        let cb = MPSMatrixDescriptor.rowBytes(fromColumns: baseCount, dataType: .float32)
        try require(rb >= dimension*4 && cb >= baseCount*4 && rb%4 == 0 && cb%4 == 0, "Invalid matrix row stride")
        batch.query_row_bytes = rb; batch.dot_row_bytes = cb
        batch.query_buffer_payload_bytes = count*dimension*4; batch.dot_buffer_payload_bytes = count*baseCount*4
        batch.query_buffer_length_bytes = count*rb; batch.dot_buffer_length_bytes = count*cb
        try require(fixedBytes + baseBuffer.allocatedSize + count*(rb+cb) <= byteCap && count*cb <= device.maxBufferLength && count*rb <= device.maxBufferLength, "Requested explicit cap exceeded")
        batch.device_allocated_before_buffers_sample = device.currentAllocatedSize
        guard let q = device.makeBuffer(length: count*rb, options: .storageModeShared),
              let dots = device.makeBuffer(length: count*cb, options: .storageModeShared) else { throw Failure("Batch buffer allocation failed") }
        batch.query_buffer_allocated_bytes = q.allocatedSize; batch.dot_buffer_allocated_bytes = dots.allocatedSize
        batch.explicit_bound_bytes = fixedBytes + baseBuffer.allocatedSize + q.allocatedSize + dots.allocatedSize
        batch.device_allocated_with_buffers_sample = device.currentAllocatedSize
        try require(batch.explicit_bound_bytes <= byteCap, "Allocated explicit cap exceeded")
        let qp = q.contents().bindMemory(to: Float.self, capacity: count*rb/4), cp = dots.contents().bindMemory(to: Float.self, capacity: count*cb/4)
        qp.initialize(repeating: 0, count: count*rb/4); cp.initialize(repeating: .nan, count: count*cb/4)
        for i in 0..<count { for j in 0..<dimension { qp[i*rb/4+j] = Float(queries[(batch.query_start+i)*dimension+j]) } }
        let qd = MPSMatrixDescriptor(rows: count, columns: dimension, rowBytes: rb, dataType: .float32)
        let cd = MPSMatrixDescriptor(rows: count, columns: baseCount, rowBytes: cb, dataType: .float32)
        let qm = MPSMatrix(buffer: q, descriptor: qd), bm = MPSMatrix(buffer: baseBuffer, descriptor: baseDescriptor), cm = MPSMatrix(buffer: dots, descriptor: cd)
        let kernel = MPSMatrixMultiplication(device: device, transposeLeft: false, transposeRight: true, resultRows: count,
                                            resultColumns: baseCount, interiorColumns: dimension, alpha: 1, beta: 0)
        kernel.options = .none
        guard let command = queue.makeCommandBuffer() else { throw Failure("Command creation failed") }
        kernel.encode(commandBuffer: command, leftMatrix: qm, rightMatrix: bm, resultMatrix: cm)
        batch.submit_s = clock.now(); batch.preparation_seconds = batch.submit_s! - batch.preparation_start_s!
        command.commit(); command.waitUntilCompleted(); batch.gpu_completion_observed_s = clock.now()
        batch.gpu_submit_to_completion_seconds = batch.gpu_completion_observed_s! - batch.submit_s!
        batch.command_buffer_status = Int(command.status.rawValue); batch.command_buffer_error = command.error?.localizedDescription
        let gs = command.gpuStartTime, ge = command.gpuEndTime
        if gs.isFinite && ge.isFinite && gs > 0 && ge > gs { batch.gpu_start_time = gs; batch.gpu_end_time = ge; batch.gpu_interval_seconds = ge-gs }
        try require(command.status == .completed && command.error == nil, "GPU command did not complete successfully")
        batch.reconstruction_start_s = clock.now()
        for local in 0..<count {
            let id = batch.query_start+local, start = clock.now()
            let (distances, best, invalid) = gpuRow(cp, localRow: local, stride: cb/4, qNorm: qNorms[id], xNorms: xNorms, d: dimension, k: topK)
            for j in 0..<baseCount { output[id*baseCount+j] = distances[j] }
            reportRows[id].top10 = best; reportRows[id].invalid_dot_count = invalid
            reportRows[id].gpu_distance_sha256 = hashWords(distances); reportRows[id].status = "reconstructed"
            reportRows[id].reconstruction_selection_seconds = clock.now()-start
        }
        batch.reconstruction_end_s = clock.now(); batch.reconstruction_selection_seconds = batch.reconstruction_end_s! - batch.reconstruction_start_s!
        batch.oracle_start_s = clock.now()
        for id in batch.query_start..<(batch.query_start+count) {
            let start = clock.now(), expected = oracle(queries[(id*dimension)..<((id+1)*dimension)], base, rows: baseCount, d: dimension)
            let check = output.withUnsafeBufferPointer { compare($0.baseAddress!.advanced(by: id*baseCount), expected) }
            reportRows[id].compared_distances = check.count; reportRows[id].mismatch_count = check.mismatches; reportRows[id].max_abs_error = check.maximum
            reportRows[id].cpu_top10 = fullSortTop(expected, k: topK); reportRows[id].cpu_distance_sha256 = hashWords(expected)
            reportRows[id].top10_exact_match = reportRows[id].top10 == reportRows[id].cpu_top10
            reportRows[id].passed = check.count == baseCount && check.mismatches == 0 && reportRows[id].invalid_dot_count == 0 && reportRows[id].top10_exact_match && reportRows[id].top10.count == topK
            reportRows[id].status = reportRows[id].passed ? "passed" : "failed"
            if !reportRows[id].passed { reportRows[id].failure = "Exact distance/top-ten comparison failed" }
            reportRows[id].cpu_oracle_validation_seconds = clock.now()-start
        }
        batch.oracle_end_s = clock.now(); batch.cpu_oracle_validation_seconds = batch.oracle_end_s! - batch.oracle_start_s!
        try require(reportRows[batch.query_start..<(batch.query_start+count)].allSatisfy(\.passed), "Batch correctness failed")
        batch.passed = true; batch.status = "passed"
    } catch {
        batch.status = "failed"; batch.failure = String(describing: error)
        for id in batch.query_start..<(batch.query_start+batch.query_count) where reportRows[id].status == "not_run" || reportRows[id].status == "reconstructed" {
            reportRows[id].status = "failed"; reportRows[id].failure = batch.failure
        }
    }
    return batch
}
func retrieve(_ base: [UInt8], _ queries: [UInt8], report: inout Report, output: inout [UInt32], clock: Clock) throws {
    let start = clock.now(), xNorms = norms(base, rows: baseCount, d: dimension), qNorms = norms(queries, rows: queryCount, d: dimension)
    guard let device = MTLCreateSystemDefaultDevice() else { throw Failure("No Metal device") }
    report.device_name = device.name; report.has_unified_memory = device.hasUnifiedMemory
    report.max_buffer_length = device.maxBufferLength; report.recommended_max_working_set_size = device.recommendedMaxWorkingSetSize
    try require(device.hasUnifiedMemory, "Unified-memory device required")
    // This sample precedes the enclosing autoreleasepool's teardown; it is not a post-cleanup sample.
    defer { report.memory.device_allocated_before_retrieve_return_sample = device.currentAllocatedSize }
    guard let queue = device.makeCommandQueue() else { throw Failure("No command queue") }
    let rb = MPSMatrixDescriptor.rowBytes(fromColumns: dimension, dataType: .float32), bytes = baseCount*rb
    try require(rb >= dimension*4 && rb%4 == 0 && bytes <= device.maxBufferLength && report.memory.fixed+bytes <= byteCap, "Invalid base matrix size/cap")
    report.memory.base_row_bytes = rb; report.memory.base_buffer_length_bytes = bytes
    report.memory.device_allocated_before_base_sample = device.currentAllocatedSize
    guard let buffer = device.makeBuffer(length: bytes, options: .storageModeShared) else { throw Failure("Base allocation failed") }
    report.memory.base_buffer_allocated_bytes = buffer.allocatedSize; report.memory.device_allocated_with_base_sample = device.currentAllocatedSize
    report.memory.conservative_explicit_bound_bytes = report.memory.fixed + buffer.allocatedSize
    try require(report.memory.conservative_explicit_bound_bytes <= byteCap, "Allocated base cap exceeded")
    let p = buffer.contents().bindMemory(to: Float.self, capacity: bytes/4); p.initialize(repeating: 0, count: bytes/4)
    for i in 0..<baseCount { for j in 0..<dimension { p[i*rb/4+j] = Float(base[i*dimension+j]) } }
    let descriptor = MPSMatrixDescriptor(rows: baseCount, columns: dimension, rowBytes: rb, dataType: .float32)
    report.index_prepare_seconds = clock.now()-start
    for i in report.batches.indices {
        var batch = autoreleasepool { runBatch(report.batches[i], device: device, queue: queue, baseBuffer: buffer, baseDescriptor: descriptor,
            base: base, queries: queries, xNorms: xNorms, qNorms: qNorms, clock: clock, fixedBytes: report.memory.fixed, reportRows: &report.queries, output: &output) }
        batch.resource_release_s = clock.now(); batch.device_allocated_after_release_sample = device.currentAllocatedSize
        report.batches[i] = batch
        report.memory.maximum_batch_buffer_allocated_bytes = max(report.memory.maximum_batch_buffer_allocated_bytes, batch.query_buffer_allocated_bytes+batch.dot_buffer_allocated_bytes)
        report.memory.conservative_explicit_bound_bytes = max(report.memory.conservative_explicit_bound_bytes, batch.explicit_bound_bytes)
        try require(batch.passed, batch.failure ?? "Batch failed")
    }
}
func publish(_ bytes: UnsafeRawBufferPointer, to path: String) throws {
    let temporary = URL(fileURLWithPath: path).deletingLastPathComponent().path + "/.retrieve-" + UUID().uuidString
    let fd = open(temporary, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, S_IRUSR | S_IWUSR)
    try require(fd >= 0, "Cannot exclusively create output temporary"); defer { close(fd); unlink(temporary) }
    var offset = 0
    while offset < bytes.count {
        let n = write(fd, bytes.baseAddress!.advanced(by: offset), bytes.count-offset)
        if n < 0 && errno == EINTR { continue }; try require(n > 0, "Output write failed"); offset += n
    }
    try require(fsync(fd) == 0 && link(temporary, path) == 0, "Output publication failed/refused")
}
func selfTest() throws {
    let base: [UInt8] = [1,2,3, 0,0,0, 4,0,2, 2,2,2], q: [UInt8] = [1,2,3, 4,0,2]
    let dots: [Float] = [14,0,10,12,.nan,.nan,.nan,.nan, 10,0,20,12,.nan,.nan,.nan,.nan]
    let golden: [[UInt32]] = [[0,14,14,2],[14,20,0,8]], xn = norms(base, rows: 4, d: 3), qn = norms(q, rows: 2, d: 3)
    for i in 0..<2 {
        let (got, best, bad) = dots.withUnsafeBufferPointer { gpuRow($0.baseAddress!, localRow: i, stride: 8, qNorm: qn[i], xNorms: xn, d: 3, k: 4) }
        try require(got == golden[i] && bad == 0 && oracle(q[(i*3)..<(i*3+3)], base, rows: 4, d: 3) == golden[i], "Rectangular/padded golden failed")
        try require(best == fullSortTop(golden[i], k: 4), "Golden selection failed")
    }
    var tied: [Neighbor] = []; for id in (0..<12).reversed() { insert(Neighbor(id: id, distance: 0), into: &tied, k: 10) }
    try require(tied.map(\.id) == Array(0..<10) && fullSortTop([UInt32](repeating: 0, count: 12), k: 10) == tied, "Cutoff tie ordering failed")
    try require(reconstruct(8_290_560, qNorm: 8_323_200, xNorm: 8_258_048, d: 128) == 128 && reconstruct(0, qNorm: 0, xNorm: 8_323_200, d: 128) == 8_323_200, "High-value exactness failed")
    for bad: Float in [.nan, .infinity, -.infinity, -1, 0.5, 8_323_201] { try require(reconstruct(bad, qNorm: 0, xNorm: 0, d: 128) == nil, "Invalid dot accepted") }
    try require(reconstruct(1, qNorm: 0, xNorm: 0, d: 128) == nil, "Negative distance accepted")
    var corrupt: [UInt32] = [1,2,3,5]
    let check = corrupt.withUnsafeBufferPointer { compare($0.baseAddress!, [1,2,3,4]) }
    try require(check.count == 4 && check.mismatches == 1 && check.maximum == 1, "Final-entry corruption accepted")
    func fixture(_ fields: [UInt32]) -> Data { fields.map(\.littleEndian).withUnsafeBytes { Data($0) } }
    let valid = fixture([3,Float(0).bitPattern,Float(128).bitPattern,Float(255).bitPattern])
    try require(try parseFvecs(valid, rows: 1, d: 3) == [0,128,255], "Valid parser fixture failed")
    var invalid = [Data(valid.dropLast()), valid+Data([0]), fixture([2,0,0,0])]
    for x: Float in [.nan,.infinity,-1,0.25,256] { invalid.append(fixture([3,0,0,x.bitPattern])) }
    for bad in invalid { do { _ = try parseFvecs(bad, rows: 1, d: 3); throw Failure("Invalid parser fixture accepted") } catch let e as Failure { try require(e.description != "Invalid parser fixture accepted", e.description) } }
    corrupt = [0,1,256,8_323_200]
    try require(hashWords(corrupt) == "a6cf483fa4e8f4eee26b7f9147d8c541e145779ac6d90eed18fb18cc01429232", "Canonical hash failed")
}
func main() -> Int32 {
    do {
        let args = Array(CommandLine.arguments.dropFirst())
        if args == ["--self-test"] { try selfTest(); print("CPU_ONLY_SELF_TEST_PASS rectangular/padding/ties/bounds/invaliddots/finalcorruption/parser/UInt32LEhash"); return 0 }
        try require(args.count == 6, "Usage: retrieve --data /absolute/data --batch-size 1|16 --output-dir /absolute/NEWdir | --self-test")
        var flags: [String:String] = [:]
        for i in stride(from: 0, to: args.count, by: 2) { try require(["--data","--batch-size","--output-dir"].contains(args[i]) && flags[args[i]] == nil, "Unknown/duplicate flag"); flags[args[i]] = args[i+1] }
        guard let dataPath = flags["--data"], dataPath.hasPrefix("/"), let size = Int(flags["--batch-size"] ?? ""), [1,16].contains(size),
              let out = flags["--output-dir"], out.hasPrefix("/") else { throw Failure("Invalid options") }
        try require(mkdir(out, S_IRWXU) == 0, "Output directory exists or cannot be created")
        let clock = Clock()
        var report = Report(batch_size: size, clock_origin_uptime_ns: clock.epoch,
            queries: (0..<queryCount).map { Query(query_id: $0, batch_index: $0/size) },
            batches: stride(from: 0, to: queryCount, by: size).enumerated().map { Batch(index: $0.offset, query_start: $0.element, query_count: min(size,queryCount-$0.element)) })
        var distances = [UInt32](repeating: .max, count: queryCount*baseCount)
        do {
            try selfTest(); report.cpu_self_test_passed = true
            let start = clock.now(), base = try loadFvecs(dataPath+"/siftsmall_base.fvecs", rows: baseCount)
            report.input_base_sha256 = base.sha
            let queries = try loadFvecs(dataPath+"/siftsmall_query.fvecs", rows: queryCount)
            report.input_query_sha256 = queries.sha; report.inputs_validated = true; report.input_read_validate_seconds = clock.now()-start
            try autoreleasepool { try retrieve(base.values, queries.values, report: &report, output: &distances, clock: clock) }
            report.gate_passed = report.queries.count == queryCount && report.queries.allSatisfy(\.passed) && report.batches.allSatisfy(\.passed)
        } catch { report.failure = String(describing: error) }
        let start = clock.now(), canonical = distances.map(\.littleEndian)
        report.distance_file_sha256 = canonical.withUnsafeBytes { hashBytes($0) }
        try canonical.withUnsafeBytes { try publish($0, to: out+"/distances.u32le") }
        report.distances_write_seconds = clock.now()-start; report.processing_through_distance_output_seconds = clock.now()
        report.completed_at = ISO8601DateFormatter().string(from: Date())
        let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted,.sortedKeys]
        try encoder.encode(report).withUnsafeBytes { try publish($0, to: out+"/RAW.json") }
        print(report.gate_passed ? "RETRIEVAL_PASS" : "RETRIEVAL_FAIL"); return report.gate_passed ? 0 : 1
    } catch { fputs("retrieve: \(error)\n", stderr); return 2 }
}
exit(main())
