# Resume Search Application

This is a simple resume search application built using Flask, FAISS, and other Python libraries. The app allows users to search through a set of resumes (in PDF format) and view detailed information about the resumes that match their search query.

## Features

- **User Authentication**: Secure login to access the resume search.
- **Resume Search**: Search resumes based on keywords. The search is enhanced by both semantic and keyword-based matching.
- **PDF Viewer**: View resumes directly in the browser using an embedded PDF viewer.
- **Summarization**: Each resume is automatically summarized to provide a brief overview.

## Technologies Used

- **Flask**: A Python web framework for building the app.
- **PyMuPDF**: For extracting text from PDF files.
- **Sentence Transformers**: For converting text into embeddings and performing semantic search.
- **FAISS**: For efficient similarity search and clustering of resume embeddings.
- **Hugging Face Transformers**: For text summarization.

## Installation

1. Clone this repository:
   ```bash
   git clone [https://github.com/Ragu2606/Resume-Search-App]
2. Navigate to the project folder:
   cd resume-search-app
3. Create and activate a virtual environment:
    For Windows
   python -m venv venv
   venv\Scripts\activate
4. Install required dependencies:
   pip install -r requirements.txt
   
## Running the Application
  To start the Flask app, run the following command:
  python app.py
  This will start the Flask development server, typically at http://127.0.0.1:5000/. Open this URL in your browser to use      the application.

## How It Works
    Login: You must log in to access the resume search functionality. The default credentials are:

    Username: admin
    Password: password123
    Search: Enter a keyword in the search bar to find resumes that match your query. The app combines keyword matching with      semantic matching using sentence embeddings.

    View Resume: Click the "View Resume" button to open the resume directly in the browser.
## Output
    When a search is performed, the app returns a list of resumes that match the query. Each search result includes:

    File Name: The name of the resume file (e.g., John_Doe_Resume.pdf).
    Match Score: A percentage that indicates how closely the resume matches the search query. This score is calculated using     a combination of semantic search and keyword matching.
    Summary: A brief summary of the resume, generated using the Hugging Face summarization pipeline.
    View Resume Button: A button that allows users to view the full resume in an embedded PDF viewer.
