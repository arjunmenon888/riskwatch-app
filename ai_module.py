import os
import json
import traceback
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        ai_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("AI Module: Gemini AI Model initialized successfully.")
    except Exception as e:
        print(f"AI Module ERROR: Could not initialize Gemini: {e}")
        ai_model = None
else:
    print("AI Module WARNING: GEMINI_API_KEY not found in .env file.")
    ai_model = None

def get_ai_analysis(observation_text, floor_input, location):
    if not ai_model:
        return {k: "AI Error - Model Not Initialized" for k in ['CorrectedDescription', 'StandardizedFloor', 'ImpactOnOperations', 'Likelihood', 'Severity', 'CorrectiveAction', 'ResponsiblePerson', 'DeadlineSuggestion']}

    valid_floors_list = [
        "basement 4", "basement 3", "basement 2", "basement 1", "groundfloor",
        "first floor", "second floor", "third floor", "forth floor", "fifth floor",
        "sixth floor", "seventh floor", "eighth floor", "nineth floor", "roof top"
    ]
    
    prompt = f"""
    Analyze the safety observation from a hotel environment.
    User's Floor Input: "{floor_input}"
    Location: "{location}"
    Original Observation: "{observation_text}"

    Your task is to return a SINGLE, VALID JSON object. Do NOT include any text or markdown formatting before or after the JSON object.

    The JSON object must have the following keys:
    1.  "StandardizedFloor": Analyze the "User's Floor Input". Map it to ONE of the following standard labels: {json.dumps(valid_floors_list)}. Use context clues like "G" for "groundfloor", "B1" for "basement 1". If you cannot confidently map it, return the original "User's Floor Input".
    2.  "CorrectedDescription": A professionally rephrased and spell-checked version of the original observation.
    3.  "ImpactOnOperations": Describe the potential impact on hotel operations, guest experience, or staff safety if the hazard is not addressed.
    4.  "Likelihood": An integer from 1 (very unlikely) to 5 (very likely).
    5.  "Severity": An integer from 1 (minor) to 5 (critical).
    6.  "CorrectiveAction": A clear, actionable recommendation.
    7.  "ResponsiblePerson": Assign ONE role from: 'chief engineer', 'head of IT', 'director of marketing', 'director of rooms', 'director of p&c', 'director of f&b', 'director of sales', 'financial controller', 'executive sous chef'.
    8.  "DeadlineSuggestion": Suggest a realistic deadline (e.g., "Immediately", "24 Hours", "1 Week").
    """
    try:
        response = ai_model.generate_content(prompt)
        raw_ai_text = response.text.strip()
        
        cleaned_response_text = raw_ai_text
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[len("```json"):].strip()
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-len("```")].strip()
        
        if not (cleaned_response_text.startswith("{") and cleaned_response_text.endswith("}")):
            first_brace = cleaned_response_text.find('{')
            last_brace = cleaned_response_text.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                cleaned_response_text = cleaned_response_text[first_brace : last_brace + 1]
            else:
                raise json.JSONDecodeError("No valid JSON structure found in AI response.", cleaned_response_text, 0)
        
        parsed_json_data = json.loads(cleaned_response_text)
        
        # --- MODIFIED: Removed 'HazardType' from the final output dict ---
        final_data = {
            'StandardizedFloor': parsed_json_data.get('StandardizedFloor', floor_input),
            'CorrectedDescription': parsed_json_data.get('CorrectedDescription', f"AI Rephrase Failed. Original: {observation_text}"),
            'ImpactOnOperations': parsed_json_data.get('ImpactOnOperations', 'N/A'),
            'Likelihood': int(parsed_json_data.get('Likelihood', 0)),
            'Severity': int(parsed_json_data.get('Severity', 0)),
            'CorrectiveAction': parsed_json_data.get('CorrectiveAction', 'N/A'),
            'ResponsiblePerson': parsed_json_data.get('ResponsiblePerson', 'N/A'),
            'DeadlineSuggestion': parsed_json_data.get('DeadlineSuggestion', 'N/A'),
        }
        return final_data

    except (json.JSONDecodeError, ValueError) as je:
        print(f"AI Module JSON/Value Error: {je}\nText that failed: {cleaned_response_text[:500]}\n{traceback.format_exc()}")
        return {k: f"AI Error (Parsing)" for k in ['CorrectedDescription', 'StandardizedFloor', 'ImpactOnOperations', 'Likelihood', 'Severity', 'CorrectiveAction', 'ResponsiblePerson', 'DeadlineSuggestion']}
    except Exception as e:
        print(f"AI Module Error in get_ai_analysis: {e}\n{traceback.format_exc()}")
        return {k: f"AI Error (General)" for k in ['CorrectedDescription', 'StandardizedFloor', 'ImpactOnOperations', 'Likelihood', 'Severity', 'CorrectiveAction', 'ResponsiblePerson', 'DeadlineSuggestion']}