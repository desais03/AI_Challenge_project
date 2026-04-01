# claim_service.py

from typing import Dict, Any

from claims_copilot.core.evaluator import evaluate_claim
from claims_copilot.data.code_maps import get_icd_label, get_cpt_label
from claims_copilot.data.policies import get_policy_by_cpt


def review_claim(
    icd_code: str,
    cpt_code: str,
    clinical_note: str,
    structured_inputs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Main orchestration function for reviewing a claim.
    This is the service layer the UI will call.
    """

    evaluation = evaluate_claim(
        icd_code=icd_code,
        cpt_code=cpt_code,
        clinical_note=clinical_note,
        structured_inputs=structured_inputs,
    )

    policy = get_policy_by_cpt(cpt_code)

    return {
        "claim_summary": {
            "icd_code": icd_code,
            "icd_label": get_icd_label(icd_code),
            "cpt_code": cpt_code,
            "cpt_label": get_cpt_label(cpt_code),
        },
        "policy_summary": {
            "policy_id": policy["policy_id"],
            "procedure_name": policy["procedure_name"],
            "allowed_icd_codes": policy["allowed_icd_codes"],
            "rules": policy["rules"],
        },
        "evaluation": evaluation,
    }