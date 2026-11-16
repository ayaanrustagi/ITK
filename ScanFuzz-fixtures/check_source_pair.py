"""Verify the bundled SEG against the referenced CT and expected pixels."""

from pathlib import Path

import highdicom
import numpy as np
import pydicom

EXPECTED_FOREGROUND = ((0, 0), (0, 7), (0, 8), (1, 15), (8, 7), (15, 15))


def main():
    directory = Path(__file__).resolve().parent
    source = pydicom.dcmread(directory / "synthetic-ct.dcm", stop_before_pixels=True)
    segmentation = highdicom.seg.segread(directory / "synthetic-binary-seg.dcm")
    mask = segmentation.get_pixels_by_source_instance(
        [source.SOPInstanceUID], segment_numbers=[1]
    )
    expected = np.zeros((1, 16, 16, 1), dtype=np.uint8)
    for row, column in EXPECTED_FOREGROUND:
        expected[0, row, column, 0] = 1
    np.testing.assert_array_equal(mask, expected)
    print(f"PASS (highdicom {highdicom.__version__}): source CT UID and all 256 pixels match.")


if __name__ == "__main__":
    main()
