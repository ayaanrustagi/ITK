"""Compare ITK reader paths on the bundled synthetic CT and binary SEG."""

import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
import pydicom


def read(executable, mode, path, expected):
    result = subprocess.run(
        [str(executable.resolve()), mode, str(path)], capture_output=True, text=True
    )
    if result.returncode != 0:
        return dict(reader=mode, file=path.name, exit=result.returncode,
                    diagnostic=result.stderr.strip())
    dimensions, pixels = result.stdout.splitlines()
    shape = tuple(map(int, dimensions.split()))
    array = np.fromstring(pixels, dtype=np.uint8, sep=" ").reshape(shape)
    if expected.ndim == 2:
        expected = expected[np.newaxis, :, :]
    return dict(reader=mode, file=path.name, shape=shape,
                values=np.unique(array).tolist(),
                foreground_positions_match=bool(np.array_equal(array != 0, expected != 0)),
                values_match=bool(np.array_equal(array, expected)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    parser.add_argument("fixtures", type=Path)
    args = parser.parse_args()
    for name in ("synthetic-ct.dcm", "synthetic-binary-seg.dcm"):
        path = args.fixtures / name
        expected = pydicom.dcmread(path).pixel_array
        for reader in ("gdcm", "gdcm-unit", "dcmtk"):
            print(json.dumps(read(args.executable, reader, path, expected)))


if __name__ == "__main__":
    main()
