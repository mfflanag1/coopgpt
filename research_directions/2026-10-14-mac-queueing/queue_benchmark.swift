import Foundation
import Metal
import MetalPerformanceShaders
import Accelerate
import CryptoKit
import Darwin

let sizes = [256, 512, 1024]
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
func correctnessSelfTest() throws {
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
struct Clock {
    let epoch: UInt64
    func now() -> Double {
        let t = DispatchTime.now().uptimeNanoseconds
        return t >= epoch ? Double(t - epoch) / 1e9 : -Double(epoch - t) / 1e9
    }
    func wait(until offset: Double) {
        let target = epoch + UInt64((offset * 1e9).rounded(.up))
        while true {
            let t = DispatchTime.now().uptimeNanoseconds
            if t >= target { return }
            Thread.sleep(forTimeInterval: Double(target - t) / 1e9)
        }
    }
}
struct Job: Codable {
    var id: Int, n: Int, kind: String, planned_offer_s: Double, deadline_s: Double
    var status = "not_offered", admission_sequence: Int?
    var observed_enqueue_s: Double?, admission_s: Double?, encode_done_s: Double?, submit_s: Double?
    var gpu_completion_observed_s: Double?, validated_completion_s: Double?, resource_release_s: Double?, failed_at_s: Double?
    var row_bytes = 0, buffer_payload_bytes = 0, buffer_length_bytes = 0, buffer_allocated_bytes = 0
    var cpu_reference_payload_bytes = 0, cpu_hash_scratch_bytes = 0
    var device_allocated_before_buffers_sample: Int?, device_allocated_with_buffers_sample: Int?, device_allocated_after_release_sample: Int?
    var gpu_start_time: Double?, gpu_end_time: Double?, gpu_interval_seconds: Double?
    var command_buffer_status: Int?, command_buffer_error: String?, check: Check?, failure: String?
    var gpu_output_sha256: String?, cpu_reference_sha256: String?, passed = false
}
func makeJobs(rate: Int) -> [Job] {
    (0..<60).map { Job(id: $0, n: sizes[$0 % 3], kind: "measured", planned_offer_s: Double($0) / Double(rate),
                      deadline_s: Double($0) / Double(rate) + 0.100) }
}
func runJob(_ initial: Job, device: MTLDevice, queue: MTLCommandQueue, clock: Clock) -> Job {
    var row = initial
    do {
        let n = row.n, rb = MPSMatrixDescriptor.rowBytes(fromColumns: row.n, dataType: .float32)
        try require(rb >= n * 4 && rb % 4 == 0, "Invalid row stride")
        let stride = rb / 4, bytes = n * rb
        row.row_bytes = rb; row.buffer_payload_bytes = 3 * n * n * 4
        row.cpu_reference_payload_bytes = n * n * 4; row.cpu_hash_scratch_bytes = n * 4
        let cpuBytes = row.cpu_reference_payload_bytes + row.cpu_hash_scratch_bytes
        try require(3 * bytes + cpuBytes <= byteCap && bytes <= device.maxBufferLength, "Explicit byte cap exceeded")
        row.device_allocated_before_buffers_sample = device.currentAllocatedSize
        guard let a = device.makeBuffer(length: bytes, options: .storageModeShared),
              let b = device.makeBuffer(length: bytes, options: .storageModeShared),
              let c = device.makeBuffer(length: bytes, options: .storageModeShared) else { throw Failure("Shared allocation failed") }
        row.buffer_length_bytes = a.length + b.length + c.length
        row.buffer_allocated_bytes = a.allocatedSize + b.allocatedSize + c.allocatedSize
        row.device_allocated_with_buffers_sample = device.currentAllocatedSize
        try require(row.buffer_allocated_bytes + cpuBytes <= byteCap, "Allocated byte cap exceeded")
        let ap = a.contents().bindMemory(to: Float.self, capacity: n * stride)
        let bp = b.contents().bindMemory(to: Float.self, capacity: n * stride)
        let cp = c.contents().bindMemory(to: Float.self, capacity: n * stride)
        fill(ap, bp, n: n, stride: stride); cp.initialize(repeating: .nan, count: n * stride)
        let descriptor = MPSMatrixDescriptor(rows: n, columns: n, rowBytes: rb, dataType: .float32)
        let am = MPSMatrix(buffer: a, descriptor: descriptor), bm = MPSMatrix(buffer: b, descriptor: descriptor)
        let cm = MPSMatrix(buffer: c, descriptor: descriptor)
        let multiply = MPSMatrixMultiplication(device: device, transposeLeft: false, transposeRight: false,
                                               resultRows: n, resultColumns: n, interiorColumns: n, alpha: 1, beta: 0)
        guard let command = queue.makeCommandBuffer() else { throw Failure("Command creation failed") }
        multiply.encode(commandBuffer: command, leftMatrix: am, rightMatrix: bm, resultMatrix: cm)
        row.encode_done_s = clock.now(); row.submit_s = clock.now()
        command.commit(); command.waitUntilCompleted(); row.gpu_completion_observed_s = clock.now()
        row.command_buffer_status = Int(command.status.rawValue); row.command_buffer_error = command.error?.localizedDescription
        let gs = command.gpuStartTime, ge = command.gpuEndTime
        if gs.isFinite && ge.isFinite && gs > 0 && ge > gs {
            row.gpu_start_time = gs; row.gpu_end_time = ge; row.gpu_interval_seconds = ge - gs
        }
        try require(command.status == .completed && command.error == nil, "Command completion failed")
        let expected = reference(ap, bp, n: n, stride: stride)
        row.check = expected.withUnsafeBufferPointer { compare(cp, $0.baseAddress!, n: n, stride: stride) }
        row.gpu_output_sha256 = canonicalHash(cp, n: n, stride: stride)
        row.cpu_reference_sha256 = expected.withUnsafeBufferPointer { canonicalHash($0.baseAddress!, n: n, stride: n) }
        row.validated_completion_s = clock.now()
        try require(row.check!.passed && row.check!.compared_elements == n * n, "Exact comparison failed")
        row.passed = true; row.status = "passed"
    } catch { row.status = "failed"; row.failure = String(describing: error); row.failed_at_s = clock.now() }
    return row
}
struct Event: Codable { let sequence: Int, job_id: Int, kind: String, time_s: Double, active_count: Int, queue_count: Int }
// All queue, row-store, and active-count access is locked; worker-owned Job copies contain no Metal objects.
final class FIFO {
    let condition = NSCondition(), capacity: Int, clock: Clock
    private(set) var jobs: [Job], events: [Event] = [], max_active_observed = 0
    private var pending: [Int] = [], closed = false, active = 0, admitted = 0
    init(jobs: [Job], capacity: Int, clock: Clock) { self.jobs = jobs; self.capacity = capacity; self.clock = clock }
    private func event(_ kind: String, _ id: Int, _ time: Double) {
        events.append(Event(sequence: events.count, job_id: id, kind: kind, time_s: time, active_count: active, queue_count: pending.count))
    }
    func enqueue(_ id: Int) {
        condition.lock(); defer { condition.unlock() }
        let t = clock.now(); jobs[id].observed_enqueue_s = t; jobs[id].status = "queued"
        pending.append(id); event("enqueue", id, t); condition.broadcast()
    }
    func close() { condition.lock(); closed = true; condition.broadcast(); condition.unlock() }
    func take() -> Job? {
        condition.lock(); defer { condition.unlock() }
        while pending.isEmpty && !closed { condition.wait() }
        if pending.isEmpty { return nil }
        precondition(active < capacity)
        let id = pending.removeFirst(), t = clock.now()
        active += 1; max_active_observed = max(max_active_observed, active)
        jobs[id].admission_s = t; jobs[id].admission_sequence = admitted; jobs[id].status = "active"; admitted += 1
        event("admit", id, t); return jobs[id]
    }
    func finish(_ result: Job) {
        condition.lock(); defer { condition.unlock() }
        let t = clock.now(); var row = result; row.resource_release_s = t; jobs[row.id] = row
        active -= 1; precondition(active >= 0); event("release", row.id, t); condition.broadcast()
    }
}
func execute(_ fifo: FIFO, offers: [Double], operation: @escaping (Job) -> Job,
             afterCleanup: @escaping (inout Job) -> Void = { _ in }, producerFinished: @escaping () -> Void = {}) {
    let workers = DispatchGroup(), producer = DispatchGroup()
    for _ in 0..<fifo.capacity {
        workers.enter()
        Thread.detachNewThread {
            defer { workers.leave() }
            while let job = fifo.take() {
                var result = autoreleasepool { operation(job) }
                afterCleanup(&result) // Pool has drained before accounting releases the active slot.
                fifo.finish(result)
            }
        }
    }
    producer.enter()
    Thread.detachNewThread {
        defer { producer.leave() }
        for (id, offer) in offers.enumerated() { fifo.clock.wait(until: offer); fifo.enqueue(id) }
        fifo.close(); producerFinished()
    }
    producer.wait(); workers.wait()
}
func queueSelfTest() throws {
    for cap in [1, 2] {
        let rows = makeJobs(rate: 100), clock = Clock(epoch: DispatchTime.now().uptimeNanoseconds + 20_000_000)
        let fifo = FIFO(jobs: rows, capacity: cap, clock: clock), allOffered = DispatchSemaphore(value: 0)
        execute(fifo, offers: rows.map(\.planned_offer_s), operation: { initial in
            var row = initial
            if row.id < cap && allOffered.wait(timeout: .now() + 3) != .success { row.failure = "Producer blocked by worker capacity" }
            if row.id == 17 { row.failure = "Intentional fake job failure" }
            row.validated_completion_s = clock.now(); Thread.sleep(forTimeInterval: 0.002)
            row.passed = row.failure == nil; row.status = row.passed ? "passed" : "failed"; return row
        }, producerFinished: { for _ in 0..<cap { allOffered.signal() } })
        try require(fifo.max_active_observed == cap && fifo.jobs.filter { !$0.passed }.map(\.id) == [17], "Fake queue cap/producer/failure test failed")
        try require(fifo.jobs.map(\.admission_sequence) == (0..<60).map { Optional($0) }, "FIFO admission order failed")
        try require(fifo.jobs[59].observed_enqueue_s! <= fifo.jobs[0].resource_release_s!, "Producer waited for capacity")
        var active = Set<Int>(), pending: [Int] = []
        for e in fifo.events {
            if e.kind == "enqueue" { pending.append(e.job_id) }
            if e.kind == "admit" { try require(pending.removeFirst() == e.job_id && active.insert(e.job_id).inserted, "FIFO event failed") }
            if e.kind == "release" { try require(active.remove(e.job_id) != nil, "Release without admission") }
            try require(active.count == e.active_count && active.count <= cap && pending.count == e.queue_count, "Active/event accounting failed")
        }
        try require(active.isEmpty && pending.isEmpty && fifo.events.count == 180, "Lost request/event")
        try require(fifo.jobs.allSatisfy { $0.resource_release_s! - $0.validated_completion_s! >= 0.001 }, "Slot released before fake cleanup")
    }
}
struct Options { let concurrency: Int, rate: Int, output: String }
func parse(_ args: [String]) throws -> Options {
    try require(args.count == 6, "Usage: queue_benchmark --concurrency 1|2 --rate 10|40|100 --output /absolute/NEW.json | --self-test")
    var flags: [String: String] = [:]
    for i in stride(from: 0, to: args.count, by: 2) {
        try require(["--concurrency", "--rate", "--output"].contains(args[i]) && flags[args[i]] == nil, "Unknown/duplicate flag")
        flags[args[i]] = args[i + 1]
    }
    guard let cap = Int(flags["--concurrency"] ?? ""), [1,2].contains(cap),
          let rate = Int(flags["--rate"] ?? ""), [10,40,100].contains(rate),
          let output = flags["--output"], output.hasPrefix("/") else { throw Failure("Invalid options") }
    return Options(concurrency: cap, rate: rate, output: output)
}
struct Report: Codable {
    var schema_version = 1, protocol_id = "mac-mps-queueing-v1"
    var concurrency: Int, rate: Int, jobs: [Job], warmups: [Job] = [], events: [Event] = []
    var max_active_observed = 0, per_job_explicit_byte_cap = byteCap, active_explicit_byte_cap: Int
    var started_at = ISO8601DateFormatter().string(from: Date()), completed_at: String?
    var epoch_uptime_ns: UInt64?, warmup_epoch_uptime_ns: UInt64?, window_end_s: Double?
    var device_name: String?, has_unified_memory: Bool?, max_buffer_length: Int?, recommended_max_working_set_size: UInt64?
    var cpu_self_test_passed = false, gate_passed = false, failure: String?
    var output_hash_encoding = "SHA256 row-major Float32 bitPattern little-endian, padding excluded, both signed zeros normalized positive; other bitPatterns preserved."
    var interpretation = "Concurrency caps whole job pipelines through CPU validation and autoreleasepool cleanup, not GPU kernel parallelism. Measured offsets use epoch_uptime_ns; warmup offsets use warmup_epoch_uptime_ns. Hardware GPU times are separate raw timestamps. Allocation counters are global samples, not per-job deltas or peaks. Working set is advisory, not free RAM. Explicit cap excludes framework internal allocations."
}
func publish(_ report: Report, to path: String) throws {
    let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let data = try encoder.encode(report), parent = URL(fileURLWithPath: path).deletingLastPathComponent().path
    let temporary = parent + "/.mps-queueing-" + UUID().uuidString + ".tmp"
    let fd = open(temporary, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, S_IRUSR | S_IWUSR)
    try require(fd >= 0, "Cannot exclusively create temporary output")
    defer { close(fd); unlink(temporary) }
    try data.withUnsafeBytes { bytes in
        var offset = 0
        while offset < bytes.count {
            let wrote = write(fd, bytes.baseAddress!.advanced(by: offset), bytes.count - offset)
            if wrote < 0 && errno == EINTR { continue }
            try require(wrote > 0, "Output write failed"); offset += wrote
        }
    }
    try require(fsync(fd) == 0, "Output fsync failed")
    try require(link(temporary, path) == 0, "Output publication refused: \(String(cString: strerror(errno)))")
}
func main() -> Int32 {
    do {
        let args = Array(CommandLine.arguments.dropFirst())
        if args == ["--self-test"] {
            try correctnessSelfTest(); try queueSelfTest()
            print("CPU_ONLY_SELF_TEST_PASS golden/checker/hash/FIFO/cap1/cap2/independent_producer/cleanup/failed_row_retained"); return 0
        }
        let options = try parse(args); var st = stat()
        try require(lstat(options.output, &st) != 0 && errno == ENOENT, "Output exists or cannot be checked")
        var report = Report(concurrency: options.concurrency, rate: options.rate, jobs: makeJobs(rate: options.rate),
                            active_explicit_byte_cap: byteCap * options.concurrency)
        do {
            try correctnessSelfTest(); report.cpu_self_test_passed = true
            guard let device = MTLCreateSystemDefaultDevice() else { throw Failure("No Metal device") }
            report.device_name = device.name; report.has_unified_memory = device.hasUnifiedMemory
            report.max_buffer_length = device.maxBufferLength; report.recommended_max_working_set_size = device.recommendedMaxWorkingSetSize
            try require(device.hasUnifiedMemory, "Device does not report unified memory")
            guard let queue = device.makeCommandQueue() else { throw Failure("Command queue creation failed") }
            let warmClock = Clock(epoch: DispatchTime.now().uptimeNanoseconds); report.warmup_epoch_uptime_ns = warmClock.epoch
            for (id, n) in sizes.enumerated() {
                let initial = Job(id: id, n: n, kind: "warmup", planned_offer_s: 0, deadline_s: 0)
                var row = autoreleasepool { runJob(initial, device: device, queue: queue, clock: warmClock) }
                row.resource_release_s = warmClock.now(); row.device_allocated_after_release_sample = device.currentAllocatedSize
                report.warmups.append(row); try require(row.passed, "Warmup failed: \(row.failure ?? "unknown")")
            }
            let clock = Clock(epoch: DispatchTime.now().uptimeNanoseconds + 50_000_000); report.epoch_uptime_ns = clock.epoch
            let fifo = FIFO(jobs: report.jobs, capacity: options.concurrency, clock: clock)
            execute(fifo, offers: report.jobs.map(\.planned_offer_s),
                    operation: { runJob($0, device: device, queue: queue, clock: clock) },
                    afterCleanup: { $0.device_allocated_after_release_sample = device.currentAllocatedSize })
            report.jobs = fifo.jobs; report.events = fifo.events; report.max_active_observed = fifo.max_active_observed
            report.window_end_s = clock.now()
            try require(report.jobs.count == 60 && report.jobs.allSatisfy(\.passed), "One or more jobs failed")
            report.gate_passed = true
        } catch { report.failure = String(describing: error) }
        report.completed_at = ISO8601DateFormatter().string(from: Date()); try publish(report, to: options.output)
        print(report.gate_passed ? "QUEUE_WINDOW_PASS" : "QUEUE_WINDOW_FAIL"); return report.gate_passed ? 0 : 1
    } catch { fputs("queue_benchmark: \(error)\n", stderr); return 2 }
}
exit(main())
