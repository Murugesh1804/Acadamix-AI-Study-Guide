import streamlit as st
import os
import sqlite3
import hashlib
import uuid
import time
from PIL import Image
import io
import json
import faiss
import numpy as np
import groq
import boto3
from io import BytesIO
import tempfile
import PyPDF2
import requests

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = None

# Set page configuration
st.set_page_config(
    page_title="Acadamix",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for modern UI with light red theme
st.markdown("""
<style>
/* Main container styling */
.stApp {
    background-color: #fff5f5;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ff6b6b 0%, #d63031 100%);
    color: white;
}

/* Button styling */
.stButton>button {
    background: #ff6b6b !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 10px 24px !important;
    border: none !important;
    transition: all 0.3s ease !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(255, 107, 107, 0.2) !important;
}

.stButton>button:hover {
    background: #d63031 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(255, 107, 107, 0.3) !important;
}

/* Input fields styling */
.stTextInput>div>div>input,
.stTextInput>div>div>input:focus {
    border-radius: 12px !important;
    border: 2px solid rgba(255, 107, 107, 0.2) !important;
    padding: 12px !important;
    box-shadow: none !important;
    transition: all 0.3s ease !important;
}

.stTextInput>div>div>input:focus {
    border-color: #ff6b6b !important;
    box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.1) !important;
}

/* File uploader styling */
.stFileUploader {
    border: 2px dashed #ff6b6b !important;
    border-radius: 16px !important;
    background: rgba(255, 107, 107, 0.05) !important;
    padding: 24px !important;
    transition: all 0.3s ease !important;
}

.stFileUploader:hover {
    background: rgba(255, 107, 107, 0.08) !important;
}

/* Tab styling */
[data-baseweb="tab-list"] {
    gap: 12px !important;
    background: transparent !important;
    border-bottom: 2px solid rgba(255, 107, 107, 0.2) !important;
    padding-bottom: 8px !important;
}

[data-baseweb="tab"] {
    background: white !important;
    border-radius: 12px 12px 0 0 !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
    margin: 5px 0 !important;
    border: 2px solid rgba(255, 107, 107, 0.1) !important;
    border-bottom: none !important;
}

[data-baseweb="tab"]:hover {
    background: #fff0f0 !important;
}

[aria-selected="true"] {
    background: #ff6b6b !important;
    color: white !important;
    border-color: #ff6b6b !important;
}

/* Card styling */
.card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 8px 24px rgba(255, 107, 107, 0.08);
    border-left: 4px solid #ff6b6b;
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 12px 32px rgba(255, 107, 107, 0.12);
    transform: translateY(-2px);
}

/* Success messages */
.stSuccess {
    border-radius: 12px !important;
    background: #e8f5e9 !important;
    border-left: 4px solid #4caf50 !important;
}

/* Error messages */
.stError {
    border-radius: 12px !important;
    background: #ffebee !important;
    border-left: 4px solid #f44336 !important;
}

/* Title styling */
.custom-title {
    color: #d63031 !important;
    font-weight: 700 !important;
    margin-bottom: 1.5rem !important;
    position: relative;
    display: inline-block;
}

.custom-title:after {
    content: "";
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 60px;
    height: 4px;
    background: #ff6b6b;
    border-radius: 2px;
}

/* Expander styling */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    color: #d63031 !important;
    background: rgba(255, 107, 107, 0.05) !important;
    border-radius: 12px !important;
}

/* Selectbox styling */
[data-baseweb="select"] {
    border-radius: 12px !important;
}

[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border: 2px solid rgba(255, 107, 107, 0.2) !important;
    transition: all 0.3s ease !important;
}

[data-baseweb="select"] > div:hover {
    border-color: #ff6b6b !important;
}

/* Spinner styling */
.stSpinner > div > div {
    border-top-color: #ff6b6b !important;
}

/* Badge styling */
.badge {
    display: inline-block;
    padding: 4px 12px;
    background: rgba(255, 107, 107, 0.1);
    color: #d63031;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 8px;
}

/* Avatar styling */
.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #ff6b6b;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-right: 12px;
}

/* Button group styling */
.button-group {
    display: flex;
    gap: 10px;
}

/* Progress bar styling */
.stProgress > div > div {
    background-color: #ff6b6b !important;
}

/* Tooltip styling */
.tooltip {
    position: relative;
    display: inline-block;
    cursor: pointer;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 200px;
    background-color: #333;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 8px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    margin-left: -100px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}

/* MCQ styling */
.mcq-question {
    font-weight: 600;
    margin-bottom: 12px;
    color: #333;
}

.mcq-option {
    padding: 10px 16px;
    background: #f8f8f8;
    border-radius: 8px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.mcq-option:hover {
    background: #fff0f0;
}

.mcq-option.correct {
    background: rgba(76, 175, 80, 0.1);
    border-left: 3px solid #4caf50;
}

.mcq-explanation {
    background: rgba(255, 107, 107, 0.05);
    padding: 12px;
    border-radius: 8px;
    margin-top: 12px;
    border-left: 3px solid #ff6b6b;
}

/* Animation for cards */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
    animation: fadeIn 0.5s ease forwards;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 107, 107, 0.5);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #ff6b6b;
}

/* Login form styling */
.login-container {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.05);
}

/* Header styling */
.app-header {
    display: flex;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 2px solid rgba(255, 107, 107, 0.1);
}

.app-logo {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(45deg, #ff6b6b, #d63031);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-right: 12px;
}
</style>
""", unsafe_allow_html=True)

# Initialize database
def init_db():
    conn = sqlite3.connect('study_assistant.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    ''')
    
    # Create notes table
    c.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        pdf_name TEXT,
        vector_data_path TEXT,
        notes_text TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create MCQs table
    c.execute('''
    CREATE TABLE IF NOT EXISTS mcqs (
        id TEXT PRIMARY KEY,
        tutor_id TEXT,
        topic TEXT,
        question TEXT,
        option1 TEXT,
        option2 TEXT,
        option3 TEXT,
        option4 TEXT,
        answer TEXT,
        FOREIGN KEY (tutor_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize FAISS index
def init_faiss(dimension=1024):
    # Create directory for vector storage if it doesn't exist
    if not os.path.exists("vector_store"):
        os.makedirs("vector_store")
    
    # Create index with specified dimension
    index = faiss.IndexFlatL2(dimension)
    return index

# Save embeddings to FAISS index
def save_to_faiss(embedding, pdf_name, user_id):
    # Convert embedding to numpy array
    embedding_np = np.array([embedding]).astype('float32')
    
    # Get dimension from the embedding
    dimension = embedding_np.shape[1]
    
    # Create a new index with the correct dimension
    index = faiss.IndexFlatL2(dimension)
    
    # Add to index
    index.add(embedding_np)
    
    # Save index
    index_path = f"vector_store/{user_id}_{pdf_name.replace(' ', '_')}.index"
    faiss.write_index(index, index_path)
    
    # Save embedding for later use
    embedding_path = f"vector_store/{user_id}_{pdf_name.replace(' ', '_')}.npy"
    np.save(embedding_path, embedding_np)
    
    # Save mapping of index to document
    mapping_path = f"vector_store/{user_id}_{pdf_name.replace(' ', '_')}.json"
    with open(mapping_path, 'w') as f:
        json.dump({"pdf_name": pdf_name, "user_id": user_id, "dimension": int(dimension)}, f)
    
    return index_path

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register new user
def register_user(username, password, role):
    conn = sqlite3.connect('study_assistant.db')
    c = conn.cursor()
    
    # Check if username already exists
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False, "Username already exists!"
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(password)
    
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (user_id, username, hashed_password, role))
    conn.commit()
    conn.close()
    
    return True, "Registration successful!"

# Login user
def login_user(username, password):
    conn = sqlite3.connect('study_assistant.db')
    c = conn.cursor()
    
    # Check credentials
    hashed_password = hash_password(password)
    c.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    
    conn.close()
    
    if user:
        return True, user[0], user[1]
    else:
        return False, None, None

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    # Use PyPDF2 to extract text (no external dependencies needed)
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.getvalue()))
    
    # Extract text from each page
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    
    return text

# Create embeddings using AWS Titan
def create_embeddings(text, aws_access_key, aws_secret_key, aws_region):
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )
    
    # Split text into chunks (max 8000 tokens)
    chunks = [text[i:i+8000] for i in range(0, len(text), 8000)]
    embeddings_list = []
    
    for chunk in chunks:
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=json.dumps({
                'inputText': chunk
            })
        )
        response_body = json.loads(response['body'].read())
        embedding = response_body['embedding']
        embeddings_list.append(embedding)
    
    # Average embeddings if multiple chunks
    if len(embeddings_list) > 1:
        embedding = np.mean(embeddings_list, axis=0)
    else:
        embedding = embeddings_list[0]
    
    return embedding

# Load FAISS index
def load_faiss_index(index_path):
    return faiss.read_index(index_path)

# Generate notes using Groq
def generate_notes(topic, context=""):
    system_prompt = (
        "You are an expert study assistant. Generate structured and concise study notes "
        "covering key concepts, definitions, examples, and practice questions."
    )
    
    # Limit the context to reduce token size
    if context and len(context) > 3000:
        context = context[:3000] + "... [content truncated for token limit]"
    
    user_prompt = f"""
    Generate comprehensive study notes for: {topic}
    
    Requirements:
    - Clear main topics and subtopics
    - Key concepts and definitions
    - Examples where applicable
    - Practice questions
    - Summary points

    Keep the response brief and within 2000 tokens.
    
    {f'Additional Context: {context}' if context else ''}
        Based on the following syllabus or content, recommend 2 relevant textbooks or reference books that would be helpful for studying this material.
    
    Content:
    {topic}
    
    For each book, provide:
    1. Title
    2. Author(s)
    3. A brief description of why it's relevant to the content
    4. The specific topics it covers that align with the content
    
    Format the recommendations in markdown with clear headings and bullet points.
    """
    
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 1500
    }
    GROQ_API_KEY="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"
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response_data = response.json()
        
        # Check for rate limit errors
        if 'error' in response_data and 'code' in response_data['error'] and response_data['error']['code'] == 'rate_limit_exceeded':
            return "The request was too large. Try with a smaller PDF or more focused topic."
            
        return response_data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
    except requests.RequestException as e:
        return f"Failed to fetch response: {str(e)}"

# Generate topic-based notes using Groq and FAISS
def generate_topic_notes(topic,groq_api_key):
    context="Make it detailed and effiecient way to learn"
    """
    Generate well-structured study notes on the given topic using Groq's LLM.
    
    Parameters:
    - topic (str): The topic to generate notes for.
    - context (str): Additional context to refine the notes.
    - groq_api_key (str): API key for Groq's LLM service.
    
    Returns:
    - str: Generated study notes in markdown format.
    """
    if not topic:
        return "Error: Topic is required."
    
    system_prompt = (
        "You are an expert study assistant. Generate structured and concise study notes "
        "covering key concepts, definitions, examples, and practice questions."
    )
    
    user_prompt = f"""
    Generate comprehensive study notes for: {topic}
    
    Requirements:
    - Clear main topics and subtopics
    - Key concepts and definitions
    - Examples where applicable
    - Practice questions
    - Summary points
    
    {f'Additional Context: {context}' if context else ''}
    """
    
    payload = {
        "model": "llama-3.3-70b-specdec",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response_data = response.json()
        output = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
    except requests.RequestException as e:
        return f"Error: Failed to fetch response - {str(e)}"
    
    return output


# Generate book suggestions using Groq
def generate_book_suggestions(text, groq_api_key):
    client = groq.Groq(api_key=groq_api_key)
    
    prompt = f"""
    Based on the following syllabus or content, recommend 5 relevant textbooks or reference books that would be helpful for studying this material.
    
    Content:
    {text}
    
    For each book, provide:
    1. Title
    2. Author(s)
    3. A brief description of why it's relevant to the content
    4. The specific topics it covers that align with the content
    
    Format the recommendations in markdown with clear headings and bullet points.
    """
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
        temperature=0.3,
        max_tokens=1024,
    )
    
    return response.choices[0].message.content

# Generate MCQs using Groq
def generate_mcqs(topic, groq_api_key):
    if not topic:
        return "Topic is required"
    
    prompt = f"""
    Create 5 multiple-choice questions (MCQs) on the topic: "{topic}".
    
    Each MCQ should:
    1. Have a clear question
    2. Have 4 options (labeled a, b, c, d)
    3. Indicate the correct answer
    4. Include a brief explanation of why the answer is correct
    
    Format the MCQs in JSON with the following structure:
    ```json
    [
      {{
        "question": "Question text here?",
        "options": [
          "Option A",
          "Option B",
          "Option C",
          "Option D"
        ],
        "correct_answer": "Option A",
        "explanation": "Explanation why Option A is correct"
      }},
      ...
    ]
    ```
    
    Ensure the questions test different aspects of the topic and vary in difficulty.
    """
    
    payload = {
        "model": "llama-3.3-70b-specdec",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response_data = response.json()
        mcq_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        
        # Parse JSON response
        try:
            mcqs = json.loads(mcq_text.strip("```json").strip("```"))
            return mcqs
        except json.JSONDecodeError:
            return mcq_text
    except requests.RequestException as e:
        return f"Failed to fetch response: {str(e)}"

# Save MCQs to database
def save_mcqs(tutor_id, topic, mcqs):
    conn = sqlite3.connect('study_assistant.db')
    c = conn.cursor()
    
    for mcq in mcqs:
        mcq_id = str(uuid.uuid4())
        c.execute("INSERT INTO mcqs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (mcq_id, tutor_id, topic, mcq['question'],
                  mcq['options'][0], mcq['options'][1], mcq['options'][2], mcq['options'][3],
                  mcq['correct_answer']))
    
    conn.commit()
    conn.close()

# Main function
def main():
    init_db()
    
    # Sidebar with modern design
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0;">
            <h1 style="color: white; font-size: 2.2rem; margin-bottom: 0.5rem;">📚 Acadamix</h1>
            <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">Your AI Study Companion</div>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.logged_in:
            st.markdown("---")
            
            # Login Section
            with st.container():
                st.markdown("""
                <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                    <h3 style="color: white; font-size: 1.2rem; margin-bottom: 12px;">🔑 Login</h3>
                </div>
                """, unsafe_allow_html=True)
                
                login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
                login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Sign In", key="login_btn", use_container_width=True):
                        success, user_id, role = login_user(login_username, login_password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.username = login_username
                            st.session_state.user_id = user_id
                            st.session_state.role = role
                            st.rerun()
                        else:
                            st.error("Invalid credentials!")

            st.markdown("---")
            
            # Registration Section
            with st.container():
                st.markdown("""
                <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                    <h3 style="color: white; font-size: 1.2rem; margin-bottom: 12px;">📝 Register</h3>
                </div>
                """, unsafe_allow_html=True)
                
                reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
                reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Create a password")
                
                st.markdown("""
                <div style="color: rgba(255,255,255,0.8); font-size: 0.85rem; margin-bottom: 10px;">
                    Select your role:
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    student_selected = st.button("👨‍🎓 Student", key="student_btn", use_container_width=True)
                with col2:
                    tutor_selected = st.button("👨‍🏫 Tutor", key="tutor_btn", use_container_width=True)
                
                reg_role = "student" if student_selected else "tutor" if tutor_selected else None
                
                if reg_role and reg_username and reg_password:
                    success, message = register_user(reg_username, reg_password, reg_role)
                    if success:
                        st.success("Account created! Please login")
                    else:
                        st.error(message)
        else:
            # User profile section
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 24px;">
                <div style="width: 60px; height: 60px; background: white; border-radius: 50%; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #ff6b6b; font-weight: bold;">
                    {st.session_state.username[0].upper()}
                </div>
                <div style="font-size: 1.2rem; color: white; margin-bottom: 4px;">{st.session_state.username}</div>
                <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 12px;">{st.session_state.role.capitalize()}</div>
                <div style="background: rgba(255,255,255,0.2); border-radius: 20px; padding: 4px 12px; display: inline-block; font-size: 0.8rem;">
                    Active
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation menu
            st.markdown("""
            <div style="margin-top: 20px;">
                <div style="color: rgba(255,255,255,0.7); font-size: 0.85rem; margin-bottom: 10px; padding-left: 10px;">
                    MAIN MENU
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            menu_items = [
                {"icon": "📄", "label": "PDF & Notes", "active": True},
                {"icon": "📚", "label": "Topic Notes", "active": False},
                {"icon": "📖", "label": "Book Suggestions", "active": False}
            ]
            
            if st.session_state.role == "tutor":
                menu_items.append({"icon": "✍️", "label": "MCQ Generator", "active": False})
            
            for item in menu_items:
                st.markdown(f"""
                <div style="background: {'rgba(255,255,255,0.2)' if item['active'] else 'transparent'}; 
                            border-radius: 12px; 
                            padding: 10px 16px; 
                            margin-bottom: 8px;
                            cursor: pointer;
                            transition: all 0.2s ease;">
                    <div style="display: flex; align-items: center;">
                        <div style="font-size: 1.2rem; margin-right: 12px;">{item['icon']}</div>
                        <div style="color: white;">{item['label']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Logout button at bottom
            st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.user_id = None
                st.session_state.role = None
                st.rerun()

    # Main content area
    if st.session_state.logged_in:
        # App header
        st.markdown("""
        <div class="app-header">
            <div class="app-logo">Acadamix</div>
            <div>Your AI-powered study assistant</div>
        </div>
        """, unsafe_allow_html=True)
        
        # API Keys Section
        with st.expander("🔑 API Configuration", expanded=False):
            with st.container():
                st.markdown("""
                <div style="margin-bottom: 16px;">
                    <div style="font-weight: 600; margin-bottom: 8px;">Configure your API keys</div>
                    <div style="color: #666; font-size: 0.9rem;">These keys are required for AI functionality</div>
                </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(2)
                with cols[0]:
                    groq_api_key = st.text_input("Groq API Key", type="password", 
                                                placeholder="Enter your Groq API key")
                with cols[1]:
                    aws_access_key = st.text_input("AWS Access Key", type="password",
                                                  placeholder="Enter your AWS access key")
                
                cols = st.columns(2)
                with cols[0]:
                    aws_secret_key = st.text_input("AWS Secret Key", type="password",
                                                  placeholder="Enter your AWS secret key")
                with cols[1]:
                    aws_region = st.text_input("AWS Region", value="us-west-2",
                                              placeholder="Enter AWS region (e.g., us-west-2)")

        # Tabs container with modern styling
        tab_bar = st.tabs(["📄 PDF & Notes", "📚 Topic Notes", "📖 Book Suggestions"])
        if st.session_state.role == "tutor":
            tab_bar += st.tabs(["✍️ MCQ Generator"])

        # PDF & Notes Tab
        with tab_bar[0]:
            st.markdown('<h2 class="custom-title">PDF Processing</h2>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown("""
                <div style="background: rgba(255, 107, 107, 0.05); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                    <div style="font-weight: 600; margin-bottom: 8px;">Upload and process PDF documents</div>
                    <div style="color: #666; font-size: 0.9rem;">Generate AI-powered study notes from your PDF files</div>
                </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns([3, 1])
                with cols[0]:
                    uploaded_file = st.file_uploader("Choose PDF file", type="pdf", 
                                                    help="Upload a PDF document to generate study notes")
                with cols[1]:
                    pdf_name = st.text_input("PDF Name", placeholder="Enter document name")
                
                if uploaded_file and pdf_name:
                    if st.button("Generate Notes 🚀", use_container_width=True):
                        if not groq_api_key or not aws_access_key or not aws_secret_key:
                            st.error("Please configure API keys first!")
                        else:
                            with st.spinner("✨ Processing PDF..."):
                                # Progress bar for better UX
                                progress = st.progress(0)
                                
                                # Step 1: Extract text
                                progress.progress(20)
                                st.markdown("<div style='font-size: 0.9rem; color: #666;'>Extracting text from PDF...</div>", unsafe_allow_html=True)
                                text = extract_text_from_pdf(uploaded_file)
                                
                                # Step 2: Create embeddings
                                progress.progress(40)
                                st.markdown("<div style='font-size: 0.9rem; color: #666;'>Creating vector embeddings...</div>", unsafe_allow_html=True)
                                embedding = create_embeddings(text, aws_access_key, aws_secret_key, aws_region)
                                
                                # Step 3: Save to FAISS
                                progress.progress(60)
                                st.markdown("<div style='font-size: 0.9rem; color: #666;'>Saving to vector database...</div>", unsafe_allow_html=True)
                                index_path = save_to_faiss(embedding, pdf_name, st.session_state.user_id)
                                
                                # Step 4: Generate notes
                                progress.progress(80)
                                st.markdown("<div style='font-size: 0.9rem; color: #666;'>Generating study notes...</div>", unsafe_allow_html=True)
                                notes = generate_notes(text, groq_api_key)
                                
                                # Step 5: Save to database
                                progress.progress(100)
                                conn = sqlite3.connect('study_assistant.db')
                                c = conn.cursor()
                                note_id = str(uuid.uuid4())
                                c.execute("INSERT INTO notes VALUES (?, ?, ?, ?, ?)",
                                         (note_id, st.session_state.user_id, pdf_name, index_path, notes))
                                conn.commit()
                                conn.close()
                                
                                # Display notes in card with animation
                                st.markdown(f"""
                                    <div class="card animate-fade-in" style="width: 100%; box-sizing: border-box;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                                            <h3 style="margin: 0; color: #d63031;">📑 {pdf_name} Notes</h3>
                                            <div class="badge">AI Generated</div>
                                        </div>
                                        <div style="white-space: pre-line;">{notes}</div>
                                    </div>
                                """, unsafe_allow_html=True)


        # Topic Notes Tab
        with tab_bar[1]:
            st.markdown('<h2 class="custom-title">Topic-based Learning</h2>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown("""
                <div style="background: rgba(255, 107, 107, 0.05); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                    <div style="font-weight: 600; margin-bottom: 8px;">Generate notes on specific topics</div>
                    <div style="color: #666; font-size: 0.9rem;">AI will search your uploaded documents and create personalized study notes</div>
                </div>
                """, unsafe_allow_html=True)
                
                topic = st.text_input("Enter learning topic", placeholder="e.g., Machine Learning Basics, Quantum Physics, French Revolution")
                
                if st.button("Generate Topic Notes 🧠", use_container_width=True):
                    if not groq_api_key or not aws_access_key or not aws_secret_key:
                        st.error("Please configure API keys first!")
                    else:
                        with st.spinner("🔍 Finding relevant content..."):
                            # Progress indicator
                            progress = st.progress(0)
                            
                            # Step 1: Search for relevant content
                            progress.progress(30)
                            st.markdown("<div style='font-size: 0.9rem; color: #666;'>Searching your knowledge base...</div>", unsafe_allow_html=True)
                            
                            # Step 2: Generate notes
                            progress.progress(70)
                            st.markdown("<div style='font-size: 0.9rem; color: #666;'>Creating personalized notes...</div>", unsafe_allow_html=True)
                            notes = generate_topic_notes(topic, groq_api_key)
                    
                            
                            progress.progress(100)
                            
                            # Display notes with animation
                            st.markdown(f"""
                            <div class="card animate-fade-in">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                                    <h3 style="margin: 0; color: #d63031;">📌 {topic} Notes</h3>
                                    <div class="badge">AI Generated</div>
                                </div>
                                <div style="white-space: pre-line;">{notes}</div>
                            </div>
                            """, unsafe_allow_html=True)

        # Book Suggestions Tab
        with tab_bar[2]:
            st.markdown('<h2 class="custom-title">Book Recommendations</h2>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown("""
                <div style="background: rgba(255, 107, 107, 0.05); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                    <div style="font-weight: 600; margin-bottom: 8px;">Get personalized book recommendations</div>
                    <div style="color: #666; font-size: 0.9rem;">Upload your syllabus to receive tailored book suggestions</div>
                </div>
                """, unsafe_allow_html=True)
                
                uploaded_syllabus = st.file_uploader("Upload syllabus PDF", type="pdf", 
                                                    help="Upload your course syllabus to get relevant book recommendations")
                
                if uploaded_syllabus:
                    if st.button("Get Recommendations 📚", use_container_width=True):
                        if not groq_api_key:
                            st.error("Please configure Groq API key!")
                        else:
                            with st.spinner("📖 Analyzing syllabus..."):
                                syllabus_text = extract_text_from_pdf(uploaded_syllabus)
                                suggestions = generate_book_suggestions(syllabus_text, groq_api_key)
                                
                                st.markdown(f"""
                                <div class="card animate-fade-in">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                                        <h3 style="margin: 0; color: #d63031;">📚 Recommended Books</h3>
                                        <div class="badge">AI Curated</div>
                                    </div>
                                    <div style="white-space: pre-line;">{suggestions}</div>
                                </div>
                                """, unsafe_allow_html=True)

        # MCQ Generator Tab (Tutors only)
        if st.session_state.role == "tutor" and len(tab_bar) > 3:
            with tab_bar[3]:
                st.markdown('<h2 class="custom-title">MCQ Generator</h2>', unsafe_allow_html=True)
                
                with st.container():
                    st.markdown("""
                    <div style="background: rgba(255, 107, 107, 0.05); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                        <div style="font-weight: 600; margin-bottom: 8px;">Create multiple-choice questions</div>
                        <div style="color: #666; font-size: 0.9rem;">Generate high-quality MCQs for assessments and quizzes</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    mcq_topic = st.text_input("Enter MCQ topic", placeholder="e.g., Neural Networks, Cell Biology, World War II")
                    

                    difficulty = st.select_slider(
                        "Difficulty Level",
                        options=["Beginner", "Intermediate", "Advanced"],
                        value="Intermediate"
                    )
                
                    if st.button("Generate Questions ❓", use_container_width=True):
                        if not groq_api_key:
                            st.error("Please configure Groq API key!")
                        else:
                            with st.spinner("🤔 Generating questions..."):
                                mcqs = generate_mcqs(mcq_topic, groq_api_key)
                                
                                if isinstance(mcqs, list):
                                    save_mcqs(st.session_state.user_id, mcq_topic, mcqs)
                                    
                                    # Display MCQs with modern styling
                                    st.markdown(f"""
                                    <div class="card animate-fade-in">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                                            <h3 style="margin: 0; color: #d63031;">📝 {mcq_topic} MCQs</h3>
                                            <div class="badge">{difficulty}</div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Display each MCQ with interactive styling
                                    for i, mcq in enumerate(mcqs, 1):
                                        st.markdown(f"""
                                        <div style="margin-bottom: 2rem; background: white; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                            <div class="mcq-question">Question {i}: {mcq['question']}</div>
                                            <div style="margin-left: 1rem; margin-top: 0.8rem;">
                                                <div class="mcq-option">A. {mcq['options'][0]}</div>
                                                <div class="mcq-option">B. {mcq['options'][1]}</div>
                                                <div class="mcq-option">C. {mcq['options'][2]}</div>
                                                <div class="mcq-option">D. {mcq['options'][3]}</div>
                                            </div>
                                            <div class="mcq-explanation">
                                                <div style="font-weight: 600; color: #d63031;">✅ Answer: {mcq['correct_answer']}</div>
                                                <div style="margin-top: 0.5rem;">💡 <strong>Explanation:</strong> {mcq['explanation']}</div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    st.markdown("</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                    <div class="card">
                                        {mcqs}
                                    </div>
                                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()