"""Build the distinct public OpenAI ZIP deterministically; --check verifies retained bytes."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
MEMBERS = ("plugin.json", "mcp.json", "LICENSE", "assets/icon.png")


def build():
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in MEMBERS:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (ROOT / "package" / name).read_bytes(), compresslevel=9)
    return output.getvalue()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = build()
    target = ROOT / "hunterkiller-public.zip"
    if args.check:
        assert target.read_bytes() == expected, "ZIP differs from deterministic source build"
        receipt = json.loads((ROOT / "receipt.json").read_text())
        assert receipt["sha256"] == hashlib.sha256(expected).hexdigest()
        assert receipt["bytes"] == len(expected)
        with zipfile.ZipFile(io.BytesIO(expected)) as archive:
            assert archive.testzip() is None
            assert archive.namelist() == list(MEMBERS)
            for name in MEMBERS:
                assert receipt["member_sha256"][name] == hashlib.sha256(archive.read(name)).hexdigest()
        print("Deterministic ZIP, CRC, members and receipt hashes passed.")
    else:
        target.write_bytes(expected)
        print(f"{len(expected)} bytes; SHA256 {hashlib.sha256(expected).hexdigest()}")
