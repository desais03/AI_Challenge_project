# policies.py

from typing import List, Dict

def get_policies() -> List[Dict]:
    return [

        {
            "policy_id": "POL001",
            "procedure_name": "MRI Lumbar Spine",
            "cpt_code": "72148",
            "allowed_icd_codes": ["M54.16", "M51.26"],

            "rules": [
                {
                    "id": "neuro_symptoms",
                    "label": "Neurological symptoms present",
                    "description": "Patient must have neurological symptoms such as numbness, weakness, or radiculopathy.",
                    "weight": 0.30,
                },
                {
                    "id": "conservative_6_weeks",
                    "label": "Conservative treatment >= 6 weeks",
                    "description": "Physical therapy or medication must be attempted for at least 6 weeks.",
                    "weight": 0.25,
                },
                {
                    "id": "no_recent_imaging",
                    "label": "No recent imaging unless worsening",
                    "description": "MRI is not covered if imaging was done within 6 months unless symptoms worsened.",
                    "weight": 0.20,
                },
                {
                    "id": "medical_necessity",
                    "label": "Medical necessity documented",
                    "description": "Clinical notes must justify the need for MRI.",
                    "weight": 0.25,
                },
            ],
        },

        {
            "policy_id": "POL002",
            "procedure_name": "Knee Arthroscopy",
            "cpt_code": "29881",
            "allowed_icd_codes": ["S83.241A", "M23.203"],

            "rules": [
                {
                    "id": "imaging_confirms_damage",
                    "label": "Imaging confirms structural damage",
                    "description": "MRI or imaging must confirm meniscal tear.",
                    "weight": 0.30,
                },
                {
                    "id": "failed_conservative",
                    "label": "Failed conservative treatment",
                    "description": "Rest or physical therapy must have failed.",
                    "weight": 0.25,
                },
                {
                    "id": "functional_impairment",
                    "label": "Functional impairment present",
                    "description": "Patient must have locking, instability, or severe pain.",
                    "weight": 0.25,
                },
                {
                    "id": "not_degenerative",
                    "label": "Not purely degenerative",
                    "description": "Not covered if condition is only mild degeneration.",
                    "weight": 0.20,
                },
            ],
        },

        {
            "policy_id": "POL003",
            "procedure_name": "CT Head",
            "cpt_code": "70450",
            "allowed_icd_codes": ["S06.0X0A", "R51"],

            "rules": [
                {
                    "id": "trauma_or_severe",
                    "label": "Head trauma or severe symptoms",
                    "description": "Must have head trauma or severe neurological concern.",
                    "weight": 0.30,
                },
                {
                    "id": "high_risk",
                    "label": "High-risk symptoms",
                    "description": "Loss of consciousness, vomiting, or confusion.",
                    "weight": 0.30,
                },
                {
                    "id": "justification",
                    "label": "Clinical justification documented",
                    "description": "Reason for CT must be clearly documented.",
                    "weight": 0.20,
                },
                {
                    "id": "not_mild",
                    "label": "Not mild headache only",
                    "description": "Mild headache alone is not sufficient.",
                    "weight": 0.20,
                },
            ],
        },

        {
            "policy_id": "POL004",
            "procedure_name": "Chemotherapy Infusion",
            "cpt_code": "96413",
            "allowed_icd_codes": ["C50.911", "C34.90"],

            "rules": [
                {
                    "id": "confirmed_cancer",
                    "label": "Confirmed malignancy",
                    "description": "Cancer diagnosis must be confirmed.",
                    "weight": 0.25,
                },
                {
                    "id": "oncologist_plan",
                    "label": "Oncologist-approved plan",
                    "description": "Treatment must be approved by oncologist.",
                    "weight": 0.25,
                },
                {
                    "id": "lab_staging",
                    "label": "Lab and staging documented",
                    "description": "Staging and lab results required.",
                    "weight": 0.20,
                },
                {
                    "id": "prior_auth",
                    "label": "Prior authorization",
                    "description": "Authorization required before treatment.",
                    "weight": 0.15,
                },
                {
                    "id": "guideline",
                    "label": "Guideline aligned",
                    "description": "Treatment follows standard guidelines.",
                    "weight": 0.15,
                },
            ],
        },
    ]


def get_policy_by_cpt(cpt_code: str) -> Dict:
    policies = get_policies()
    for policy in policies:
        if policy["cpt_code"] == cpt_code:
            return policy
    raise ValueError(f"No policy found for CPT {cpt_code}")