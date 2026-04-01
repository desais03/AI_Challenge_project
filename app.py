import streamlit as st

from claims_copilot.services.claim_service import review_claim
from claims_copilot.data.code_maps import CPT_MAP, ICD_MAP
from claims_copilot.core.llm_reasoner import generate_ai_explanation
from claims_copilot.data.synthetic_data import generate_synthetic_dataset

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI Claims Copilot", layout="wide")

# -----------------------------
# CUSTOM STYLING (YOUR PALETTE)
# -----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(180deg, #fff7ed 0%, #ffffff 100%);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #FF8104, #FF4700);
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-weight: bold;
    border: none;
}

/* Headers */
h2, h3 {
    color: #FA2400;
}

/* Cards */
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown("## 🏥 AI Claims Copilot")
st.markdown("### Proactively Reduce Claim Denials with AI + Policy Validation")

# -----------------------------
# SIDEBAR INPUT
# -----------------------------
st.sidebar.header("Claim Input")

selected_cpt = st.sidebar.selectbox(
    "Select Procedure (CPT)",
    list(CPT_MAP.keys()),
    format_func=lambda x: f"{x} - {CPT_MAP[x]}"
)

selected_icd = st.sidebar.selectbox(
    "Select Diagnosis (ICD)",
    list(ICD_MAP.keys()),
    format_func=lambda x: f"{x} - {ICD_MAP[x]}"
)

st.sidebar.markdown("### Structured Clinical Inputs")

structured_inputs = {
    "conservative_weeks": st.sidebar.slider("Conservative Treatment (weeks)", 0, 10, 6),
    "recent_imaging_months": st.sidebar.slider("Recent Imaging (months ago)", 0, 12, 6),
    "symptoms_worsened": st.sidebar.checkbox("Symptoms worsened"),
    "neurological_symptoms": st.sidebar.checkbox("Neurological symptoms"),
    "imaging_confirms_damage": st.sidebar.checkbox("Imaging confirms damage"),
    "failed_conservative_treatment": st.sidebar.checkbox("Failed conservative treatment"),
    "functional_impairment": st.sidebar.checkbox("Functional impairment"),
    "purely_degenerative": st.sidebar.checkbox("Degenerative condition"),
    "head_trauma_or_severe_neuro": st.sidebar.checkbox("Head trauma / severe neuro"),
    "high_risk_symptoms": st.sidebar.checkbox("High-risk symptoms"),
    "mild_headache_only": st.sidebar.checkbox("Mild headache only"),
    "confirmed_malignancy": st.sidebar.checkbox("Confirmed cancer"),
    "oncologist_plan": st.sidebar.checkbox("Oncologist plan"),
    "lab_and_staging": st.sidebar.checkbox("Lab + staging"),
    "prior_auth_documented": st.sidebar.checkbox("Prior authorization"),
    "guideline_aligned": st.sidebar.checkbox("Guideline aligned"),
}

# -----------------------------
# CLINICAL NOTE
# -----------------------------
st.subheader("📝 Clinical Note")

clinical_note = st.text_area(
    "",
    "Patient presents with lower back pain radiating to leg. Completed 8 weeks PT. MRI recommended.",
    height=150
)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def generate_fix_suggestions(missing_rules):
    suggestions = []
    for rule in missing_rules:
        if "neurological" in rule.lower():
            suggestions.append("Document neurological symptoms explicitly in notes.")
        elif "conservative" in rule.lower():
            suggestions.append("Include prior treatment duration and outcomes.")
        elif "imaging" in rule.lower():
            suggestions.append("Attach imaging reports or justify absence.")
        elif "authorization" in rule.lower():
            suggestions.append("Ensure prior authorization is submitted.")
        else:
            suggestions.append("Provide additional clinical justification.")
    return suggestions


# -----------------------------
# ANALYSIS
# -----------------------------
if st.button("🔍 Analyze Claim"):

    result = review_claim(selected_icd, selected_cpt, clinical_note, structured_inputs)
    evaluation = result["evaluation"]

    # -----------------------------
    # METRICS
    # -----------------------------
    st.subheader("📊 Decision Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"<h2 style='color:#FF4700'>{evaluation['approval_probability']}%</h2>", unsafe_allow_html=True)
        st.caption("Approval Probability")

    with col2:
        st.info(evaluation["verdict"])

    with col3:
        st.warning(f"{len(evaluation['missing_rules'])} Missing Conditions")

    st.divider()

    # -----------------------------
    # RISK + VALUE ADD
    # -----------------------------
    colA, colB, colC = st.columns(3)

    # Risk
    if evaluation["approval_probability"] > 80:
        risk = "Low Risk"
    elif evaluation["approval_probability"] > 50:
        risk = "Medium Risk"
    else:
        risk = "High Risk"

    colA.subheader("🚨 Risk Level")
    colA.error(risk)

    # Time Saved
    time_saved = len(evaluation["missing_rules"]) * 5
    colB.subheader("⏱ Time Saved")
    colB.success(f"{time_saved} mins / claim")

    # Confidence
    confidence = max(100 - (len(evaluation["missing_rules"]) * 10), 50)
    colC.subheader("📊 Confidence")
    colC.info(f"{confidence}%")

    st.divider()

    # -----------------------------
    # CONDITIONS
    # -----------------------------
    colD, colE = st.columns(2)

    with colD:
        st.subheader("✔️ Met Conditions")
        for item in evaluation["met_rules"]:
            st.success(item)

    with colE:
        st.subheader("❌ Missing Conditions")
        for item in evaluation["missing_rules"]:
            st.warning(item)

    st.divider()

    # -----------------------------
    # FIX SUGGESTIONS
    # -----------------------------
    st.subheader("💡 Recommended Fixes")

    fixes = generate_fix_suggestions(evaluation["missing_rules"])

    for fix in fixes:
        st.info(fix)

    st.divider()

    # -----------------------------
    # AI EXPLANATION
    # -----------------------------
    st.subheader("🤖 AI Explanation")

    explanation = generate_ai_explanation(
        clinical_note,
        selected_icd,
        selected_cpt,
        evaluation,
        result["policy_summary"]["rules"]
    )

    st.info(explanation)

# -----------------------------
# IMPACT SIMULATION
# -----------------------------
st.divider()
st.subheader("📊 System Impact Simulation")

if st.button("📈 Run Impact Simulation"):

    df = generate_synthetic_dataset(50)

    before_avg = df["approval_prob"].mean()

    df["improved_prob"] = df["approval_prob"] + (df["missing_rules"] * 5)
    df["improved_prob"] = df["improved_prob"].apply(lambda x: min(x, 100))

    after_avg = df["improved_prob"].mean()

    improvement = ((after_avg - before_avg) / before_avg) * 100

    col1, col2, col3 = st.columns(3)

    col1.metric("Before", f"{int(before_avg)}%")
    col2.metric("After", f"{int(after_avg)}%")
    col3.metric("Improvement", f"{int(improvement)}%")

    st.divider()

    st.bar_chart({
        "Before": df["approval_prob"].value_counts(),
        "After": df["improved_prob"].value_counts()
    })

    st.dataframe(df[["icd", "cpt", "approval_prob", "improved_prob", "missing_rules"]])

# -----------------------------
# FOOTER
# -----------------------------
st.divider()
st.caption("USC Tech Fest AI Challenge | Hybrid AI + Policy Intelligence System")