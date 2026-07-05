import os
import logging
from pypdf import PdfReader
import docx
import openai

logger = logging.getLogger("OnboardGenius.AI")

def extract_text_from_file(file_path: str) -> str:
    """
    Extracts plain text from PDF and DOCX documents.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at: {file_path}")

    _, ext = os.path.splitext(file_path.lower())
    text_content = ""

    try:
        if ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content += extracted + "\n"
        elif ext == ".docx":
            doc = docx.Document(file_path)
            text_content = "\n".join([p.text for p in doc.paragraphs])
        else:
            # Fallback text reading for raw text files
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text_content = f.read()
    except Exception as e:
        logger.error(f"Error extracting text from file {file_path}: {e}")
        raise RuntimeError(f"Could not parse document file: {e}")

    return text_content.strip()

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-openai-api-key-here":
        return openai.OpenAI(api_key=api_key)
    return None

def summarize_document(file_path: str) -> str:
    """
    Parses document and generates a bulleted summary using OpenAI.
    """
    try:
        text = extract_text_from_file(file_path)
        if not text:
            return "The document appears to be empty or contains unreadable text."

        # Limit text size to prevent token overflow in small models
        text_preview = text[:4000]

        client = get_openai_client()
        if client:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional HR assistant. Summarize the following document text into a concise, bullet-pointed summary focusing on employee onboarding, compliance, policies, or expectations."},
                        {"role": "user", "content": f"Document Text:\n\n{text_preview}"}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI summarization failed: {e}")
                # Fallback to local extraction
        
        # Local fallback summary
        return f"### Document Summary (Local Extraction Fallback)\n- **File Name**: {os.path.basename(file_path)}\n- **Extracted Characters**: {len(text)}\n- **Content Preview**: {text[:300]}...\n\n*(Note: Configure a valid OPENAI_API_KEY in your .env file to enable detailed AI summaries)*"
    except Exception as e:
        return f"Failed to summarize document: {e}"

def generate_onboarding_email(email_type: str, details: dict) -> str:
    """
    Generates professional email drafts (e.g. welcome, equipment request).
    """
    client = get_openai_client()
    if client:
        try:
            prompt = f"Write a professional email draft of type '{email_type}'. Details: {details}"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an HR Administrator. Write clear, professional, and friendly email drafts based on the details provided."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI email generation failed: {e}")

    # Fallback response
    if "welcome" in email_type.lower():
        return f"Subject: Welcome to the Team!\n\nDear {details.get('employee_name', 'Employee')},\n\nWe are absolutely thrilled to welcome you to the {details.get('department', 'Company')} department as our new {details.get('position', 'Team Member')}. Your start date is set for {details.get('start_date', 'your start date')}.\n\nPlease review your onboarding dashboard tasks before your first day.\n\nBest regards,\nHR Administration"
    elif "equipment" in email_type.lower():
        return f"Subject: IT Equipment Request - {details.get('employee_name', 'Employee')}\n\nHi IT Support,\n\nPlease prepare the hardware setup for {details.get('employee_name', 'Employee')}, joining as a {details.get('position', 'Team Member')} in the {details.get('department', 'Company')} department.\n\nRequired:\n- Laptop / Desktop\n- Office credentials setup\n\nThank you,\nHR Administration"
    else:
        return f"Subject: Onboarding Update\n\nDear {details.get('employee_name', 'Team Member')},\n\nThis is a quick update regarding your onboarding tasks. Please log in to your dashboard to review pending compliance checklists.\n\nBest regards,\nHR Administration"

def recommend_tasks_by_job(position: str, department: str) -> list[dict]:
    """
    Generates recommended tasks based on employee position and department.
    """
    client = get_openai_client()
    if client:
        try:
            prompt = f"Generate 4 onboarding tasks for position: '{position}', department: '{department}'."
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an onboarding supervisor. Recommend 4 specific tasks in structured CSV-like format: 'Title | Description | Days offset'. Return only the tasks, one per line."},
                    {"role": "user", "content": prompt}
                ]
            )
            lines = response.choices[0].message.content.strip().split("\n")
            recommended = []
            for line in lines:
                parts = line.split("|")
                if len(parts) >= 2:
                    recommended.append({
                        "title": parts[0].strip().replace("- ", ""),
                        "description": parts[1].strip(),
                        "days_due": int(parts[2].strip()) if len(parts) > 2 and parts[2].strip().isdigit() else 7
                    })
            if recommended:
                return recommended
        except Exception as e:
            logger.error(f"OpenAI task recommendation failed: {e}")

    # Fallback static recommendations
    return [
        {"title": f"Review {department} orientation guidelines", "description": "Read through department-specific wiki pages and documentation.", "days_due": 3},
        {"title": f"Complete {position} setup credentials", "description": "Configure developer tools, systems accesses, and secure credentials.", "days_due": 2},
        {"title": "Schedule 1-on-1 team welcome intro", "description": "Coordinate a short call with team leads to introduce yourself.", "days_due": 5},
        {"title": "Submit signed employee handbook agreement", "description": "Upload a signed copy of company handbook rules in the documents tab.", "days_due": 7}
    ]
