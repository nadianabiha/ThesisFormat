import os
from functools import lru_cache

from google import genai


@lru_cache(maxsize=1)
def _get_client():
    # Dibuat saat pertama dipakai, agar manage.py (migrate, dll.)
    # tetap jalan walaupun GEMINI_API_KEY belum diset.
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate(prompt):
    response = _get_client().models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )
    return response.text
