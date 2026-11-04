"""Provider configuration. Secrets stay in the process or a local .env file."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/'
DEFAULT_GEMINI_MODEL = 'gemini-3.1-flash-lite'


@dataclass(frozen=True)
class Settings:
    provider: str
    model: str
    api_key: str = ''
    base_url: str | None = None

    @classmethod
    def from_env(cls, provider: str | None = None, model: str | None = None,
                 env_file: Path | None = BASE / '.env') -> 'Settings':
        if env_file is not None and env_file.is_file():
            try:
                from dotenv import load_dotenv
            except ImportError as exc:
                raise RuntimeError('Instale as dependências: python -m pip install -r requirements.txt') from exc
            load_dotenv(env_file, override=False)
        selected = (provider or os.getenv('AI_PROVIDER', 'gemini')).strip().lower()
        if selected not in {'gemini', 'openai', 'offline'}:
            raise ValueError('AI_PROVIDER deve ser gemini, openai ou offline.')
        if selected == 'offline':
            return cls('offline', 'deterministic-demo')
        if selected == 'gemini':
            key = (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or '').strip()
            chosen = model or os.getenv('GEMINI_MODEL', DEFAULT_GEMINI_MODEL)
            endpoint = GEMINI_BASE_URL
        else:
            key = os.getenv('OPENAI_API_KEY', '').strip()
            chosen = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            endpoint = None
        if key.lower() in {'your_api_key_here', 'cole_sua_chave_aqui', 'your_gemini_api_key_here'}:
            key = ''
        return cls(selected, chosen.strip(), key, endpoint)
