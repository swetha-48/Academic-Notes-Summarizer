import PyPDF2
import docx
import io

def read_document(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == 'pdf':
        return read_pdf(uploaded_file)
    elif file_type == 'docx':
        return read_docx(uploaded_file)
    elif file_type == 'txt':
        return uploaded_file.read().decode('utf-8')
    else:
        return None

def read_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:  # Check if text extraction was successful
                text += page_text + "\n\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def read_docx(file):
    try:
        doc = docx.Document(io.BytesIO(file.read()))
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return None