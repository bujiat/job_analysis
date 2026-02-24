"""
Text preprocessing for IR: tokenize, remove stop words, stem.
Uses NLTK (tokenization, stopwords, Porter stemmer). Same pipeline for documents and queries.
"""
from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

_STEMMER = PorterStemmer()
_STOP_WORDS = set(stopwords.words("english"))


def _tokenize(text: str) -> List[str]:
    """Lowercase, tokenize (NLTK), keep alphabetic tokens only."""
    if not text or not isinstance(text, str):
        return []
    tokens = word_tokenize(text.lower())
    return [t for t in tokens if t.isalpha()]


def _remove_stop_words(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in _STOP_WORDS]


def _stem(tokens: List[str]) -> List[str]:
    return [_STEMMER.stem(t) for t in tokens]


def preprocess_text(text: str) -> List[str]:
    """Pipeline: tokenize → remove stop words → stem. Returns list of terms."""
    tokens = _tokenize(text)
    tokens = _remove_stop_words(tokens)
    return _stem(tokens)
