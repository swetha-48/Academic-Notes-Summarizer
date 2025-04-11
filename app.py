import streamlit as st
from utils import read_document
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the GEMINI API key from .env
api_key = os.getenv("GEMINI_API_KEY")

# Configure page
st.set_page_config(
    page_title="Document Summarizer & Q&A Generator",
    page_icon="📄",
    layout="centered"
)

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .summary-container, .qa-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4B7BE5;
        margin-top: 20px;
    }
    .qa-item {
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 1px solid #e0e0e0;
    }
    .qa-question {
        font-weight: bold;
        color: #4B7BE5;
        margin-bottom: 5px;
    }
    .qa-answer {
        margin-left: 10px;
    }
    .stButton > button {
        background-color: #4B7BE5;
        color: white;
        font-weight: bold;
    }
    .info-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #4B7BE5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .info-card h4 {
        margin-top: 0;
        color: #4B7BE5;
    }
    .info-card p {
        margin-bottom: 0;
        font-size: 0.9rem;
    }
    .info-cards-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .tabs-container {
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown("<h1 class='main-header'>📄 Document Summarizer & Q&A Generator</h1>", unsafe_allow_html=True)
st.markdown("Upload a document (PDF, DOCX, or TXT) to get an AI-powered summary and Q&A using Gemini Flash.")

# API Key input - only shown if not in environment
if not api_key:
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.warning("Please enter your Gemini API Key to continue")
        st.stop()
else:
    # Configure Gemini API with the key from .env
    genai.configure(api_key=api_key)

# Information Cards
st.markdown("<div class='info-cards-container'>", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "txt"])

# Main workflow
if uploaded_file is not None:
    with st.spinner("Reading document..."):
        content = read_document(uploaded_file)

    if content:
        st.success("✅ Document loaded successfully!")

        # Summarize button
        if st.button("Generate Summary & Q&A", type="primary"):
            try:
                with st.spinner("AI is analyzing your document..."):
                    # Configure the model - using Flash model for faster processing
                    model = genai.GenerativeModel("gemini-1.5-flash")

                    # Enhanced prompt for summary and Q&A
                    prompt = f"""Analyze the following document and provide:

                    1. A clear and concise summary of the main points and key information.
                    2. At least 5 important question-answer pairs based on the document content. These should cover key information that would be valuable for someone wanting to understand the document.

                    Format your response as follows:

                    SUMMARY:
                    [Your summary here]

                    Q&A:
                    Q1: [Question 1]
                    A1: [Answer 1]

                    Q2: [Question 2]
                    A2: [Answer 2]

                    [and so on for at least 5 Q&A pairs]

                    Document content:
                    {content[:100000]}  # Limit content to avoid token limits
                    """

                    # Generate response
                    response = model.generate_content(prompt)
                    full_response = response.text

                    # Split the response into summary and Q&A sections
                    parts = full_response.split("Q&A:")

                    if len(parts) >= 2:
                        summary_part = parts[0].replace("SUMMARY:", "").strip()
                        qa_part = "Q&A:" + parts[1].strip()

                        # Create tabs for Summary and Q&A
                        tab1, tab2 = st.tabs(["Summary", "Q&A"])

                        with tab1:
                            st.markdown("<div class='summary-container'>", unsafe_allow_html=True)
                            st.markdown(summary_part)
                            st.markdown("</div>", unsafe_allow_html=True)

                            # Download summary
                            st.download_button(
                                label="Download Summary",
                                data=summary_part,
                                file_name=f"summary_{uploaded_file.name.split('.')[0]}.txt",
                                mime="text/plain"
                            )

                        with tab2:
                            st.markdown("<div class='qa-container'>", unsafe_allow_html=True)

                            # Parse and display Q&A pairs
                            qa_lines = qa_part.strip().split('\n')
                            qa_pairs = []

                            current_q = ""
                            current_a = ""

                            for line in qa_lines[1:]:  # Skip the "Q&A:" header
                                line = line.strip()
                                if not line:
                                    continue

                                if line.startswith("Q") and ":" in line:
                                    # If we have a previous Q&A pair, add it to our list
                                    if current_q and current_a:
                                        qa_pairs.append((current_q, current_a))

                                    # Start a new question
                                    parts = line.split(":", 1)
                                    if len(parts) > 1:
                                        current_q = parts[1].strip()
                                        current_a = ""

                                elif line.startswith("A") and ":" in line:
                                    parts = line.split(":", 1)
                                    if len(parts) > 1:
                                        current_a = parts[1].strip()

                            # Add the last Q&A pair if it exists
                            if current_q and current_a:
                                qa_pairs.append((current_q, current_a))

                            # Display Q&A pairs
                            for i, (question, answer) in enumerate(qa_pairs, 1):
                                st.markdown(f"<div class='qa-item'>", unsafe_allow_html=True)
                                st.markdown(f"<div class='qa-question'>Q{i}: {question}</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='qa-answer'>A{i}: {answer}</div>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)

                            # Download Q&A
                            st.download_button(
                                label="Download Q&A",
                                data=qa_part,
                                file_name=f"qa_{uploaded_file.name.split('.')[0]}.txt",
                                mime="text/plain"
                            )

                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        # If the response doesn't have the expected format, display it as is
                        st.markdown("<div class='summary-container'>", unsafe_allow_html=True)
                        st.markdown(full_response)
                        st.markdown("</div>", unsafe_allow_html=True)

                        # Simple download option
                        st.download_button(
                            label="Download Full Response",
                            data=full_response,
                            file_name=f"response_{uploaded_file.name.split('.')[0]}.txt",
                            mime="text/plain"
                        )

            except Exception as e:
                st.error(f"Error generating content: {str(e)}")
                st.info(
                    "If you're seeing a model not found error, try using 'gemini-1.5-pro' instead of 'gemini-1.5-flash' or check the available models in the Gemini AI documentation.")
    else:
        st.error("Could not read the document content. Please check the file format.")

# Footer
st.caption("Powered by Google Gemini AI")
