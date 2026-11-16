"""Generate a synthetic CT and DICOM SEG with six known foreground pixels."""

import argparse
from pathlib import Path

import highdicom as hd
import numpy as np
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.sr.coding import Code
from pydicom.uid import CTImageStorage, ExplicitVRLittleEndian, generate_uid


SHAPE = (16, 16)
FOREGROUND = ((0, 0), (0, 7), (0, 8), (1, 15), (8, 7), (15, 15))


def make_source_image(path):
    sop_uid = generate_uid()
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = CTImageStorage
    file_meta.MediaStorageSOPInstanceUID = sop_uid
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    source = FileDataset(path, {}, file_meta=file_meta, preamble=bytes(128))
    source.SOPClassUID = CTImageStorage
    source.SOPInstanceUID = sop_uid
    source.StudyInstanceUID = generate_uid()
    source.SeriesInstanceUID = generate_uid()
    source.FrameOfReferenceUID = generate_uid()
    source.Modality = "CT"
    source.ImageType = ["ORIGINAL", "PRIMARY", "AXIAL"]
    source.BodyPartExamined = "KNEE"
    source.Laterality = "L"
    source.PatientName = "Synthetic^ScanFuzz"
    source.PatientID = "SYNTHETIC"
    source.PatientBirthDate = ""
    source.PatientSex = ""
    source.StudyID = "1"
    source.StudyDate = "20000101"
    source.StudyTime = "000000"
    source.AccessionNumber = ""
    source.ReferringPhysicianName = ""
    source.Manufacturer = "ScanFuzz synthetic fixture"
    source.SeriesNumber = 1
    source.AcquisitionNumber = 1
    source.InstanceNumber = 1
    source.PositionReferenceIndicator = ""
    source.PatientPosition = "HFS"
    source.ImagePositionPatient = [0, 0, 0]
    source.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
    source.PixelSpacing = [1, 1]
    source.SliceThickness = 1
    source.KVP = ""
    source.RescaleIntercept = 0
    source.RescaleSlope = 1
    source.RescaleType = "HU"
    source.set_pixel_data(
        np.zeros(SHAPE, dtype="<u2"),
        "MONOCHROME2",
        bits_stored=16,
        generate_instance_uid=False,
    )
    source.save_as(path, enforce_file_format=True)
    return source


def write_fixtures(output_dir, mask):
    output_dir.mkdir(parents=True, exist_ok=True)
    source_path = output_dir / "synthetic-ct.dcm"
    seg_path = output_dir / "synthetic-binary-seg.dcm"
    source = make_source_image(source_path)
    segment = hd.seg.SegmentDescription(
        segment_number=1,
        segment_label="Synthetic mask",
        segmented_property_category=Code("49755003", "SCT", "Morphologically Abnormal Structure"),
        segmented_property_type=Code("108369006", "SCT", "Neoplasm"),
        algorithm_type="MANUAL",
    )
    segmentation = hd.seg.Segmentation(
        source_images=[source],
        pixel_array=mask,
        segmentation_type="BINARY",
        segment_descriptions=[segment],
        series_instance_uid=generate_uid(),
        series_number=2,
        sop_instance_uid=generate_uid(),
        instance_number=1,
        manufacturer="ScanFuzz",
        manufacturer_model_name="Synthetic fixture",
        software_versions="1",
        device_serial_number="SYNTHETIC",
        content_description="Synthetic regression fixture",
        content_label="SYNTHETIC",
    )
    segmentation.save_as(seg_path, enforce_file_format=True)
    return source_path, seg_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    mask = np.zeros(SHAPE, dtype=np.uint8)
    for row, column in FOREGROUND:
        mask[row, column] = 1
    for path in write_fixtures(args.output_dir, mask):
        print(path)


if __name__ == "__main__":
    main()
