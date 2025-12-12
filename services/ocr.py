import google.generativeai as genai
import PIL.Image
import json
import re
import time
from PIL import Image
import requests
from io import BytesIO

def load_image_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for errors (like 404)
        return BytesIO(response.content)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None
class PrescriptionOCR:
    def __init__(self, api_key):
        # Configure Google AI
        genai.configure(api_key=api_key)

        # --- STRATEGY ---
        # 1. PRIMARY: gemini-2.5-flash
        #    - The "Brain". Best reasoning for messy handwriting. 
        #    - Limit: ~250 requests/day (Free Tier).
        self.primary_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        # 2. HAIL MARY BACKUP: gemini-2.5-flash-lite
        #    - The "Workhorse". Slightly less nuanced, but very fast.
        #    - Limit: ~1,000 requests/day.
        #    - We switch to this if the primary model hits a rate limit.
        self.backup_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            generation_config={"response_mime_type": "application/json"}
        )

    def extract_medicines(self, image_path):
        """
        Main entry point. Handles image loading, AI calling, and failover logic.
        """
        print(f"Reading: {image_path}")
        try:
            img = PIL.Image.open(image_path)
        except Exception as e:
            return {"error": f"Image load failed: {str(e)}"}

        # The Prompt: Tuned for medical extraction
        prompt = """
        You are an expert clinical pharmacist. 
        Analyze this prescription image and extract the medicine details.
        
        Strict Rules:
        1. Identify the Medicine Name. Correct spelling errors based on common drug names (e.g. 'Pcm' -> 'Paracetamol', 'Aug' -> 'Augmentin').
        2. Identify Dosage (e.g. 500mg) and Frequency (e.g. 1-0-1, BD, SOS).
        3. Return a JSON list of objects.
        
        JSON Structure:
        [
          {"name": "Medicine Name", "dosage": "500mg", "frequency": "BD", "confidence": "high"},
          ...
        ]
        """

        # --- ATTEMPT 1: PRIMARY MODEL ---
        try:
            print("🚀 Sending to Primary (Gemini 2.5 Flash)...")
            response = self.primary_model.generate_content([prompt, img])
            return self._parse_json(response.text)

        except Exception as e:
            print(f"⚠️ Primary Model Failed: {e}")
            print("🔄 Initiating Hail Mary Protocol...")

            # --- ATTEMPT 2: HAIL MARY BACKUP ---
            try:
                # Small cool-down to prevent rapid-fire API errors
                time.sleep(1) 
                print("🛡️ Sending to Backup (Gemini 2.5 Flash Lite)...")
                response = self.backup_model.generate_content([prompt, img])
                return self._parse_json(response.text)
            
            except Exception as e2:
                print(f"❌ CRITICAL: Backup also failed: {e2}")
                return []

    def _parse_json(self, raw_text):
        """
        Robust JSON cleaning. Even though we requested JSON, 
        AI sometimes wraps it in markdown blocks.
        """
        try:
            # Remove ```json and ``` if present
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            print("Error: AI returned invalid JSON.")
            return []

# --- HOW TO USE IN YOUR WEBAPP ---

if __name__ == "__main__":
    # Replace with your actual key
    API_KEY = ""

    # Initialize once (e.g., in your app startup)
    ocr = PrescriptionOCR(API_KEY)

    # Call whenever needed
    result = ocr.extract_medicines(load_image_from_url("https://ik.imagekit.io/RemediRX/pres1?updatedAt=1764441758082"))
    print("\n--- FINAL RESULT ---")
    print(json.dumps(result, indent=4))
