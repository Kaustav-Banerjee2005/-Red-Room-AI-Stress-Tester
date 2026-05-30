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
