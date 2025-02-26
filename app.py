from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
import fitz
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

app = Flask(__name__)

# Configuration
class Config:
    RESUME_DIR = "resumes/"
    MAX_PAGES = 3
    LOG_FILE = "app.log"
    SCORE_THRESHOLD = 0.1
    TOGETHER_AI_API_KEY = "Replace with your API key"
    TOGETHER_AI_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

# Setup logging
logging.basicConfig(
    filename=Config.LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

@lru_cache(maxsize=100)
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    logger.info(f"Processing: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
        if doc.page_count > Config.MAX_PAGES:
            logger.warning(f"Skipping {pdf_path}: Exceeds {Config.MAX_PAGES} pages")
            return None
        text = "".join(page.get_text() or "" for page in doc)
        logger.info(f"Extracted text from: {pdf_path}")
        return text
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {str(e)}")
        return None

@lru_cache(maxsize=500)
def generate_summary_cached(text, query):
    """Generate a summary using Together AI API and cache results."""
    logger.info(f"Generating summary for query: {query}")
    headers = {"Authorization": f"Bearer {Config.TOGETHER_AI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": Config.TOGETHER_AI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a recruiter. Provide a concise summary (150 words)."},
            {"role": "user", "content": f"Summarize this resume based on: {query}\n{text[:2000]}"}
        ],
        "max_tokens": 150
    }
    
    try:
        response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        summary = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Summary not available.")
        logger.info(f"Summary generated successfully for query: {query}")
        return summary
    except Exception as e:
        logger.error(f"Together AI API failed: {str(e)}")
        return "Summary unavailable due to processing error."

@app.route("/", methods=["GET"])
def index():
    """Render the index page."""
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    """Search and summarize resumes based on query."""
    query = request.form.get("query", "").strip()
    logger.info(f"Received search request: {query}")

    if not query:
        logger.warning("Empty query received")
        return jsonify({"error": "Query is required"}), 400

    resume_data = {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(extract_text_from_pdf, os.path.join(Config.RESUME_DIR, f)): f
            for f in os.listdir(Config.RESUME_DIR) if f.lower().endswith(".pdf")
        }
        for future in futures:
            filename = futures[future]
            text = future.result()
            if text and filename not in resume_data:
                resume_data[filename] = text

    if not resume_data:
        logger.warning("No resumes found or extracted")
        return jsonify({"results": []})  # ✅ Return empty JSON array instead of rendering HTML

    logger.info("Vectorizing resumes and searching for matches...")
    vectorizer = TfidfVectorizer(stop_words="english")
    doc_vectors = vectorizer.fit_transform(resume_data.values())

    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, doc_vectors)[0]

    results = []
    seen_resumes = set()
    for idx, (filename, text) in enumerate(resume_data.items()):
        score = scores[idx]
        logger.info(f"Score for {filename}: {score:.2f}")

        if score > Config.SCORE_THRESHOLD and filename not in seen_resumes:
            seen_resumes.add(filename)
            summary = generate_summary_cached(text, query)  # ✅ Cached summary
            results.append({
                "filename": filename,
                "score": round(score * 100, 2),
                "summary": summary,
                "preview": text[:200]
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    logger.info(f"Returning {len(results)} matching results.")

    return jsonify({"results": results})  # ✅ Always return JSON

@app.route("/view/<filename>", methods=["GET"])
def view_resume(filename):
    """Serve a resume PDF for viewing."""
    file_path = os.path.join(Config.RESUME_DIR, filename)
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {filename}")
        return "Resume not found", 404
    logger.info(f"Serving file: {filename}")
    return send_from_directory(Config.RESUME_DIR, filename, mimetype="application/pdf")

if __name__ == "__main__":
    os.makedirs(Config.RESUME_DIR, exist_ok=True)
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)
