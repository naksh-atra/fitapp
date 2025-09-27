# tests/legacy/conftest.py
import os

# Provide a dummy key so modules that create API clients at import time don't crash
os.environ.setdefault("OPENAI_API_KEY", "test")  # legacy-only safety
