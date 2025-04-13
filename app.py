import streamlit as st
from src.utils.fuzzy_match import match_drug

# ---- Mocked interaction data ----
interactions = {
    ("aspirin", "ibuprofen"): "Increased risk of bleeding",
    ("acetaminophen", "alcohol"): "Increased risk of liver damage",
    ("lisinopril", "potassium"): "Risk of high potassium levels",
    ("tadalafil", "nitrates"): "May cause dangerous drop in blood pressure"
}


# ---- Core logic ----
def check_interaction(drug1, drug2):
    drug1 = match_drug(drug1)
    drug2 = match_drug(drug2)

    pair = (drug1.lower(), drug2.lower())
    reverse_pair = (drug2.lower(), drug1.lower())

    if pair in interactions:
        return interactions[pair]
    elif reverse_pair in interactions:
        return interactions[reverse_pair]
    else:
        return "No known interaction."


# ---- Streamlit App ----
st.set_page_config(page_title="Check My Meds", page_icon="💊")

st.title("💊 Check My Meds")
st.subheader("Instantly check for potential drug-drug interactions")

with st.form("interaction_form"):
    drug1 = st.text_input("First drug")
    drug2 = st.text_input("Second drug")
    submitted = st.form_submit_button("Check Interaction")

    if submitted:
        if drug1 and drug2:
            matched1 = match_drug(drug1)
            matched2 = match_drug(drug2)

            result = check_interaction(matched1, matched2)

            st.markdown("### 🔍 Result")
            st.success(f"**{matched1.title()} + {matched2.title()}** → {result}")

            if drug1.lower() != matched1.lower() or drug2.lower() != matched2.lower():
                st.info(f"Showing results for corrected spelling: **{matched1.title()} + {matched2.title()}**")
        else:
            st.warning("Please enter two drug names.")
