import streamlit as st
from utils.api_utils import get_rxnav_interactions, get_openfda_interactions
from utils.nlp_utils import analyze_interactions, generate_patient_friendly_summary

st.set_page_config(page_title="CheckMyMeds - Drug Interaction Checker",
                   page_icon="💊",
                   layout="wide")


def main():
    st.title("💊 CheckMyMeds")
    st.subheader("Drug Interaction Checker")

    st.markdown("""
    This application helps you check for potential interactions between medications.
    Enter the names of two drugs below to see if there are any known interactions.
    """)

    col1, col2 = st.columns(2)

    with col1:
        drug1 = st.text_input("First Drug Name", key="drug1")

    with col2:
        drug2 = st.text_input("Second Drug Name", key="drug2")

    if st.button("Check Interaction", type="primary"):
        if not drug1 or not drug2:
            st.error("Please enter both drug names to check for interactions.")
        elif drug1.lower() == drug2.lower():
            st.warning("Please enter two different drug names.")
        else:
            with st.spinner(
                    f"Checking for interactions between {drug1} and {drug2}..."
            ):
                rxnav_results = get_rxnav_interactions(drug1, drug2)

                if rxnav_results['status'] == 'success' and rxnav_results[
                        'interactions']:
                    display_rxnav_results(rxnav_results, drug1, drug2)
                else:
                    st.info(
                        "No interactions found in RxNav or RxNav service unavailable. Checking OpenFDA..."
                    )

                    med1 = drug1.strip().lower()
                    med2 = drug2.strip().lower()

                    found_mentions = []

                    openfda1 = get_openfda_interactions(med1)
                    if openfda1['status'] == 'success':
                        analysis1 = analyze_interactions(
                            openfda1['data'], med2)
                        if analysis1['found_interactions']:
                            found_mentions.append((med1, med2, analysis1))

                    openfda2 = get_openfda_interactions(med2)
                    if openfda2['status'] == 'success':
                        analysis2 = analyze_interactions(
                            openfda2['data'], med1)
                        if analysis2['found_interactions']:
                            found_mentions.append((med2, med1, analysis2))

                    if found_mentions:
                        for primary, secondary, result in found_mentions:
                            display_openfda_results(result, primary, secondary)
                    else:
                        st.info(
                            f"No label mentions found between {drug1.title()} and {drug2.title()} in FDA data."
                        )

    st.markdown("---")
    st.caption("""
    **Disclaimer**: This application provides information from public APIs and is intended for educational purposes only.
    Always consult your healthcare provider before making any decisions about your medications.
    """)


def display_rxnav_results(results, drug1, drug2):
    st.success("✅ Drug interaction information found in RxNav")

    interactions = results['interactions']

    if not interactions:
        st.info(
            f"No known interactions found between {drug1} and {drug2} in RxNav database."
        )
        return

    st.subheader(f"Interaction Information: {drug1} + {drug2}")

    for idx, interaction in enumerate(interactions, 1):
        with st.expander(
                f"Interaction {idx}: {interaction.get('severity', 'Information')}"
        ):
            st.markdown(f"**Description**: {interaction['description']}")

            if 'severity' in interaction:
                severity_color = "🔴" if interaction['severity'].lower(
                ) == 'high' else "🟠" if interaction['severity'].lower(
                ) == 'moderate' else "🟡"
                st.markdown(
                    f"**Severity**: {severity_color} {interaction['severity']}"
                )

            if 'source' in interaction:
                st.markdown(f"**Source**: {interaction['source']}")


def display_openfda_results(results, drug1, drug2):
    if results['found_interactions']:
        st.warning(
            f"⚠️ Potential interactions between {drug1} and {drug2} found in FDA label data"
        )

        st.subheader(
            f"Potential Interaction Information: {drug1.title()} + {drug2.title()}"
        )

        for section, texts in results['highlighted_texts'].items():
            if texts:
                with st.expander(
                        f"From {section.replace('_', ' ').title()} Section"):
                    for text in texts:
                        st.markdown("📄 **Label Snippet:**")
                        st.markdown(f"> {text}")

                        summary = generate_patient_friendly_summary(text)
                        st.markdown(f"🧠 **What This Means:**\n\n{summary}")
    else:
        st.info(
            f"No mentions of {drug2} found in {drug1}'s OpenFDA drug information."
        )

        if results['available_sections']:
            st.subheader(f"Available Information for {drug1.title()}")
            for section in results['available_sections']:
                st.markdown(f"- {section.replace('_', ' ').title()}")
        else:
            st.info(
                f"No detailed label information found for {drug1.title()} in OpenFDA database."
            )


if __name__ == "__main__":
    main()
