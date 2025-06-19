import os
import logging
from openai import OpenAI
from typing import Dict, Any
import PyPDF2
import docx

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: str) -> str:
    """Extract text content from PDF or DOCX files."""
    file_ext = file_path.lower().split('.')[-1]
    
    if file_ext == 'pdf':
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ' '.join(page.extract_text() for page in pdf_reader.pages)
    elif file_ext in ['docx', 'doc']:
        doc = docx.Document(file_path)
        text = ' '.join(paragraph.text for paragraph in doc.paragraphs)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")
    
    return text

def parse_with_gpt4(file_path: str) -> Dict[str, Any]:
    """
    Parse a resume using OpenAI's GPT-4 model.
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        Dict[str, Any]: Parsed resume data in a standardized format
    """
    try:
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OpenAI API key")
        
        client = OpenAI()
        
        # Extract text from the resume file
        resume_text = extract_text_from_file(file_path)
        
        # Prepare the prompt
        system_prompt = """You are a resume parsing expert. Extract the following information from the resume text:
        - Full Name
        - Email Address
        - Phone Number
        - Skills (as a list)
        - Work Experience (as a list of dictionaries with company, title, dates, and description)
        - Education (as a list of dictionaries with institution, degree, dates)
        
        Format the output as a JSON object with these keys: name, email, mobile_number, skills, experience, education"""
        
        # Call GPT-4 API
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # or another appropriate model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": resume_text}
            ],
            response_format={ "type": "json_object" }
        )
        
        # Parse and validate the response
        parsed_data = eval(response.choices[0].message.content)
        
        # Ensure all required fields are present
        required_fields = ["name", "email", "mobile_number", "skills", "experience", "education"]
        for field in required_fields:
            if field not in parsed_data:
                parsed_data[field] = [] if field in ["skills", "experience", "education"] else ""
        
        return parsed_data
        
    except Exception as e:
        logger.error(f"Error in GPT-4 parsing: {str(e)}")
        raise 