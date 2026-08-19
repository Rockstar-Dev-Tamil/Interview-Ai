import os
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Initialize the client. We assume GOOGLE_API_KEY is in the environment.
client = genai.Client()

def lint_code(language: str, code: str) -> list:
    """
    Validates the syntax of the provided code using Gemini.
    Returns a list of error strings. Returns an empty list if the code is valid.
    """
    logger.info(f"Linting {language} code via Gemini...")
    
    prompt = f"""
    You are a strict compiler and static analyzer for the {language} programming language.
    Your job is to find compilation errors, syntax errors, and missing brackets/semicolons in the provided code.
    If the code contains errors, output a JSON array of strings, where each string is a precise error message containing the line number and the issue.
    If the code has no syntax errors, output an empty JSON array: []
    
    Do NOT output any markdown blocks or explanations, JUST the JSON array.
    
    Code to evaluate:
    ```{language}
    {code}
    ```
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json"
            )
        )
        
        # Parse the JSON response
        errors = json.loads(response.text.strip())
        if not isinstance(errors, list):
            return ["Compilation Error: Unable to parse syntax correctly."]
            
        return errors
    except Exception as e:
        logger.error(f"Error calling Gemini linter: {e}")
        return [f"System Error: Failed to lint code. {str(e)}"]
