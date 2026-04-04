import streamlit as st

from claims_copilot.services.claim_service import review_claim
from claims_copilot.data.code_maps import CPT_MAP, ICD_MAP
from claims_copilot.core.llm_reasoner import generate_ai_explanation
from claims_copilot.data.synthetic_data import generate_synthetic_dataset

st.set_page_config(page_title="ClaimIQ", layout="wide")

# -----------------------------
# GLOBAL STYLING
# -----------------------------
st.markdown("""
<style>

/* Fonts */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Inter:wght@300;400;600&display=swap');

/* Background */
html, body {
    background: linear-gradient(180deg, #fff7f2 0%, #fdf2e9 50%, #f8ede3 100%) !important;
    font-family: 'Inter', sans-serif;
    color: #231F20;
}

/* Remove white blocks */
[data-testid="stAppViewContainer"],
[data-testid="stVerticalBlock"] {
    background: transparent !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f6efe8;
}

/* Layout */
.block-container {
    padding: 2rem;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #AD974F, #8E793E);
    color: #fffaf7;
    border-radius: 12px;
    font-weight: 600;
    border: none;
}

/* Headers */
h2, h3 {
    color: #8E793E;
}

/* HERO */
.hero {
    position: relative;
    height: 320px;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 40px;
    background: url('https://images.unsplash.com/photo-1580281657527-47f249e9c0a2') center/cover no-repeat;
}

.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background: rgba(20,20,20,0.65);
}

.hero-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    color: #fffaf7;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 68px;
    font-weight: 800;
    letter-spacing: 1.5px;

    color: #E6C77A;  /* brighter gold */

    text-shadow: 
        0px 2px 8px rgba(0,0,0,0.6),
        0px 0px 20px rgba(230, 199, 122, 0.25);
}

.hero-sub {
    margin-top: 15px;
    font-size: 20px;
    color: #f3f3f3;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="hero-content">
        <div class="hero-title">ClaimIQ</div>
        <div class="hero-sub">
            Health Insurance now simplified
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# CUSTOM CARD FUNCTION
# -----------------------------
def render_card(text, type="neutral"):
    color_map = {
        "success": "#e8f5ec",
        "warning": "#fff4e5",
        "neutral": "#f7f5f2"
    }

    st.markdown(
        f"""
        <div style="
            background-color: {color_map[type]};
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 8px;
            border-left: 4px solid #AD974F;
            font-size: 14px;
        ">
        {text}
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# NEW: DOCUMENT LOGIC
# -----------------------------
def evaluate_documents(evaluation, document_inputs):
    missing_docs = []
    available_docs = []

    required_docs = {
        "insurance_card": "Insurance Card",
        "physician_notes": "Physician Notes",
        "icd_cpt_codes": "ICD & CPT Codes",
        "medical_necessity": "Medical Necessity Proof"
    }

    rules_text = " ".join(evaluation["met_rules"] + evaluation["missing_rules"]).lower()

    if "imaging" in rules_text:
        required_docs["imaging_reports"] = "Imaging Reports"

    if "authorization" in rules_text:
        required_docs["prior_authorization"] = "Prior Authorization"

    for key, label in required_docs.items():
        if document_inputs.get(key):
            available_docs.append(label)
        else:
            missing_docs.append(label)

    return available_docs, missing_docs


# -----------------------------
# SIDEBAR (UNCHANGED + ADDED DOCS)
# -----------------------------
st.sidebar.header("Claim Input")

selected_cpt = st.sidebar.selectbox(
    "Procedure (CPT)",
    list(CPT_MAP.keys()),
    format_func=lambda x: f"{x} - {CPT_MAP[x]}"
)

selected_icd = st.sidebar.selectbox(
    "Diagnosis (ICD)",
    list(ICD_MAP.keys()),
    format_func=lambda x: f"{x} - {ICD_MAP[x]}"
)

st.sidebar.markdown("### Clinical Inputs")

structured_inputs = {
    "conservative_weeks": st.sidebar.slider("Treatment Weeks", 0, 10, 6),
    "recent_imaging_months": st.sidebar.slider("Recent Imaging (months)", 0, 12, 6),
    "neurological_symptoms": st.sidebar.checkbox("Neurological symptoms"),
    "failed_conservative_treatment": st.sidebar.checkbox("Failed treatment"),
    "imaging_confirms_damage": st.sidebar.checkbox("Imaging confirms damage"),
    "functional_impairment": st.sidebar.checkbox("Functional impairment"),
    "prior_auth_documented": st.sidebar.checkbox("Prior authorization"),
}

# -----------------------------
# NEW: DOCUMENT CHECKBOXES
# -----------------------------
st.sidebar.markdown("### Documents")

document_inputs = {
    "insurance_card": st.sidebar.checkbox("Insurance Card"),
    "physician_notes": st.sidebar.checkbox("Physician Notes"),
    "icd_cpt_codes": st.sidebar.checkbox("ICD & CPT Codes"),
    "medical_necessity": st.sidebar.checkbox("Medical Necessity Documentation"),
    "imaging_reports": st.sidebar.checkbox("Imaging Reports"),
    "prior_authorization": st.sidebar.checkbox("Prior Authorization"),
}

# -----------------------------
# INPUT
# -----------------------------
st.subheader("Clinical Note")

clinical_note = st.text_area(
    "",
    "Patient presents with lower back pain radiating to leg. Completed 8 weeks PT. MRI recommended.",
    height=150
)

# -----------------------------
# ANALYSIS
# -----------------------------
if st.button("Analyze Claim"):

    result = review_claim(selected_icd, selected_cpt, clinical_note, structured_inputs)
    evaluation = result["evaluation"]

    # -----------------------------
    # NEW: DOCUMENT EVALUATION
    # -----------------------------
    available_docs, missing_docs = evaluate_documents(evaluation, document_inputs)

    # -----------------------------
    # NEW: DOCUMENT IMPACT ON SCORE
    # -----------------------------
    penalty = len(missing_docs) * 5
    adjusted_score = max(evaluation["approval_probability"] - penalty, 0)
    evaluation["adjusted_probability"] = adjusted_score

    st.subheader("Decision Summary")

    col1, col2, col3 = st.columns(3)

    # 👇 ONLY CHANGE: use adjusted score
    col1.metric("Approval", f"{evaluation['adjusted_probability']}%")
    col2.metric("Verdict", evaluation["verdict"])
    col3.metric("Missing", len(evaluation["missing_rules"]))

    st.divider()

    colA, colB, colC = st.columns(3)

    risk = "Low" if adjusted_score > 80 else "Medium" if adjusted_score > 50 else "High"

    colA.metric("Risk", risk)
    colB.metric("Time Saved", f"{len(evaluation['missing_rules']) * 5} mins")
    colC.metric("Confidence", f"{max(100 - len(evaluation['missing_rules']) * 10, 50)}%")

    st.divider()

    colD, colE = st.columns(2)

    with colD:
        st.subheader("Met Conditions")
        for r in evaluation["met_rules"]:
            render_card(r, "success")

    with colE:
        st.subheader("Missing Conditions")
        for r in evaluation["missing_rules"]:
            render_card(r, "warning")

    st.divider()

    # -----------------------------
    # UPDATED DOCUMENT SECTION
    # -----------------------------
    st.subheader(" Document Readiness")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Available Documents")
        for doc in available_docs:
            render_card(doc, "success")

    with col2:
        st.markdown("### Missing Documents")
        for doc in missing_docs:
            render_card(doc, "warning")

    st.markdown("### AI Validation Status")

    render_card(f"Approval likelihood: {adjusted_score}%", "neutral")

    if len(missing_docs) > 0:
        render_card("⚠️ Missing required documentation", "warning")
    else:
        render_card("✅ Documents complete. Ready for submission.", "success")

    st.divider()

    # -----------------------------
    # AI EXPLANATION
    # -----------------------------
    st.subheader("AI Explanation")

    explanation = generate_ai_explanation(
        clinical_note,
        selected_icd,
        selected_cpt,
        evaluation,
        result["policy_summary"]["rules"]
    )

    render_card(explanation, "neutral")

# -----------------------------
# SIMULATION
# -----------------------------
st.divider()
st.subheader("Impact Simulation")

if st.button("Run Simulation"):

    df = generate_synthetic_dataset(50)

    before = df["approval_prob"].mean()
    df["improved"] = df["approval_prob"] + (df["missing_rules"] * 5)
    df["improved"] = df["improved"].clip(upper=100)

    after = df["improved"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric("Before", f"{int(before)}%")
    col2.metric("After", f"{int(after)}%")
    col3.metric("Improvement", f"{int(((after - before)/before)*100)}%")

    st.bar_chart(df[["approval_prob", "improved"]])

# -----------------------------
# FOOTER
# -----------------------------
st.divider()
st.caption("AI Claims Copilot • USC Tech Fest")