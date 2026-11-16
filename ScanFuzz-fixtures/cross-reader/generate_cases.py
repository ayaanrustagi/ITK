"""Generate five synthetic DICOM segmentation scenarios with their source CTs."""

import argparse
from copy import deepcopy
from pathlib import Path
import sys

import highdicom as hd
import numpy as np
from pydicom.sr.coding import Code
from pydicom.uid import generate_uid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generate_source_pair import make_source_image


def generate_case(root, name, rows, columns, slices, segments, fractional=False):
    output_dir = root / name
    output_dir.mkdir(parents=True, exist_ok=True)
    prototype_path = output_dir / "prototype.dcm"
    prototype = make_source_image(prototype_path)
    prototype_path.unlink()
    images = []
    mask = np.zeros((slices, rows, columns, segments), dtype=np.uint8)
    for index in range(slices):
        image = deepcopy(prototype)
        image.SOPInstanceUID = generate_uid()
        image.file_meta.MediaStorageSOPInstanceUID = image.SOPInstanceUID
        image.InstanceNumber = index + 1
        image.ImagePositionPatient = [0, 0, index]
        image.set_pixel_data(np.zeros((rows, columns), dtype="<u2"), "MONOCHROME2", 16,
                             generate_instance_uid=False)
        image.save_as(output_dir / f"ct-{index + 1}.dcm", enforce_file_format=True)
        images.append(image)
        for seg_index in range(segments):
            mask[index, 0, 0, seg_index] = 1
            mask[index, (1 + index + seg_index) % rows, columns - 1, seg_index] = 1
            mask[index, -1, -1, seg_index] = 1
    pixel_array = mask.astype(np.float32) * 0.5 if fractional else mask
    descriptions = [hd.seg.SegmentDescription(
        segment_number=index + 1, segment_label=f"Synthetic mask {index + 1}",
        segmented_property_category=Code("49755003", "SCT", "Morphologically Abnormal Structure"),
        segmented_property_type=Code("108369006", "SCT", "Neoplasm"),
        algorithm_type="MANUAL",
    ) for index in range(segments)]
    segmentation = hd.seg.Segmentation(
        source_images=images, pixel_array=pixel_array,
        segmentation_type="FRACTIONAL" if fractional else "BINARY",
        segment_descriptions=descriptions, series_instance_uid=generate_uid(),
        series_number=2, sop_instance_uid=generate_uid(), instance_number=1,
        manufacturer="ScanFuzz", manufacturer_model_name="Synthetic fixture",
        software_versions="1", device_serial_number="SYNTHETIC", omit_empty_frames=False,
    )
    path = output_dir / "seg.dcm"
    segmentation.save_as(path, enforce_file_format=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    for case in (
        ("byte-aligned-single-frame", 16, 16, 1, 1),
        ("odd-single-frame", 7, 9, 1, 1),
        ("odd-multi-frame", 7, 9, 3, 1),
        ("overlapping-segments", 7, 9, 2, 2),
        ("fractional-control", 16, 16, 1, 1, True),
    ):
        generate_case(args.output_dir, *case)


if __name__ == "__main__":
    main()
