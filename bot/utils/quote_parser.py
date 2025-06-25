"""Simple and reliable quote parser for bot commands."""

import re
from typing import List

def extract_quoted_strings(text: str) -> List[str]:
    """
    Extract all quoted strings from text, preserving duplicates and order.
    Normalizes all quote types to standard quotes first.
    
    Args:
        text (str): Input text containing quoted strings
        
    Returns:
        List[str]: List of extracted strings (without quotes), preserving all instances
    """
    if not text:
        return []
    
    text = text.strip()
    
    # NORMALIZE: Replace all curly quotes with standard quotes using Unicode
    text = text.replace('\u201C', '"')  # Left curly quote (") → standard quote
    text = text.replace('\u201D', '"')  # Right curly quote (") → standard quote
    
    # Now use simple regex for standard quotes only
    matches = re.findall(r'"([^"]*)"', text)
    
    # Return all matches, preserving duplicates and order
    return [match.strip() for match in matches]

def has_unquoted_text(text: str) -> bool:
    """
    Check if there's meaningful text outside of quotes.
    
    Args:
        text (str): Input text to check
        
    Returns:
        bool: True if there's text outside quotes
    """
    if not text or not text.strip():
        return False
    
    # Normalize quotes first using Unicode
    normalized = text.replace('\u201C', '"').replace('\u201D', '"')
    
    # Remove all quoted content
    cleaned = re.sub(r'"[^"]*"', '', normalized)
    
    # Check if anything meaningful remains
    remaining = re.sub(r'[^\w]', '', cleaned.strip())
    return len(remaining) > 0