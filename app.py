import streamlit as st

# ---- Mocked interaction data ----
interactions = {
    ("aspirin", "ibuprofen"): "Increased risk of bleeding",
    ("acetaminophen", "alcohol"): "Increased risk of liver damage",
    ("lisinopril", "potassium"): "Risk of high potassium levels",
    ("tadalafil", "nitrates"): "May cause dangerous drop in blood pressure"
}


# ---- Core logic ----
def check_interaction(drug1, drug2):
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
            result = check_interaction(drug1, drug2)
            st.markdown(f"### 🔍 Result")
            st.success(f"**{drug1.title()} + {drug2.title()}** → {result}")
        else:
            st.warning("Please enter two drug names.")
