"""Utility functions for Speech Agent analysis."""
import re
from typing import Dict, List, Tuple
from collections import Counter

FILLER_WORDS = {'um', 'uh', 'like', 'you know', 'basically', 'literally', 'so yeah', 'i mean'}

def _clean_text(text: str) -> str:
    """Clean text by removing punctuation and lowercasing."""
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text

def count_filler_words(transcript: str) -> Tuple[Dict[str, int], int]:
    """
    Count the occurrences of filler words in the transcript.
    
    Args:
        transcript: The interview transcript text.
        
    Returns:
        A tuple containing a dictionary of filler word counts and the total filler count.
    """
    counts = {filler: 0 for filler in FILLER_WORDS}
    total = 0
    
    text = transcript.lower()
    
    # Handle multi-word fillers first
    for filler in ['you know', 'so yeah', 'i mean']:
        count = len(re.findall(rf'\b{filler}\b', text))
        if count > 0:
            counts[filler] = count
            total += count
            # Remove them so we don't double count parts
            text = text.replace(filler, '')
            
    # Handle single word fillers
    words = _clean_text(text).split()
    word_counts = Counter(words)
    
    for filler in ['um', 'uh', 'like', 'basically', 'literally']:
        if filler in word_counts:
            counts[filler] = word_counts[filler]
            total += word_counts[filler]
            
    # Filter out zero counts
    counts = {k: v for k, v in counts.items() if v > 0}
    
    return counts, total

def calculate_speaking_pace(word_count: int, duration_seconds: int) -> float:
    """
    Calculate the speaking pace in words per minute (WPM).
    
    Args:
        word_count: Total number of words.
        duration_seconds: Total duration of speech in seconds.
        
    Returns:
        Words per minute as a float.
    """
    if duration_seconds <= 0:
        return 0.0
    minutes = duration_seconds / 60.0
    return round(word_count / minutes, 2)

def vocabulary_diversity(transcript: str) -> float:
    """
    Calculate the Type-Token Ratio (TTR) as a measure of vocabulary diversity.
    TTR = (number of unique words) / (total number of words)
    
    Args:
        transcript: The interview transcript text.
        
    Returns:
        The TTR as a float between 0 and 1.
    """
    words = _clean_text(transcript).split()
    total_words = len(words)
    
    if total_words == 0:
        return 0.0
        
    unique_words = len(set(words))
    return round(unique_words / total_words, 4)
