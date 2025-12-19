import google.genai as genai
from app.core.config import settings

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash', generation_config=genai.GenerationConfig(
            response_mime_type='application/json',
        ))

    async def generate_response(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error communicating with Gemini API: {e}")
            return "Error: Could not get a response from the AI model."

    def generate_json_from_prompt(self, system_prompt: str, user_prompt: str) -> str:
        full_prompt = f"{system_prompt}\n\nUser request: '{user_prompt}'"
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error generating JSON from Gemini API: {e}")
            raise