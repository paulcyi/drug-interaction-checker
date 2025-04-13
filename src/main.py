import requests
from src.utils.fuzzy_match import match_drug

interactions = {
    ("aspirin", "ibuprofen"): "Increased risk of bleeding",
    ("acetaminophen", "alcohol"): "Increased risk of liver damage",
    ("lisinopril", "potassium"): "Risk of high potassium levels"
}


def get_rxcui(drug_name):
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
    response = requests.get(url)
    data = response.json()

    try:
        return data["idGroup"]["rxnormId"][0]
    except (KeyError, IndexError):
        return None


def check_interaction(drug1, drug2):
    pair = (drug1.lower(), drug2.lower())
    reverse_pair = (drug2.lower(), drug1.lower())

    if pair in interactions:
        return interactions[pair]
    elif reverse_pair in interactions:
        return interactions[reverse_pair]
    else:
        return "No known interaction"


def check_interaction_from_rxcuis(rxcui1, rxcui2):
    url = f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui={rxcui1}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DrugCheckerBot/1.0; +https://github.com/paulcyi)"
    }
    response = requests.get(url, headers=headers)

    print(f"🔗 Hitting URL: {url}")
    print(f"API status: {response.status_code}")
    print(f"API raw response (preview):\n{response.text[:300]}")

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        return "❌ API returned an unexpected response (not JSON)."

    try:
        interactions = data['interactionTypeGroup'][0]['interactionType'][0]['interactionPair']
        for interaction in interactions:
            if rxcui2 in interaction['interactionConcept'][1]['minConceptItem']['rxcui']:
                return interaction['description']
        return "No interaction found between these two drugs."
    except (KeyError, IndexError):
        return "ℹ️ No known interaction or drugs not found in interaction database."


if __name__ == "__main__":
    print("Welcome to the Drug Interaction Checker")
    drug1 = input("Enter the first drug: ").strip()
    drug2 = input("Enter the second drug: ").strip()

    rxcui1 = get_rxcui(drug1)
    rxcui2 = get_rxcui(drug2)

    if rxcui1 and rxcui2:
        interaction_result = check_interaction_from_rxcuis(rxcui1, rxcui2)
        print(f"\nInteraction between {drug1.title()} and {drug2.title()}:")
        print(interaction_result)
    else:
        print("\n❌ One or both drugs not recognized.")
