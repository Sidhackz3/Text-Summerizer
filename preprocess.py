# preprocess.py
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

_stopwords = set(stopwords.words('english'))
_lemmatizer = WordNetLemmatizer()

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)            # collapse whitespace
    text = re.sub(r'\[[0-9]*\]', '', text)      # remove references like [1]
    return text.strip()

def split_sentences(text: str):
    text = clean_text(text)
    sentences = sent_tokenize(text)
    return [s.strip() for s in sentences if s.strip()]

def tokenize_for_vector(text: str):
    tokens = word_tokenize(text)
    tokens = [t.lower() for t in tokens if t.isalpha()]
    tokens = [t for t in tokens if t not in _stopwords]
    tokens = [_lemmatizer.lemmatize(t) for t in tokens]
    return tokens
