#!/usr/bin/env python3
"""Build deterministic, hash-checked review packets from an explicit manifest."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_records(value):
    if isinstance(value, dict):
        if "path" in value and "sha256" in value:
            yield value
        for child in value.values():
            yield from file_records(child)
    elif isinstance(value, list):
        for child in value:
            yield from file_records(child)


def main():
    base = Path(__file__).resolve().parents[1]
    manifest_path = base / "handoff/MINIMAL_REVIEW_PACKETS.json"
    manifest = json.loads(manifest_path.read_text())
    snapshots = {}
    for row in file_records(manifest):
        previous = snapshots.setdefault(row["path"], row["sha256"])
        if previous != row["sha256"]:
            raise ValueError("Conflicting hashes: " + row["path"])
    archives = []
    metadata = manifest["archive_policy"]["metadata_paths"]
    for packet in manifest["archive_sets"]:
        paths = sorted(set(packet["proof_and_evidence_paths"] + metadata))
        content = {}
        members = []
        for relative in paths:
            part = PurePosixPath(relative)
            if part.is_absolute() or ".." in part.parts:
                raise ValueError("Unsafe archive path: " + relative)
            path = base / relative
            if path.is_symlink() or not path.is_file():
                raise ValueError("Missing or symlink member: " + relative)
            data = path.read_bytes()
            sha = digest(data)
            if relative not in metadata and snapshots.get(relative) != sha:
                raise ValueError("Missing or stale accepted hash: " + relative)
            content[relative] = data
            members.append({"path": relative, "bytes": len(data), "sha256": sha})
        internal = {
            "packet_id": packet["id"], "claim_scope": packet["claim_scope"],
            "status": "Internally reviewed research; novelty and external review pending",
            "members": members,
        }
        content["ARCHIVE_MANIFEST.json"] = (
            json.dumps(internal, indent=2, sort_keys=True) + "\n"
        ).encode()
        content["START_HERE.txt"] = (
            "CoopGPT review packet " + packet["id"] + "\n\n"
            + packet["claim_scope"] + "\n\n"
            "Begin with handoff/REVIEW_READING_ORDER.txt and the matching packet\n"
            "in handoff/MINIMAL_REVIEW_PACKETS.json. This archive includes only\n"
            "the selected claim's explicit proof/checker dependencies. Other\n"
            "modules named in the shared reading guide are separate packets.\n\n"
            "Internal acceptance is not external specialist review, formal proof\n"
            "verification, publication acceptance or novelty confirmation.\n"
            "Checker passes supplement the analytic proofs. If running a checker,\n"
            "extract to a disposable directory and use python3 -I, never -O.\n"
            "Checkers can regenerate JSON beside their source. No network or\n"
            "third-party Python packages are required for these packet checks.\n\n"
            "ARCHIVE_MANIFEST.json records every supplied source file's SHA-256.\n"
            "No third-party original papers or raw telemetry are bundled.\n"
        ).encode()
        name = packet["archive_name"]
        if Path(name).name != name or not name.endswith(".zip"):
            raise ValueError("Unsafe archive name")
        destination = base / "handoff" / name
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9) as archive:
            for relative, data in sorted(content.items()):
                info = zipfile.ZipInfo(relative, (2026, 10, 17, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data, compresslevel=9)
        with zipfile.ZipFile(destination) as archive:
            if archive.testzip() is not None:
                raise AssertionError("Corrupt archive")
            if sorted(archive.namelist()) != sorted(content):
                raise AssertionError("Archive membership mismatch")
            for name, original in content.items():
                if archive.read(name) != original:
                    raise AssertionError("Archive content mismatch: " + name)
        data = destination.read_bytes()
        archives.append({"id": packet["id"], "path": "handoff/" + destination.name,
                         "claim_scope": packet["claim_scope"],
                         "files": len(content), "bytes": len(data),
                         "sha256": digest(data)})
    report = {"status": "PASS", "deterministic": True,
              "crc_and_all_member_bytes_verified": True, "archives": archives}
    (base / "handoff/REVIEW_ARCHIVES.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
