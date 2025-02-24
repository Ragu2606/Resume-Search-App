# Flask Resume Search Application

## Overview
This is a Flask-based Resume Search Application that allows users to search for resumes based on a given query. The application extracts text from PDF resumes, applies TF-IDF vectorization for similarity search, and generates concise summaries using the Together AI API.

## Features
- Extracts text from PDF resumes (limited to 3 pages).
- Uses TF-IDF and cosine similarity to match resumes against user queries.
- Integrates Together AI for summarizing resumes.
- Displays matched resumes with relevance scores.
- Provides a PDF viewing option for selected resumes.
- Logs search activity and processing details.

## Prerequisites
Before running the application, ensure you have:
- Python 3.7+
- Flask
- Required Python libraries (see Installation section)
- Together AI API Key

## Installation

### 1. Clone the Repository
```sh
 git clone https://github.com/yourusername/flask-resume-search.git
 cd flask-resume-search
```

### 2. Install Dependencies
Create a virtual environment (optional but recommended):
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

Install required libraries:
```sh
pip install -r requirements.txt
```

### 3. Configure API Key
Replace `TOGETHER_AI_API_KEY` in `app.py` with your valid API key from [Together AI](https://together.ai/).

### 4. Create Resumes Directory
```sh
mkdir resumes
```
Place PDF resumes in the `resumes/` folder.

## Running the Application
```sh
python app.py
```
The app runs on `http://127.0.0.1:5000/` by default.

## API Endpoints

### 1. Home Page
- **Endpoint:** `/`
- **Method:** GET
- **Description:** Renders the search page.

### 2. Search Resumes
- **Endpoint:** `/search`
- **Method:** POST
- **Parameters:** `query` (search term)
- **Response:** JSON containing matched resumes with scores and summaries.

### 3. View Resume
- **Endpoint:** `/view/<filename>`
- **Method:** GET
- **Description:** Serves a PDF resume.

## Deployment
### Deploy on AWS EC2
1. Launch an EC2 instance (Ubuntu recommended).
2. Install Python, Flask, and dependencies.
3. Configure API key and upload resumes.
4. Run the app with:
```sh
python app.py
```
5. Set up an Nginx reverse proxy for production use.

### Deploy on Docker
1. Build the Docker image:
```sh
docker build -t flask-resume-app .
```
2. Run the container:
```sh
docker run -p 5000:5000 flask-resume-app
```

## Logging
- Logs are stored in `app.log`.
- Logs include search queries, resume processing status, and API errors.

## Contributing
Pull requests are welcome! Feel free to improve search accuracy, enhance the UI, or integrate additional AI models.

## License
This project is open-source under the MIT License.

