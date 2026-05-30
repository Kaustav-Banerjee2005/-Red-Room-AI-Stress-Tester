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