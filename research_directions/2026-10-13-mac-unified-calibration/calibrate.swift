import Foundation
import Metal
import MetalPerformanceShaders
import Accelerate
import CryptoKit
import Darwin

let order = [256, 512, 1024, 1024, 256, 512, 512, 1024, 256]
let byteCap = 64 * 1024 * 1024
struct Failure: Error, CustomStringConvertible { let description: String; init(_ s: String) { description = s } }
func require(_ value: Bool, _ reason: String) throws { if !value { throw Failure(reason) } }
struct Check: Codable {
    var compared_elements = 0, mismatch_count = 0, nonfinite_count = 0
    var max_abs_error: Double? = 0
    var max_abs_finite_error: Double = 0
    var passed: Bool { mismatch_count == 0 && nonfinite_count == 0 }
}
// Both collection and self-test use this complete, exact, row-stride-aware comparison.
func compare(_ actual: UnsafePointer<Float>, _ expected: UnsafePointer<Float>, n: Int, stride: Int) -> Check {
    var c = Check()
    for i in 0..<n { for j in 0..<n {
        let a = actual[i * stride + j], e = expected[i * n + j]
        c.compared_elements += 1
        if !a.isFinite || !e.isFinite { c.nonfinite_count += 1; c.mismatch_count += 1; continue }
        let error = abs(Double(a) - Double(e))
        if error != 0 { c.mismatch_count += 1 }
        c.max_abs_finite_error = max(c.max_abs_finite_error, error)
    } }
    c.max_abs_error = c.nonfinite_count == 0 ? c.max_abs_finite_error : nil
    return c
}
func canonicalHash(_ values: UnsafePointer<Float>, n: Int, stride: Int) -> String {
    var hash = SHA256(), row = [UInt32](repeating: 0, count: n)
    for i in 0..<n {
        for j in 0..<n {
            let value = values[i * stride + j]
            row[j] = (value == 0 ? UInt32(0) : value.bitPattern).littleEndian
        }
        row.withUnsafeBytes { hash.update(bufferPointer: $0) }
    }
    return hash.finalize().map { String(format: "%02x", $0) }.joined()
}
func fill(_ a: UnsafeMutablePointer<Float>, _ b: UnsafeMutablePointer<Float>, n: Int, stride: Int) {
    a.initialize(repeating: 0, count: n * stride); b.initialize(repeating: 0, count: n * stride)
    for i in 0..<n { for j in 0..<n {
        a[i * stride + j] = Float((i + 3 * j) % 7 - 3)
        b[i * stride + j] = Float((5 * i + j) % 11 - 5)
    } }
}
func reference(_ a: UnsafePointer<Float>, _ b: UnsafePointer<Float>, n: Int, stride: Int) -> [Float] {
    var result = [Float](repeating: 0, count: n * n)
    result.withUnsafeMutableBufferPointer { c in
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, Int32(n), Int32(n), Int32(n),
                    1, a, Int32(stride), b, Int32(stride), 0, c.baseAddress!, Int32(n))
    }
    return result
}
func selfTest() throws {
    let n = 4, stride = 8
    let a = UnsafeMutablePointer<Float>.allocate(capacity: n * stride)
    let b = UnsafeMutablePointer<Float>.allocate(capacity: n * stride)
    defer { a.deallocate(); b.deallocate() }
    fill(a, b, n: n, stride: stride)
    let golden: [Float] = [31,-3,-4,-5, -5,24,20,16, -6,16,16,16, -7,8,12,16]
    let cpu = reference(a, b, n: n, stride: stride)
    var padded = [Float](repeating: .nan, count: n * stride)
    for i in 0..<n { for j in 0..<n { padded[i * stride + j] = cpu[i * n + j] } }
    func check() -> Check { padded.withUnsafeBufferPointer { p in golden.withUnsafeBufferPointer {
        compare(p.baseAddress!, $0.baseAddress!, n: n, stride: stride)
    } } }
    try require(check().passed && check().compared_elements == 16, "CPU SGEMM/golden/padded comparator failed")
    let knownHash = "3528d12e2f4ce4f09b261bebe1f87a9bf13961f72a9f8fb5e8b10517db08d24a"
    try require(padded.withUnsafeBufferPointer { canonicalHash($0.baseAddress!, n: n, stride: stride) } == knownHash,
                "Canonical padded Float32-LE SHA256 failed")
    try require(golden.withUnsafeBufferPointer { canonicalHash($0.baseAddress!, n: n, stride: n) } == knownHash,
                "Canonical golden Float32-LE SHA256 failed")
    padded[0] = 0
    let zeroHash = padded.withUnsafeBufferPointer { canonicalHash($0.baseAddress!, n: n, stride: stride) }
    padded[0] = -0.0
    try require(padded[0].bitPattern == 0x80000000 &&
                padded.withUnsafeBufferPointer { canonicalHash($0.baseAddress!, n: n, stride: stride) } == zeroHash,
                "Signed-zero hash normalization failed")
    padded[0] = golden[0]
    padded[3 * stride + 3] += 1
    try require(!check().passed && check().mismatch_count == 1 && check().max_abs_error == 1, "Corruption accepted")
    padded[0] = .nan
    try require(!check().passed && check().mismatch_count == 2 && check().nonfinite_count == 1 && check().max_abs_error == nil,
                "NaN or later corruption accepted")
    padded[1] = .infinity
    try require(check().mismatch_count == 3 && check().nonfinite_count == 2 && check().compared_elements == 16, "Infinity or early exit accepted")
}
struct Trial: Codable {
    var n: Int, index: Int, kind: String
    var row_bytes = 0, buffer_payload_bytes = 0, buffer_length_bytes = 0, buffer_allocated_bytes = 0
    var cpu_reference_payload_bytes = 0, cpu_hash_scratch_bytes = 0
    var gpu_output_sha256: String?, cpu_reference_sha256: String?
    var device_allocated_before_buffers_sample: Int?, device_allocated_with_buffers_sample: Int?
    var submit_to_complete_seconds: Double?, gpu_start_time: Double?, gpu_end_time: Double?, gpu_interval_seconds: Double?
    var command_buffer_status: String?, command_buffer_error: String?, check: Check?, failure: String?
    var passed = false
}
func runTrial(device: MTLDevice, queue: MTLCommandQueue, n: Int, index: Int, kind: String) -> Trial {
    var row = Trial(n: n, index: index, kind: kind)
    do {
        let rowBytes = MPSMatrixDescriptor.rowBytes(fromColumns: n, dataType: .float32)
        try require(rowBytes >= n * 4 && rowBytes % 4 == 0, "Invalid recommended row stride")
        let stride = rowBytes / 4, bytes = n * rowBytes
        row.row_bytes = rowBytes; row.buffer_payload_bytes = 3 * n * n * 4
        row.cpu_reference_payload_bytes = n * n * 4; row.cpu_hash_scratch_bytes = n * 4
        try require(3 * bytes + row.cpu_reference_payload_bytes + row.cpu_hash_scratch_bytes <= byteCap && bytes <= device.maxBufferLength, "Explicit buffer budget exceeded")
        row.device_allocated_before_buffers_sample = device.currentAllocatedSize
        guard let a = device.makeBuffer(length: bytes, options: .storageModeShared),
              let b = device.makeBuffer(length: bytes, options: .storageModeShared),
              let c = device.makeBuffer(length: bytes, options: .storageModeShared) else { throw Failure("Shared buffer allocation failed") }
        row.buffer_length_bytes = a.length + b.length + c.length
        row.buffer_allocated_bytes = a.allocatedSize + b.allocatedSize + c.allocatedSize
        row.device_allocated_with_buffers_sample = device.currentAllocatedSize
        try require(row.buffer_allocated_bytes + row.cpu_reference_payload_bytes + row.cpu_hash_scratch_bytes <= byteCap, "Allocated buffer budget exceeded")
        let ap = a.contents().bindMemory(to: Float.self, capacity: n * stride)
        let bp = b.contents().bindMemory(to: Float.self, capacity: n * stride)
        let cp = c.contents().bindMemory(to: Float.self, capacity: n * stride)
        fill(ap, bp, n: n, stride: stride); cp.initialize(repeating: .nan, count: n * stride)
        // MPSMatrix stores rows with the explicit stride; neither operand is transposed.
        let descriptor = MPSMatrixDescriptor(rows: n, columns: n, rowBytes: rowBytes, dataType: .float32)
        let am = MPSMatrix(buffer: a, descriptor: descriptor), bm = MPSMatrix(buffer: b, descriptor: descriptor)
        let cm = MPSMatrix(buffer: c, descriptor: descriptor)
        let multiply = MPSMatrixMultiplication(device: device, transposeLeft: false, transposeRight: false,
                                               resultRows: n, resultColumns: n, interiorColumns: n, alpha: 1, beta: 0)
        guard let command = queue.makeCommandBuffer() else { throw Failure("Command buffer creation failed") }
        multiply.encode(commandBuffer: command, leftMatrix: am, rightMatrix: bm, resultMatrix: cm)
        let start = DispatchTime.now().uptimeNanoseconds
        command.commit(); command.waitUntilCompleted()
        let end = DispatchTime.now().uptimeNanoseconds
        row.submit_to_complete_seconds = Double(end - start) / 1e9
        row.command_buffer_status = String(describing: command.status)
        row.command_buffer_error = command.error?.localizedDescription
        let gs = command.gpuStartTime, ge = command.gpuEndTime
        if gs.isFinite && ge.isFinite && gs > 0 && ge > gs {
            row.gpu_start_time = gs; row.gpu_end_time = ge; row.gpu_interval_seconds = ge - gs
        }
        try require(command.status == .completed && command.error == nil, "Command buffer did not complete successfully")
        // CPU reference is outside the measured GPU submission/completion interval.
        let expected = reference(ap, bp, n: n, stride: stride)
        row.check = expected.withUnsafeBufferPointer { compare(cp, $0.baseAddress!, n: n, stride: stride) }
        row.gpu_output_sha256 = canonicalHash(cp, n: n, stride: stride)
        row.cpu_reference_sha256 = expected.withUnsafeBufferPointer { canonicalHash($0.baseAddress!, n: n, stride: n) }
        try require(row.check!.passed && row.check!.compared_elements == n * n, "Exact full-matrix comparison failed")
        row.passed = true
    } catch { row.failure = String(describing: error) }
    return row
}
struct Report: Codable {
    var schema_version = 1, protocol_id = "mac-mps-f32-correctness-v1"
    var started_at = ISO8601DateFormatter().string(from: Date()), completed_at: String?
    var size_order = order, dtype = "Float32", matrix_layout = "row-major", storage_mode = "shared"
    var device_name: String?, has_unified_memory: Bool?, max_buffer_length: Int?, recommended_max_working_set_size: UInt64?
    var explicit_buffer_and_reference_cap_bytes = byteCap
    var output_hash_encoding = "SHA256 of row-major Float32 bitPattern encoded little-endian; padding excluded; both signed zeros normalized to positive zero; all other bitPatterns preserved. Hashes computed after timed interval."
    var exactness_bound = "Each product and partial sum is an integer with absolute bound 15*N < 2^24."
    var interpretation = "Diagnostic timing only. Metal allocation counters are samples, not peaks or allocatable capacity. Recommended working set is advisory, not free RAM. CPU reference reuses Metal A/B and allocates separate C; framework internals are not counted."
    var warmup: Trial?, trials: [Trial] = [], failure: String?, cpu_self_test_passed = false, gate_passed = false
}
// Same-directory temp + exclusive hard link publishes complete JSON atomically without replacing any path.
func publish(_ report: Report, to path: String) throws {
    let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let data = try encoder.encode(report)
    let parent = URL(fileURLWithPath: path).deletingLastPathComponent().path
    let temporary = parent + "/.mps-calibration-" + UUID().uuidString + ".tmp"
    let fd = open(temporary, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, S_IRUSR | S_IWUSR)
    try require(fd >= 0, "Cannot exclusively create output temporary: \(String(cString: strerror(errno)))")
    defer { close(fd); unlink(temporary) }
    try data.withUnsafeBytes { bytes in
        var offset = 0
        while offset < bytes.count {
            let wrote = write(fd, bytes.baseAddress!.advanced(by: offset), bytes.count - offset)
            if wrote < 0 && errno == EINTR { continue }
            try require(wrote > 0, "Output write failed")
            offset += wrote
        }
    }
    try require(fsync(fd) == 0, "Output fsync failed")
    try require(link(temporary, path) == 0, "Output publication refused: \(String(cString: strerror(errno)))")
}
func main() -> Int32 {
    let args = Array(CommandLine.arguments.dropFirst())
    do {
        if args == ["--self-test"] { try selfTest(); print("CPU_ONLY_SELF_TEST_PASS golden/padding/corruption/NaN/infinity/full_scan/SHA256"); return 0 }
        try require(args.count == 2 && args[0] == "--output" && args[1].hasPrefix("/"), "Usage: calibrate --self-test | --output /absolute/NEW_PATH.json")
        var st = stat()
        try require(lstat(args[1], &st) != 0 && errno == ENOENT, "Output path already exists or cannot be checked")
        var report = Report()
        do {
            try selfTest(); report.cpu_self_test_passed = true
            guard let device = MTLCreateSystemDefaultDevice() else { throw Failure("No default Metal device") }
            report.device_name = device.name; report.has_unified_memory = device.hasUnifiedMemory
            report.max_buffer_length = device.maxBufferLength; report.recommended_max_working_set_size = device.recommendedMaxWorkingSetSize
            try require(device.hasUnifiedMemory, "Default device does not report unified memory")
            guard let queue = device.makeCommandQueue() else { throw Failure("Cannot create command queue") }
            report.warmup = autoreleasepool { runTrial(device: device, queue: queue, n: 64, index: 0, kind: "warmup") }
            try require(report.warmup!.passed, "Warmup failed: \(report.warmup!.failure ?? "unknown")")
            for (index, n) in order.enumerated() {
                let row = autoreleasepool { runTrial(device: device, queue: queue, n: n, index: index + 1, kind: "measured") }
                report.trials.append(row)
                try require(row.passed, "Trial \(index + 1) failed: \(row.failure ?? "unknown")")
            }
            report.gate_passed = report.trials.count == 9 && report.trials.allSatisfy(\.passed) && report.warmup!.passed
        } catch { report.failure = String(describing: error) }
        report.completed_at = ISO8601DateFormatter().string(from: Date())
        try publish(report, to: args[1]); print(report.gate_passed ? "CALIBRATION_PASS" : "CALIBRATION_FAIL")
        return report.gate_passed ? 0 : 1
    } catch { fputs("calibrate: \(error)\n", stderr); return 2 }
}
exit(main())
