"""Compare all three ITK reader modes on each generated SEG case."""

import argparse
import json
from pathlib import Path

from pydicom import dcmread

from compare import read


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    parser.add_argument("fixtures", type=Path)
    args = parser.parse_args()
    results = {}
    for seg in sorted(args.fixtures.glob("*/seg.dcm")):
        expected = dcmread(seg).pixel_array
        results[seg.parent.name] = [
            read(args.executable, mode, seg, expected)
            for mode in ("gdcm", "gdcm-unit", "dcmtk")
        ]
    if not results:
        parser.error("No generated */seg.dcm cases found")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
