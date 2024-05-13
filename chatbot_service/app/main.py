from fastapi import FastAPI, HTTPException
import requests
import re
from transformers import pipeline

app = FastAPI()
nlp = pipeline("text-classification")

@app.post("/ask")
async def ask_chatbot(question: str):
    try:
        intent = nlp(question)
        placement = extract_placement(question)
        if "employee" in intent[0]['label']:
            response = requests.get(f"http://api_service:8000/get_employee/{placement}")
        elif "department" in intent[0]['label']:
            response = requests.get(f"http://api_service:8000/get_department/{placement}")
        else:
            raise HTTPException(status_code=404, detail="Question not understood")
        return response.json()
    except Exception as e:
        # Handle unexpected errors
        print(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def extract_placement(question):
    match = re.search(r'\b(\d+)[st|nd|rd|th]\b', question)
    return match.group(0) if match else 'Unknown'
