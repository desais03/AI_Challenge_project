# synthetic_data.py

import random
import pandas as pd
from typing import List, Dict

from claims_copilot.core.evaluator import evaluate_claim


def generate_clinical_note(cpt_code: str, is_good_case: bool) -> str:

    if cpt_code == "72148":  # MRI
        if is_good_case:
            return "Patient presents with lower back pain radiating to leg with numbness. Completed 8 weeks of physical therapy with no improvement. MRI recommended."
        else:
            return "Patient has mild back pain. MRI requested."

    elif cpt_code == "29881":  # Knee
        if is_good_case:
            return "MRI confirms meniscal tear. Patient has instability and failed physical therapy. Surgery recommended."
        else:
            return "Knee discomfort, no imaging confirmation. Surgery requested."

    elif cpt_code == "70450":  # CT Head
        if is_good_case:
            return "Patient suffered head trauma with vomiting and confusion. CT required to rule out bleeding."
        else:
            return "Patient reports mild headache. CT requested."

    elif cpt_code == "96413":  # Chemo
        if is_good_case:
            return "Biopsy confirmed cancer. Oncologist approved chemotherapy plan with staging complete."
        else:
            return "Possible cancer, no staging or treatment plan. Chemo requested."

    return "Generic clinical note"


def generate_synthetic_dataset(n: int = 50) -> pd.DataFrame:

    data: List[Dict] = []

    icd_options = [
        "M54.16", "M51.26",
        "S83.241A", "M23.203",
        "S06.0X0A", "R51",
        "C50.911", "C34.90"
    ]

    cpt_options = ["72148", "29881", "70450", "96413"]

    for i in range(n):

        cpt = random.choice(cpt_options)
        icd = random.choice(icd_options)

        is_good_case = random.random() > 0.4

        clinical_note = generate_clinical_note(cpt, is_good_case)

        structured_inputs = {
            "conservative_weeks": random.choice([0, 2, 4, 6, 8]),
            "recent_imaging_months": random.choice([1, 3, 6, 12]),
            "symptoms_worsened": random.choice([True, False]),
            "neurological_symptoms": random.choice([True, False]),
            "imaging_confirms_damage": random.choice([True, False]),
            "failed_conservative_treatment": random.choice([True, False]),
            "functional_impairment": random.choice([True, False]),
            "purely_degenerative": random.choice([True, False]),
            "head_trauma_or_severe_neuro": random.choice([True, False]),
            "high_risk_symptoms": random.choice([True, False]),
            "mild_headache_only": random.choice([True, False]),
            "confirmed_malignancy": random.choice([True, False]),
            "oncologist_plan": random.choice([True, False]),
            "lab_and_staging": random.choice([True, False]),
            "prior_auth_documented": random.choice([True, False]),
            "guideline_aligned": random.choice([True, False]),
        }

        result = evaluate_claim(icd, cpt, clinical_note, structured_inputs)

        data.append({
            "claim_id": f"CLM_{i+1}",
            "icd": icd,
            "cpt": cpt,
            "note": clinical_note,
            "approval_prob": result["approval_probability"],
            "verdict": result["verdict"],
            "missing_rules": len(result["missing_rules"])
        })

    return pd.DataFrame(data)