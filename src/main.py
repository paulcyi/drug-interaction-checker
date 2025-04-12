# src/main.py

interactions = {
    ("aspirin", "ibuprofen"): "Increased risk of bleeding",
    ("acetaminophen", "alcohol"): "Increased risk of liver damage",
    ("lisinopril", "potassium"): "Risk of high potassium levels"
}

def check_interaction(drug1, drug2):
    pair = (drug1.lower(), drug2.lower())
    reverse_pair = (drug2.lower(), drug1.lower())

    if pair in interactions:
        return interactions[pair]
    elif reverse_pair in interactions:
        return interactions[reverse_pair]
    else:
        return "No known interaction"

if __name__ == "__main__":
    print(check_interaction("Aspirin", "Ibuprofen"))
