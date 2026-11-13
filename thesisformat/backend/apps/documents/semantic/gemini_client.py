import os
from functools import lru_cache

from google import genai
from google.genai import types


def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# Urutan model: model utama dulu, lalu cadangan jika model utama
# sibuk/timeout. Bisa diganti lewat .env, contoh:
# GEMINI_MODELS=gemini-3.8-flash,gemini-3.7-flash,gemini-3.5-flash
GEMINI_MODELS = [
    name.strip()
    for name in os.getenv(
        "GEMINI_MODELS",
        "gemini-3.8-flash,gemini-3.7-flash,gemini-3.5-flash",
    ).split(",")
    if name.strip()
]

# Batas waktu satu panggilan Gemini (detik). Gemini menolak nilai di
# bawah 10 detik, jadi nilai minimum dipaksa 10.
GEMINI_TIMEOUT_SECONDS = max(10, _env_int("GEMINI_TIMEOUT_SECONDS", 60))


@lru_cache(maxsize=1)
def _get_client():
    # Dibuat saat pertama dipakai, agar manage.py (migrate, dll.)
    # tetap jalan walaupun GEMINI_API_KEY belum diset.
    return genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
        http_options=types.HttpOptions(
            timeout=GEMINI_TIMEOUT_SECONDS * 1000,  # milidetik
        ),
    )


def generate(prompt, model=None):
    response = _get_client().models.generate_content(
        model=model or GEMINI_MODELS[0],
        contents=prompt,
    )
    return response.text
