import os
from functools import lru_cache

from google import genai
from google.genai import errors, types


def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# Urutan model: model utama dulu, lalu cadangan jika model utama
# sibuk/timeout. Model "lite" ditaruh di urutan kedua karena biasanya
# tetap tersedia saat model flash biasa sedang penuh (503), dan tetap
# terjangkau dalam batas waktu total. Bisa diganti lewat .env, contoh:
# GEMINI_MODELS=gemini-3.8-flash,gemini-3.5-flash-lite,gemini-3.7-flash
GEMINI_MODELS = [
    name.strip()
    for name in os.getenv(
        "GEMINI_MODELS",
        "gemini-3.8-flash,gemini-3.5-flash-lite,gemini-3.7-flash,"
        "gemini-3.1-flash-lite,gemini-3.5-flash",
    ).split(",")
    if name.strip()
]

# Batas waktu satu panggilan Gemini (detik). Gemini menolak nilai di
# bawah 10 detik, jadi nilai minimum dipaksa 10. Dokumen panjang bisa
# butuh 40-70 detik, jadi 60 detik sering memotong jawaban yang hampir jadi.
GEMINI_TIMEOUT_SECONDS = max(10, _env_int("GEMINI_TIMEOUT_SECONDS", 75))

# Seed tetap + temperature 0 = jawaban sekonsisten mungkin untuk dokumen
# yang sama (Google tidak menjamin 100% identik, tapi jauh lebih stabil).
GEMINI_SEED = 42


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


def generation_config(low_thinking=True):
    """
    Pengaturan jawaban AI:
    - temperature 0 + seed: tidak "kreatif", hasil konsisten.
    - response_mime_type JSON: jawaban dijamin JSON (tidak ada teks lain).
    - thinking_level "low": pemeriksaan format tidak perlu berpikir lama,
      jadi jawaban lebih cepat dan lebih jarang timeout.
    """
    return types.GenerateContentConfig(
        temperature=0,
        seed=GEMINI_SEED,
        response_mime_type="application/json",
        thinking_config=(
            types.ThinkingConfig(thinking_level="low") if low_thinking else None
        ),
    )


def generate(prompt, model=None):
    model = model or GEMINI_MODELS[0]
    client = _get_client()
    try:
        response = client.models.generate_content(
            model=model, contents=prompt, config=generation_config(),
        )
    except errors.APIError as exc:
        if getattr(exc, "code", None) != 400:
            raise
        # Sebagian model menolak pengaturan mode berpikir (400):
        # ulangi sekali dengan model yang sama tanpa pengaturan itu.
        response = client.models.generate_content(
            model=model, contents=prompt, config=generation_config(low_thinking=False),
        )
    return response.text
