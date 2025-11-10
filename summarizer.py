# summarizer.py (improved NLP-based summarizer)
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk import pos_tag, word_tokenize
from preprocess import split_sentences, clean_text

nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('punkt', quiet=True)

# ---------- Helper for keyword extraction ----------
def extract_keywords(text, top_n=5):
    words = word_tokenize(text)
    tagged = pos_tag(words)
    nouns = [w for w, t in tagged if t.startswith('NN')]
    freq = nltk.FreqDist(nouns)
    top_nouns = [word.capitalize() for word, _ in freq.most_common(top_n)]
    return " ".join(top_nouns) if top_nouns else "Summary"

# ---------- Improved TextRank ----------
def summarize_textrank(text, num_sentences=3):
    sentences = split_sentences(text)
    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(sentences)
    sim_matrix = cosine_similarity(X)

    nx_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(nx_graph, max_iter=300)
    ranked = sorted(((scores[i], i, s) for i, s in enumerate(sentences)), reverse=True)
    selected = sorted([i for _, i, _ in ranked[:num_sentences]])

    summary = " ".join([sentences[i] for i in selected])
    return summary

# ---------- TF-IDF Weighted Frequency Summarizer ----------
def summarize_tfidf(text, num_sentences=3):
    sentences = split_sentences(text)
    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(sentences)
    scores = X.sum(axis=1).A1
    ranked_idx = np.argsort(scores)[-num_sentences:]
    ranked_idx.sort()

    summary = " ".join([sentences[i] for i in ranked_idx])
    return summary

# ---------- Frequency-based NLP Summarizer (New Add-On) ----------
def summarize_frequency(text, num_sentences=3):
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))

    sentences = split_sentences(text)
    words = word_tokenize(text.lower())
    freq_table = {}
    for word in words:
        if word.isalpha() and word not in stop_words:
            freq_table[word] = freq_table.get(word, 0) + 1

    sentence_scores = {}
    for sent in sentences:
        for word, freq in freq_table.items():
            if word in sent.lower():
                sentence_scores[sent] = sentence_scores.get(sent, 0) + freq

    ranked_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    summary = " ".join(ranked_sentences[:num_sentences])
    return summary

# ---------- Title Generator ----------
def suggest_title(text):
    tfidf = TfidfVectorizer(stop_words='english', max_features=100)
    X = tfidf.fit_transform([text])
    top_terms = np.array(tfidf.get_feature_names_out())[np.argsort(X.toarray()).flatten()[::-1][:5]]
    keyword_title = " ".join([w.capitalize() for w in top_terms])
    phrase_title = extract_keywords(text, top_n=3)
    return phrase_title or keyword_title or "Summary"

# ---------- Main Function ----------
def generate_summary_and_title(text, num_sentences=3, method='textrank'):
    if not text.strip():
        return "", "No Content"
    
    text = clean_text(text)
    if method == 'tfidf':
        summary = summarize_tfidf(text, num_sentences)
    elif method == 'frequency':
        summary = summarize_frequency(text, num_sentences)
    else:
        summary = summarize_textrank(text, num_sentences)
    
    title = suggest_title(summary if summary else text)
    return summary, title
