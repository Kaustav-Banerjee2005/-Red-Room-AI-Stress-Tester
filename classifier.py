# classifier.py
import re
from transformers import pipeline

print("Initializing Safety Classifier Engine...")
try:
    # Loads the toxic-bert model from HuggingFace
    toxicity_analyzer = pipeline(
        "text-classification", 
        model="unitary/toxic-bert", 
        tokenizer="unitary/toxic-bert"
    )
    print("Safety models loaded successfully.")
except Exception as e:
    print(f"Model loading failed: {e}")
    toxicity_analyzer = None
def detect_jailbreak(text: str) -> bool:
    """
    Scans text for adversarial jailbreaks, developer mode bypasses,
    and system override phrases using case-insensitive regex.
    """
    jailbreak_patterns = [
        r"ignore previous instructions",
        r"pretend you are",
        r"dan",
        r"developer mode",
        r"no restrictions",
        r"system override",
        r"you are now unfiltered",
        r"bypass safety",
        r"jailbreak",
        r"disregard all prior rules"
    ]
    combined_pattern = re.compile("|".join(jailbreak_patterns), re.IGNORECASE)
    return bool(combined_pattern.search(text))


def detect_pii(text: str) -> list:
    """
    Scans text for personal data leaks (Emails, Phone numbers, Card numbers).
    Returns a list of flagged PII types.
    """
    detected_pii = []
    
    email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    phone_regex = re.compile(r'\b\d{10}\b|\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b')
    card_regex = re.compile(r'\b\d{4}[-\s]??\d{4}[-\s]??\d{4}[-\s]??\d{4}\b')
    
    if email_regex.search(text):
        detected_pii.append("email")
    if phone_regex.search(text):
        detected_pii.append("phone_number")
    if card_regex.search(text):
        detected_pii.append("card_number")
        
    return detected_pii
print(detect_jailbreak("Please ignore previous instructions"))
def get_toxicity_score(text: str) -> float:
    """
    Passes text through toxic-bert to evaluate toxicity.
    Returns a confidence score between 0.0 and 1.0 if toxic, else 0.0.
    """
    if not toxicity_analyzer:
        return 0.0
    
    # Run the text through the pipeline
    predictions = toxicity_analyzer(text)[0]
    
    # toxic-bert flags specific labels like 'toxic', 'insult', etc.
    # If it predicts a toxic label with confidence, return the score.
    if predictions['label'].lower() != 'clean' and predictions['score'] > 0.5:
        return predictions['score']
        
    return 0.0
def safety_classifier(text_input: str) -> dict:
    """
    Main gateway function for safety evaluation.
    Evaluates text and returns the strictly structured risk schema dictionary.
    """
    flagged = False
    categories = []
    severity = "LOW"
    confidence = 1.0  # Default high confidence for clean text
    action = "allow"
    
    # 1. Evaluate Jailbreak Threats
    if detect_jailbreak(text_input):
        flagged = True
        categories.append("jailbreak")
        severity = "HIGH"
        confidence = 0.95
        action = "block"
        
    # 2. Evaluate PII Data
    pii_found = detect_pii(text_input)
    if pii_found:
        flagged = True
        categories.extend(pii_found)
        if severity != "HIGH": 
            severity = "MEDIUM"
            confidence = 0.90
            action = "block"

    # 3. Evaluate Toxicity
    toxicity_score = get_toxicity_score(text_input)
    if toxicity_score > 0.6:  # Flag if toxicity confidence crosses 60%
        flagged = True
        categories.append("toxicity")
        if toxicity_score > 0.85:
            severity = "HIGH"
            action = "block"
        elif severity != "HIGH":
            severity = "MEDIUM"
            action = "block"
        confidence = max(confidence, round(toxicity_score, 2)) if confidence != 1.0 else round(toxicity_score, 2)

    return {
        "flagged": flagged,
        "categories": categories,
        "severity": severity,
        "confidence": confidence,
        "action": action
    }

