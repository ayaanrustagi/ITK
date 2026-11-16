# Compare ITK DICOM readers on the ScanFuzz fixture

This local comparison uses the synthetic CT and SEG files one directory up. It reports the decoded values and tests whether nonzero positions and exact values match pydicom independently.

The recorded result used ITK PR commit `fb01f4114829ff68f2b88ed3900ea9a16d13e4bf`, which includes the GDCM opt-in API, and its pinned DCMTK dependency `554b74475`. Set `ITK_SRC` to a checkout of that ITK commit. With CMake, Ninja, a C++ compiler, and Python available, run from this directory.

```sh
cmake -G Ninja -S "$ITK_SRC" -B itk-build -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=OFF -DITK_BUILD_DEFAULT_MODULES=OFF \
  -DModule_ITKIODCMTK=ON -DModule_ITKIOGDCM=ON
cmake --build itk-build --target ITKIODCMTK ITKIOGDCM
cmake -S . -B probe-build -DITK_DIR="$PWD/itk-build"
cmake --build probe-build
python -m pip install pydicom==3.0.2 numpy
python compare.py probe-build/compare-reader ..
```

The probe reports every reader outcome, including errors. Compare its six JSON lines with `results.jsonl`. The CT control should agree in all modes. For the SEG, all reader modes should agree on the six foreground positions. Exact values should match pydicom through ITK's DCMTK reader and opt-in GDCM reader.
