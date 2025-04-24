import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_rxnav_interactions(drug1, drug2):
    """
    Get interaction information between two drugs from RxNav API
    
    Args:
        drug1 (str): Name of the first drug
        drug2 (str): Name of the second drug
        
    Returns:
        dict: Status and interaction data
    """
    result = {
        'status': 'error',
        'message': '',
        'interactions': []
    }
    
    try:
        # First, find RxCUIs for the drug names
        drug1_rxcui = get_rxcui(drug1)
        drug2_rxcui = get_rxcui(drug2)
        
        if not drug1_rxcui:
            result['message'] = f"Could not find RxCUI for {drug1}"
            return result
            
        if not drug2_rxcui:
            result['message'] = f"Could not find RxCUI for {drug2}"
            return result
        
        # Now check for interactions using the RxCUIs
        interactions_url = f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={drug1_rxcui}+{drug2_rxcui}"
        response = requests.get(interactions_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if there are interaction groups in the response
            if 'fullInteractionTypeGroup' in data['interactionTypeGroup']:
                interactions = []
                
                for group in data['interactionTypeGroup'][0]['fullInteractionType']:
                    for interaction in group['interactionPair']:
                        description = interaction['description']
                        severity = get_interaction_severity(description)
                        
                        interactions.append({
                            'description': description,
                            'severity': severity,
                            'source': group.get('source', 'RxNav')
                        })
                
                result['status'] = 'success'
                result['interactions'] = interactions
            else:
                # No interactions found
                result['status'] = 'success'
                result['message'] = 'No interactions found'
        else:
            result['message'] = f"RxNav API returned status code {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        result['message'] = f"Error connecting to RxNav API: {str(e)}"
        logger.error(f"RxNav API error: {str(e)}")
    except json.JSONDecodeError:
        result['message'] = "Error parsing RxNav API response"
        logger.error("JSON decode error with RxNav response")
    except Exception as e:
        result['message'] = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error in get_rxnav_interactions: {str(e)}")
    
    return result

def get_rxcui(drug_name):
    """
    Get RxCUI (RxNorm Concept Unique Identifier) for a drug name
    
    Args:
        drug_name (str): Name of the drug
        
    Returns:
        str: RxCUI if found, None otherwise
    """
    try:
        # Use RxNav API to find the RxCUI by drug name
        url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}&search=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if RxCUI was found
            if 'idGroup' in data and 'rxnormId' in data['idGroup'] and data['idGroup']['rxnormId']:
                return data['idGroup']['rxnormId'][0]
    
    except Exception as e:
        logger.error(f"Error getting RxCUI for {drug_name}: {str(e)}")
    
    return None

def get_interaction_severity(description):
    """
    Estimate interaction severity based on description text
    
    Args:
        description (str): Interaction description
        
    Returns:
        str: Estimated severity (High, Moderate, or Low)
    """
    # Keywords that might indicate high severity
    high_severity_keywords = [
        'contraindicated', 'severe', 'fatal', 'death', 'life-threatening',
        'avoid', 'dangerous', 'serious', 'risk', 'not recommended'
    ]
    
    # Keywords that might indicate moderate severity
    moderate_severity_keywords = [
        'caution', 'adjust', 'monitor', 'reduce', 'increase',
        'moderate', 'may', 'possible', 'potentially'
    ]
    
    description_lower = description.lower()
    
    for keyword in high_severity_keywords:
        if keyword in description_lower:
            return "High"
    
    for keyword in moderate_severity_keywords:
        if keyword in description_lower:
            return "Moderate"
    
    return "Low"

def get_openfda_interactions(drug_name):
    """
    Get drug information from OpenFDA API
    
    Args:
        drug_name (str): Name of the drug
        
    Returns:
        dict: Status and drug data
    """
    result = {
        'status': 'error',
        'message': '',
        'data': {}
    }
    
    try:
        # Search OpenFDA for the drug by name
        url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{drug_name}+brand_name:{drug_name}&limit=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                drug_data = data['results'][0]
                
                # Extract interaction sections
                interaction_data = {}
                
                # Check for drug interactions section
                if 'drug_interactions' in drug_data:
                    interaction_data['drug_interactions'] = drug_data['drug_interactions']
                
                # Check for warnings section
                if 'warnings' in drug_data:
                    interaction_data['warnings'] = drug_data['warnings']
                
                # Check for precautions section
                if 'precautions' in drug_data:
                    interaction_data['precautions'] = drug_data['precautions']
                
                # Check for boxed warnings (high severity)
                if 'boxed_warning' in drug_data:
                    interaction_data['boxed_warning'] = drug_data['boxed_warning']
                
                # Additional useful sections
                if 'warnings_and_cautions' in drug_data:
                    interaction_data['warnings_and_cautions'] = drug_data['warnings_and_cautions']
                
                result['status'] = 'success'
                result['data'] = interaction_data
            else:
                result['status'] = 'error'
                result['message'] = f"No information found for {drug_name} in OpenFDA"
        elif response.status_code == 404:
            result['status'] = 'error'
            result['message'] = f"No information found for {drug_name} in OpenFDA"
        else:
            result['status'] = 'error'
            result['message'] = f"OpenFDA API returned status code {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        result['message'] = f"Error connecting to OpenFDA API: {str(e)}"
        logger.error(f"OpenFDA API error: {str(e)}")
    except json.JSONDecodeError:
        result['message'] = "Error parsing OpenFDA API response"
        logger.error("JSON decode error with OpenFDA response")
    except Exception as e:
        result['message'] = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error in get_openfda_interactions: {str(e)}")
    
    return result
