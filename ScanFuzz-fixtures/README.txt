ScanFuzz synthetic DICOM segmentation check

This package contains a synthetic 16 × 16 CT image and its binary segmentation. Both files use fictional metadata and generated pixel data. They passed dciodvfy (dicom3tools 20260927).

Local evaluation

1. Import synthetic-ct.dcm and its referenced synthetic-binary-seg.dcm into the same local test environment. If the application supports DICOM SEG overlays, check that the mask aligns with the source image.
2. If your tool exposes the decoded mask as numbers, compare the foreground values to the list below. The total foreground count should be six, and the SEG stores a value of 1 at each foreground position.
3. Record your tool and version, whether it imported the overlay, and any decoded foreground value you can inspect. If the test would be useful to your project, tell us where it could fit in your test suite.

Expected foreground positions

Coordinates are zero-based (row, column). The positions are (0, 0), (0, 7), (0, 8), (1, 15), (8, 7), and (15, 15). All other pixels are background. A viewer can display the same outline even when its reader converts 1 to 255. The numeric check is useful for software that selects a particular label.

Reference result

pydicom 3.0.2 decoded all six foreground values as 1. ITK 5.4.7 returned 255 at the same six positions. The corresponding public report is ITK issue #6641 at https://github.com/InsightSoftwareConsortium/ITK/issues/6641.

Optional automated source-pair check

In a Python environment, install highdicom 0.28.1 with
python -m pip install highdicom==0.28.1
Then run python check_source_pair.py from the unpacked directory.
The script looks up segment 1 by the source CT's instance UID and
compares all 256 mask pixels against the expected array.
