import os
import fitz  # PyMuPDF for PDF processing
import faiss
import torch
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import re
from collections import Counter
import numpy as np

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# Load models (Force CPU usage)
device = "cpu"
model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)

# User credentials (Hardcoded for now)
users = {"admin": generate_password_hash("password123")}

# Function to extract text from a PDF (reads the full document)
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([doc[i].get_text("text") for i in range(len(doc))])  # Read all pages
    return text.strip()

# Function to summarize text
def summarize_text(text, max_length=150):
    if len(text.split()) > 50:
        chunks = split_text_into_chunks(text, max_tokens=500)  # Avoiding long input error
        summarized_chunks = [summarizer(chunk, max_length=max_length, min_length=50, do_sample=False)[0]['summary_text'] for chunk in chunks]
        return " ".join(summarized_chunks)
    return text[:500]

# Function to split text into smaller chunks (avoiding model token limit)
def split_text_into_chunks(text, max_tokens=500):
    words = text.split()
    return [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]

# Function to load resumes from a directory
def load_resumes(folder_path):
    resume_texts, resume_links = [], []
    if not os.path.exists(folder_path):
        print("Resume folder not found!")
        return [], []
    
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file)
            text = extract_text_from_pdf(pdf_path)
            if text:
                summary = summarize_text(text)
                resume_texts.append((file, text, summary))
                resume_links.append(file)  # Store file name for direct access
    print(f"Loaded {len(resume_texts)} resumes")  # Debugging
    return resume_texts, resume_links

# Function to create FAISS index (handles full resumes)
def create_faiss_index(resume_texts):
    if not resume_texts:
        return None, None

    resume_embeddings = []
    
    for file, full_text, summary in resume_texts:
        chunks = split_text_into_chunks(full_text)  # Split text into chunks
        chunk_embeddings = model.encode(chunks, convert_to_numpy=True)  # Convert directly to NumPy
        avg_embedding = np.mean(chunk_embeddings, axis=0)  # Average the embeddings
        
        resume_embeddings.append(avg_embedding)

    resume_embeddings = np.stack(resume_embeddings)
    d = resume_embeddings.shape[1]  # Dimension of embeddings
    index = faiss.IndexFlatL2(d)
    index.add(resume_embeddings)
    
    print(f"FAISS index created with {len(resume_texts)} resumes")  # Debugging
    return index, resume_embeddings

# Function to authenticate a user
def authenticate_user(username, password):
    return username in users and check_password_hash(users[username], password)

# Function to calculate keyword relevance
def keyword_match_score(query, resume_text):
    query_words = set(re.findall(r'\b\w+\b', query.lower()))  # Extract words from query
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))  # Extract words from resume

    common_words = query_words.intersection(resume_words)  # Find common words
    keyword_score = (len(common_words) / len(query_words)) * 100 if query_words else 0  # Normalize to 100

    return round(keyword_score, 2)

# Function to search resumes with improved scoring
def search_resumes(query, index, resume_texts, embeddings, resume_links, top_k=5):
    if index is None or embeddings is None:
        return []

    query_embedding = model.encode(query, convert_to_numpy=True).reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)

    seen_files = set()  # Avoid duplicates
    results = []
    max_distance = max(distances[0]) if len(distances[0]) > 0 else 1.0  # Avoid division by zero

    for idx, score in zip(indices[0], distances[0]):
        if idx < 0 or idx >= len(resume_texts):
            continue  # Ignore invalid indices

        file_name = resume_texts[idx][0]
        resume_text = resume_texts[idx][1]

        if file_name not in seen_files:
            seen_files.add(file_name)

            # FAISS similarity score (normalized)
            faiss_score = 100 - (float(score) / float(max_distance) * 100)

            # Keyword-based score
            keyword_score = keyword_match_score(query, resume_text)

            # Weighted score (70% FAISS + 30% keyword match)
            final_score = round((0.7 * faiss_score) + (0.3 * keyword_score), 2)

            results.append({
                "file": file_name,
                "summary": resume_texts[idx][2],
                "match_score": final_score,
                "link": file_name  # Updated to only include the filename
            })

    print(f"Found {len(results)} matching resumes")  # Debugging
    return results

# Home route
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if authenticate_user(username, password):
            session['user'] = username
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Resume search API
@app.route('/search', methods=['POST'])
def search():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"message": "Query is required"}), 400
    
    folder_path = "./resumes"
    resume_texts, resume_links = load_resumes(folder_path)
    index, embeddings = create_faiss_index(resume_texts)
    results = search_resumes(query, index, resume_texts, embeddings, resume_links)
    
    return jsonify(results)

@app.route('/resumes/<path:filename>')
def serve_resume(filename):
    resume_folder = './resumes'
    # Sanitize the filename to avoid malicious paths
    sanitized_filename = os.path.basename(filename)
    
    # Check if the file exists
    file_path = os.path.join(resume_folder, sanitized_filename)
    if os.path.exists(file_path):
        return send_from_directory(resume_folder, sanitized_filename)
    else:
        abort(404)

if __name__ == "__main__":
    app.run(debug=True)
