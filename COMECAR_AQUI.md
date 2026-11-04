# Getting Started with Google Gemini

This project supports **Gemini 3.1 Flash-Lite** for conversational responses and tool calling. Availability of a free tier depends on the Google project and current account quotas; free use is not unlimited.

## 1. Create an API key

1. Open [Google AI Studio — API keys](https://aistudio.google.com/apikey).
2. Sign in to a Google account and accept the applicable terms.
3. Select **Create API key**, or use an existing key from a project with access to the configured model.
4. To try the free tier, review the billing tier and quota of your Google project before making API requests.
5. Keep the key on your local machine. **Do not paste an API key into a chat message, screenshot, or GitHub repository.**

## 2. Install and configure

Open a terminal in the repository directory, next to `app.py` and `requirements.txt`. Python 3.10 or later is required.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Using the virtual environment's Python executable avoids needing to activate PowerShell scripts. If `python` is not found, try the `py` launcher or install a supported Python version.

In the new `.env` file, configure:

```dotenv
AI_PROVIDER=gemini
GEMINI_API_KEY=YOUR_API_KEY_HERE
GEMINI_MODEL=gemini-3.1-flash-lite
```

Save it as **`.env`** alongside `app.py`, not `.env.txt`. Only `.env.example`, which contains no real credentials, belongs in the repository.

**macOS/Linux:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` using a local text editor and set the same variables.

## 3. Verify API access and start a conversation

**Windows:**

```powershell
.\.venv\Scripts\python.exe app.py --check-api
.\.venv\Scripts\python.exe app.py
```

**macOS/Linux:**

```bash
.venv/bin/python app.py --check-api
.venv/bin/python app.py
```

The first command performs a real request about store opening hours and checks the AI → policy retrieval tool → response path. The second launches the interactive customer support assistant.

Try these sample customer questions in Brazilian Portuguese:

1. `Quais violões vocês têm até R$ 500?`
2. `E de 7 cordas, quais vocês têm?`
3. `Quais produtos estão em promoção?`
4. `Qual o prazo para reembolso?`
5. `Qual o status do pedido 1?` — provide the corresponding fictional customer's email if requested.

The conversation commands remain `/limpar` (reset chat history) and `/sair` (exit), because the assistant serves Brazilian customers.

## Troubleshooting

| Symptom | Recommended action |
| --- | --- |
| Offline demonstration instead of Gemini | Check that `.env` is in the project root and `GEMINI_API_KEY` is configured, then restart the application. |
| Authentication denied | Check that the complete API key was copied correctly and that the project can access the Gemini API. |
| Model unavailable | Check the available models for your API key in Google AI Studio, and adjust `GEMINI_MODEL` if needed. |
| Quota exceeded | Review account quotas, free-tier eligibility, and billing configuration. The application does not enable paid billing or switch providers automatically. |
| Connection failure | Check your network connection and retry. The application is designed to retain earlier conversation state when a request fails. |

To run without credentials or network access:

```bash
python app.py --offline
```

Offline mode is a deterministic demonstration rather than a generative conversation. Natural-language Gemini conversations require a valid key and network access.

Never publish real keys or paste them into error reports.
