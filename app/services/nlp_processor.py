import re
from typing import Dict, List, Set

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

_NLTK_READY = False


def _ensure_nltk_resources() -> None:
    global _NLTK_READY
    if _NLTK_READY:
        return

    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
    ]

    for path_name, download_name in resources:
        try:
            nltk.data.find(path_name)
        except LookupError:
            nltk.download(download_name, quiet=True)

    _NLTK_READY = True


def preprocess_text(raw_text: str) -> Dict[str, List[str] | Set[str] | str]:
    _ensure_nltk_resources()

    normalized = raw_text.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()

    tokens = word_tokenize(normalized)
    filtered_tokens = [token for token in tokens if token not in stop_words and not token.isdigit()]
    lemmas = [lemmatizer.lemmatize(token) for token in filtered_tokens]

    return {
        "normalized_text": " ".join(lemmas),
        "tokens": lemmas,
        "token_set": set(lemmas),
    }
