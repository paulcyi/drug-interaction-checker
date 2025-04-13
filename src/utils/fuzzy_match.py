from rapidfuzz import process

KNOWN_DRUGS = [
    "aspirin", "ibuprofen", "acetaminophen", "lisinopril",
    "potassium", "alcohol", "tadalafil", "nitrates"
]

def match_drug(input_name, score_cutoff=80):
    """
    Attempts to match a possibly misspelled drug name to a known drug.

    Args:
        input_name (str): User input
        score_cutoff (int): Minimum score for match confidence (0–100)

    Returns:
        str: Best-matched drug name or original input if no match
    """
    match, score, _ = process.extractOne(input_name, KNOWN_DRUGS, score_cutoff=score_cutoff)
    return match if match else input_name
