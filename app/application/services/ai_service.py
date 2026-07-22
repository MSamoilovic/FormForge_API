"""
Service for communicating with the AI model.

Uses an OpenAI-compatible interface, so the provider is a matter of
configuration (`AI_BASE_URL` / `AI_MODEL`) rather than code. Defaults to Gemini.
"""
from openai import AsyncOpenAI

from app.core.config import settings


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.AI_BASE_URL,
            api_key=settings.GEMINI_API_KEY,
        )
        self.model = settings.AI_MODEL

    async def generate_response(self, prompt: str) -> str:
        """Free-form text response to a prompt."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    async def generate_json_from_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """
        Returns the model's response in JSON format as a string.

        Does not parse or validate — that is the caller's responsibility,
        since the caller knows which schema it needs to fit.
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
