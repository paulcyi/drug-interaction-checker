import requests

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
    url = f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={rxcui1}+{rxcui2}"
    response = requests.get(url)
    data = response.json()

    try:
        interactions = data['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair']
        for interaction in interactions:
            return interaction['description']
    except (KeyError, IndexError):
        return "No known interaction or drugs not found in interaction database."


if __name__ == "__main__":
    drug1 = "aspirin"
    drug2 = "ibuprofen"

    rxcui1 = get_rxcui(drug1)
    rxcui2 = get_rxcui(drug2)

    if rxcui1 and rxcui2:
        interaction_result = check_interaction_from_rxcuis(rxcui1, rxcui2)
        print(f"Interaction between {drug1.title()} and {drug2.title()}: {interaction_result}")
    else:
        print("One or both drugs not recognized.")
