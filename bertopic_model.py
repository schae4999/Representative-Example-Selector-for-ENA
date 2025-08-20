import pandas as pd
import numpy as np
import csv

from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer

from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance, PartOfSpeech

def column_to_list(csv_file: str, column_index: int):
    """
    Extract a column from CSV file as a list.
    """
    data = []
    with open(csv_file, 'r', newline='', encoding="cp1252") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > column_index:
                data.append(row[column_index])

    return data

def load_connection_data(csv_file, column_index):
    """
    Load code pair column.
    """
    docs_clo = column_to_list(csv_file, column_index)
    del docs_clo[0] # removes the first item (column header)
    docs_clo = list(filter(None, docs_clo))
    
    return docs_clo

def create_model():
    """
    Create BERTopic model.
    """
    # 1. Extract embeddings
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    # 2. Reduce dimensionality
    pca_model = PCA(n_components=30) # reduces down to 30 dimensions

    # 3. Cluster reduced embeddings
    hdbscan_model = HDBSCAN(min_cluster_size=4, metric='euclidean', prediction_data=True)

    # 4. Tokenize topics
    vectorizer_model = CountVectorizer(stop_words="english")

    # 5. Create topic representations
    ctfidf_model = ClassTfidfTransformer()

    # 6. Fine-tune representations
    key_representation_model = MaximalMarginalRelevance()

    # Create model
    topic_model = BERTopic(
        embedding_model = embedding_model,
        umap_model = pca_model,
        hdbscan_model = hdbscan_model,
        vectorizer_model = vectorizer_model,
        ctfidf_model = ctfidf_model,
        representation_model = key_representation_model,
        calculate_probabilities = True
    )

    return topic_model

def fit_transform():
    """
    Load data and fit the model.
    """
    docs_clo = load_connection_data()
    topics, probs = create_model().fit_transform(docs_clo)
    return topics, probs, docs_clo

class PerformanceTechnicalAnalyzer:
    """
    BERTopic analyzer specifically for Performance.Parameters_Technical.Constraints
    """

    def __init__(self):
        self.model = None
        self.topics = None
        self.probs = None
        self.docs = None

    def fit_transform(self):
        self.docs = load_connection_data("ref_pipe_paired_code_occurrences.csv", 7)
        self.model = create_model()
        self.topics, self.probs = self.model.fit_transform(self.docs)

        return self.topics, self.probs # list of topic assignments, probability scores for the topic assignments
