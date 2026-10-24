// Arithmetic/parser/oracle/self-test copied unchanged from qualified 2026-10-14 source.
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
