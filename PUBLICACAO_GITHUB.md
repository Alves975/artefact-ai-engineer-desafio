# GitHub Publication and Verification — Artefact Technical Case

**Public repository:** https://github.com/Alves975/artefact-ai-engineer-desafio

The application code, configuration templates, test suite, examples, and CSV/policy-text data required by the agent are available in the public repository. The original `data/políticas_da_loja.pdf` file from the supplied ZIP was **not published**; the application uses the extracted `data/policies_extracted.txt` instead. Distribution rights should be verified before publishing any original case materials.

## Local installation and execution

Python 3.10 or later is required.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python app.py --offline
```

For Google Gemini, copy `.env.example` to `.env`, set `GEMINI_API_KEY`, and run `python app.py --check-api`. Do not commit the real `.env` or share the key.

See [Getting Started with Google Gemini](COMECAR_AQUI.md) for operating-system-specific setup instructions.

## Verification status and limitations

The following results describe a previous local validation session on November 4, 2026, not a fresh GitHub Actions result:

- Python source compilation: **passed** using `python -m compileall -q app.py src tests scripts`.
- Deterministic offline CLI demonstration: **passed**.
- 41 unit/regression tests not requiring the external SDK: **passed**.
- Complete test suite using the installed OpenAI SDK and mocked HTTP responses: **not executed in that session** because the `openai` dependency could not be installed in the environment.
- Real Gemini API call: **not verified in that session**; it requires a valid API key and network access.

The README also records the source project's earlier reported result of 61 passing tests. This result should be reproduced locally or in GitHub Actions before claiming a new complete verification.

## Submission

Artefact's form requests **(1)** an English PDF generated from the README/project documentation and **(2)** a public GitHub link. The repository URL above is the code link; uploading an archive is not a substitute for a public repository.

Keep the application's customer-facing Portuguese responses and the original business data unchanged. Translating documentation does not require changing the agent's behavior or internal function names.
