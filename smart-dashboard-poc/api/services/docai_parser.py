import os
import logging
from google.cloud import documentai
from typing import Dict, Any

logger = logging.getLogger(__name__)

def parse_with_docai(file_path: str) -> Dict[str, Any]:
    """
    Parse a resume using Google Document AI.
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        Dict[str, Any]: Parsed resume data in a standardized format
    """
    try:
        # Initialize Document AI client
        client = documentai.DocumentProcessorServiceClient()
        
        # Get the processor details from environment variables
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us")  # Default to US
        processor_id = os.getenv("GOOGLE_DOCAI_PROCESSOR_ID")
        
        if not all([project_id, processor_id]):
            raise ValueError("Missing required Google Cloud configuration")
            
        name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
        
        # Read the file
        with open(file_path, "rb") as file:
            document_content = file.read()
            
        # Create the document object
        raw_document = documentai.RawDocument(
            content=document_content,
            mime_type="application/pdf"  # Assuming PDF, adjust if needed
        )
        
        # Process the document
        request = documentai.ProcessRequest(
            name=name,
            raw_document=raw_document
        )
        
        result = client.process_document(request=request)
        document = result.document
        
        # Extract and structure the data
        # Note: This is a basic implementation. Adjust the parsing logic based on
        # your Document AI processor's output structure
        parsed_data = {
            "name": "",
            "email": "",
            "mobile_number": "",
            "skills": [],
            "experience": [],
            "education": []
        }
        
        # Process entities from Document AI
        for entity in document.entities:
            if entity.type_ == "person_name":
                parsed_data["name"] = entity.mention_text
            elif entity.type_ == "email_address":
                parsed_data["email"] = entity.mention_text
            elif entity.type_ == "phone_number":
                parsed_data["mobile_number"] = entity.mention_text
            elif entity.type_ == "skill":
                parsed_data["skills"].append(entity.mention_text)
            # Add more entity mappings as needed
        
        return parsed_data
        
    except Exception as e:
        logger.error(f"Error in Document AI parsing: {str(e)}")
        raise 