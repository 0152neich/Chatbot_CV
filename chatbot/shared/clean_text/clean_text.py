import re

class TextCleaner:
    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """Clean the text by removing extra spaces, newlines, and specific patterns.
        
        Args:
            text (str): Text to clean.
        
        Returns:
            str: Cleaned text.
        """
        text = re.sub(r"^\s*[-*]\s*", "", text, flags=re.MULTILINE)
        text = text.replace("*", "")
        text = re.sub(r"\s+", " ", text)

        return text.strip()
