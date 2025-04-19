import re

def clean_text(text):
    """Clean and preprocess scraped text."""
    text = re.sub(r"<[^>]*?>", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^\w\s.,!?]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()
