# Acasamix - AI Powered Notes Generator & Study Assistant

This application provides an AI-powered study assistant for both students and tutors. It uses RAG (Retrieval Augmented Generation) to process PDFs and generate structured notes and other study materials.

## Features

### For All Users
- **User Authentication**: Register and login with role-based access (student or tutor)
- **PDF Upload & Notes Generation**: Upload PDFs and generate comprehensive study notes
- **Topic-based Notes Generation**: Get notes on specific topics from your uploaded documents
- **Book Suggestions**: Get book recommendations based on uploaded syllabus

### For Tutors (Additional Features)
- **MCQ Preparation**: Generate multiple-choice questions with answers and explanations

## Setup Instructions

### Prerequisites
- Python 3.8+
- Tesseract OCR installed on your system ([Installation Guide](https://github.com/tesseract-ocr/tesseract))
- Groq API Key
- AWS Access Key and Secret Key (for AWS Bedrock Titan Embeddings)

### Installation

1. Clone the repository:
```
git clone [repository-url]
cd ai-study-assistant
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
streamlit run app.py
```

4. Access the application in your web browser at `http://localhost:8501`

## Usage

1. Register for an account as either a student or tutor
2. Log in with your credentials
3. Configure your API keys in the "API Configuration" section
4. Use the various tabs to access different features:
   - Upload PDFs and generate notes
   - Generate topic-specific notes
   - Get book suggestions
   - Create MCQs (tutors only)

## Technologies Used

- **Frontend**: Streamlit
- **LLM**: Groq's API (using Llama3 70B model)
- **Vector DB**: FAISS
- **Embeddings**: AWS Titan (Bedrock)
- **Database**: SQLite
- **PDF Processing**: pdf2image & pytesseract

## Project Structure

- `app.py`: Main application code
- `study_assistant.db`: SQLite database for user data, notes, and MCQs
- `vector_store/`: Directory storing FAISS indexes and metadata
- `requirements.txt`: Required Python packages
