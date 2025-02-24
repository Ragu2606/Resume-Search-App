# Resume Search Application

This is a Flask-based web application for searching and summarizing resumes using Natural Language Processing (NLP). The application extracts text from PDF resumes, indexes them using TF-IDF vectorization, and allows users to search for relevant resumes based on a given query.

## Features
- Upload and store PDF resumes in the `resumes/` directory.
- Extract text from PDF resumes using PyMuPDF.
- Vectorize and search resumes using TF-IDF and cosine similarity.
- Generate summaries using Together AI API.
- View resumes directly in the browser.

## Technologies Used
- **Flask** - Web framework
- **Scikit-learn** - TF-IDF vectorization & cosine similarity
- **PyMuPDF (fitz)** - PDF text extraction
- **Concurrent.futures** - Multi-threaded processing
- **Together AI API** - Resume summarization
- **Logging** - Application logging for debugging and monitoring

## Installation & Setup

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- pip (Python package manager)

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/resume-search-app.git
   cd resume-search-app
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (if needed):**
   - Configure `TOGETHER_AI_API_KEY` in `Config` class inside `app.py`.

5. **Create `resumes/` directory:**
   ```bash
   mkdir resumes
   ```

6. **Run the application:**
   ```bash
   python app.py
   ```
   The application will start on `http://127.0.0.1:5000/`.

## Usage
1. Open `http://127.0.0.1:5000/` in your browser.
2. Enter search queries based on skills, experience, etc.
3. The application will return matching resumes along with their summaries.
4. Click "View Resume" to open the full resume PDF.

## API Endpoints
- `GET /` - Homepage with search functionality.
- `POST /search` - Search for resumes based on a query.
- `GET /view/<filename>` - View a specific resume PDF.

## Deployment
To deploy on a server, you can use **Gunicorn**:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
Alternatively, you can deploy using **Docker**:
```bash
docker build -t resume-search-app .
docker run -p 5000:5000 resume-search-app
```

## Logs
Application logs are stored in `app.log`. You can monitor logs using:
```bash
tail -f app.log
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss the proposed changes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Together AI for text summarization API
- Scikit-learn for NLP processing
- Flask for web development
