# evaluator.py

from typing import Dict, List

from claims_copilot.data.policies import get_policy_by_cpt


def evaluate_claim(
    icd_code: str,
    cpt_code: str,
    clinical_note: str,
    structured_inputs: Dict
) -> Dict:

    policy = get_policy_by_cpt(cpt_code)

    score = 0.0
    met_rules: List[str] = []
    missing_rules: List[str] = []

    # -----------------------------
    # Step 1: ICD validation
    # -----------------------------
    if icd_code in policy["allowed_icd_codes"]:
        score += 0.15
        icd_valid = True
    else:
        icd_valid = False

    # -----------------------------
    # Step 2: Rule evaluation
    # -----------------------------
    rule_results = {}

    if cpt_code == "72148":  # MRI
        rule_results = {
            "neuro_symptoms": structured_inputs["neurological_symptoms"],
            "conservative_6_weeks": structured_inputs["conservative_weeks"] >= 6,
            "no_recent_imaging": structured_inputs["recent_imaging_months"] >= 6 or structured_inputs["symptoms_worsened"],
            "medical_necessity": "recommended" in clinical_note.lower()
        }

    elif cpt_code == "29881":  # Knee
        rule_results = {
            "imaging_confirms_damage": structured_inputs["imaging_confirms_damage"],
            "failed_conservative": structured_inputs["failed_conservative_treatment"],
            "functional_impairment": structured_inputs["functional_impairment"],
            "not_degenerative": not structured_inputs["purely_degenerative"]
        }

    elif cpt_code == "70450":  # CT
        rule_results = {
            "trauma_or_severe": structured_inputs["head_trauma_or_severe_neuro"],
            "high_risk": structured_inputs["high_risk_symptoms"],
            "justification": "required" in clinical_note.lower() or "rule out" in clinical_note.lower(),
            "not_mild": not structured_inputs["mild_headache_only"]
        }

    elif cpt_code == "96413":  # Chemo
        rule_results = {
            "confirmed_cancer": structured_inputs["confirmed_malignancy"],
            "oncologist_plan": structured_inputs["oncologist_plan"],
            "lab_staging": structured_inputs["lab_and_staging"],
            "prior_auth": structured_inputs["prior_auth_documented"],
            "guideline": structured_inputs["guideline_aligned"]
        }

    # -----------------------------
    # Step 3: Score rules
    # -----------------------------
    for rule in policy["rules"]:
        rule_id = rule["id"]
        weight = rule["weight"]

        if rule_results.get(rule_id, False):
            score += weight
            met_rules.append(rule["label"])
        else:
            missing_rules.append(rule["description"])

    # -----------------------------
    # Step 4: Final score
    # -----------------------------
    approval_probability = int(min(score * 100, 100))

    if approval_probability >= 80:
        verdict = "Likely Approved"
    elif approval_probability >= 55:
        verdict = "Needs Review"
    else:
        verdict = "Likely Denied"

    # -----------------------------
    # Step 5: Return result
    # -----------------------------
    return {
        "approval_probability": approval_probability,
        "verdict": verdict,
        "icd_valid": icd_valid,
        "met_rules": met_rules,
        "missing_rules": missing_rules
    }