import re
from collections import defaultdict


def analyze_interactions(drug_data, target_drug):
    """
    Analyze drug data from OpenFDA to find mentions of the target drug.

    Args:
        drug_data (dict): OpenFDA drug data with interaction sections
        target_drug (str): Name of the drug to look for

    Returns:
        dict: Analysis results with highlighted text
    """
    result = {
        'found_interactions': False,
        'available_sections': list(drug_data.keys()),
        'highlighted_texts': defaultdict(list),
    }

    if not drug_data:
        return result

    target_variations = get_drug_name_variations(target_drug)

    for section, texts in drug_data.items():
        if not texts:
            continue

        if isinstance(texts, str):
            text_list = [texts]
        else:
            text_list = texts

        for text in text_list:
            for variant in target_variations:
                if variant in text.lower():
                    snippet = re.sub(f"(?i)({re.escape(variant)})", r"**\1**",
                                     text)
                    result['highlighted_texts'][section].append(snippet)
                    result['found_interactions'] = True
                    break  # Only match once per section

    return result


def get_drug_name_variations(drug_name):
    base = drug_name.lower().strip()
    ignore_suffixes = [
        "sodium", "hydrochloride", "acetate", "phosphate", "sulfate",
        "nitrate", "chloride", "mesylate", "succinate"
    ]
    words = base.split()
    core_words = [word for word in words if word not in ignore_suffixes]
    base_name = " ".join(core_words)

    variations = set()
    variations.add(base)
    variations.add(base_name)
    variations.update(core_words)

    return list(variations)


def generate_patient_friendly_summary(snippet):
    lowered = snippet.lower()

    explanations = {
        "bleeding":
        "This combination may increase your risk of serious bleeding.",
        "bleed":
        "This combination may increase your risk of serious bleeding.",
        "hemorrhage":
        "This combination may increase your risk of internal bleeding.",
        "liver damage": "This may harm your liver if taken together.",
        "serotonin syndrome":
        "This could lead to dangerously high levels of serotonin.",
        "qt prolongation": "This may affect your heart rhythm.",
        "cns depression":
        "This may cause extreme drowsiness or slow breathing.",
        "respiratory depression": "This may slow down your breathing.",
        "renal impairment": "This may worsen kidney function.",
        "seizures": "This combination may increase your risk of seizures.",
        "hypotension": "This may cause dangerously low blood pressure.",
        "toxicity": "This may increase your risk of toxicity or overdose.",
    }

    for keyword, summary in explanations.items():
        if keyword in lowered:
            return summary

    return "This combination may lead to unwanted side effects. Please consult your doctor or pharmacist."
