# code_maps.py

from typing import Dict


# ICD → Diagnosis mapping
ICD_MAP: Dict[str, str] = {
    "M54.16": "Radiculopathy, lumbar region",
    "M51.26": "Intervertebral disc displacement, lumbar region",

    "S83.241A": "Tear of medial meniscus, right knee",
    "M23.203": "Meniscus derangement, unspecified knee",

    "S06.0X0A": "Concussion without loss of consciousness",
    "R51": "Headache",

    "C50.911": "Breast cancer, right side",
    "C34.90": "Lung cancer, unspecified",
}


# CPT → Procedure mapping
CPT_MAP: Dict[str, str] = {
    "72148": "MRI Lumbar Spine",
    "29881": "Knee Arthroscopy",
    "70450": "CT Head",
    "96413": "Chemotherapy Infusion",
}


def get_icd_label(icd_code: str) -> str:
    return ICD_MAP.get(icd_code, "Unknown ICD Code")


def get_cpt_label(cpt_code: str) -> str:
    return CPT_MAP.get(cpt_code, "Unknown CPT Code")