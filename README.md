<h1 align="center">Representative Example Selector for Epistemic Network Analysis (ENA)</h1>

<p align="center">
  <b>An interactive Shiny for Python application for exploring <i>representative qualitative excerpts</i> behind ENA code pair connections using <i>BERTopic</i>.</b>
</p>

---

## 🔎 Overview

The **Representative ENA Example Selector** enables researchers to inspect the *actual discourse* underlying ENA connections.  
Given a specific **ENA code pair**, the app:

- Loads corresponding text segments from a CSV file  
- Uses **BERTopic** (embeddings → PCA → HDBSCAN → topic representation) to cluster excerpts into coherent topics  
- Provides two levels of interactive filtering:
  1. **Selector #1 — Choose a code pair**  
  2. **Selector #2 — Choose a topic** to view representative documents  
- Visualizes:
  - A **topic distribution bar chart**  
  - A **document panel** showing representative excerpts for any selected topic  

This tool supports:
- Selecting relevant qualitative examples for papers or reports
- Interpreting high-frequency ENA connections  
- Understanding the semantic diversity within a single code pair  

---

## ⭐️ Main Components

### 1. BERTopic Model

This module manages data extraction and topic modeling.

#### **Data Loading**
- Extracts a single column from a CSV file containing text associated with an ENA code pair
- Removes the header and filters out empty rows
- Returns a cleaned list of sentences

#### **Model Construction**
BERTopic is created with:

- **SentenceTransformer** — sentence embeddings  
- **PCA(n_components=30)** — dimensionality reduction  
- **HDBSCAN(min_cluster_size=4)** — clustering  
- **CountVectorizer(stop_words="english")** — tokenization  
- **ClassTfidfTransformer()** and **MaximalMarginalRelevance()** — topic representations  

#### **Model Fitting**
The analyzer:
- Loads text from the specified CSV column
- Fits BERTopic on all excerpts
- Stores:
  - Raw documents
  - Topic assignments
  - Topic probabilities
  - The fitted BERTopic model

---

## 2. Shiny App (UI + Server)

The Shiny for Python application provides an interactive interface for exploring topics and their representative excerpts.

### **UI Components**
- **Selector #1 — Code Pair Selector**  
  Choose which ENA code pair column to examine  
- **Selector #2 — Topic Selector**  
  Choose a BERTopic topic cluster to view its representative excerpts
- **Plot Card**  
  Displays topic distribution using Plotly  
- **Document Card**  
  Shows representative examples for the selected topic

### **Server Logic**
- Auto-runs BERTopic fitting on start  
- Populates topic dropdown after fitting  
- Updates selected topic and document display  
- Handles Plotly rendering and UI updates

---

## 📄 Expected Data Format

The app expects a CSV file with at least one column containing text excerpts associated with ENA code pairs.

Requirements:
- First row is a **header**
- The column for the chosen code pair contains text
- Empty cells are removed

Example structure:

| col0 | col1 | col2 | … | **col7** |
|------|------|------|----|----------|
| ID   | …    | …    | …  | *Text for selected code pair* |

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/schae4999/Representative-Example-Selector-for-ENA.git
cd Representative-Example-Selector-for-ENA
```

### 2. Install dependencies
```bash
pip install \
  shiny \
  shiny-express \
  plotly \
  pandas \
  numpy \
  sentence-transformers \
  scikit-learn \
  hdbscan \
  bertopic \
  faicons
```

### 3. Run the application
```bash
shiny run app.py
```
