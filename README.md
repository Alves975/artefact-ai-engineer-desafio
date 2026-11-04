# Empório da Música — Customer Support Agent

Python technical case for **Artefact — AI Engineer**. A text assistant answers questions about the supplied musical-instrument catalog, customer orders and store policies.

**Default provider: Google Gemini**, using `gemini-3.1-flash-lite`. It supports function calling and has a free tier according to the official Google documentation checked on November 2, 2026. Free access has account/project quotas; it is not unlimited. The application never enables billing, switches providers or upgrades to a paid model automatically. Whether requests are free depends on the Google project's billing tier and available quota.

The existing OpenAI SDK is retained as a **client library** using Google's documented compatibility endpoint. In Gemini mode, requests and the Gemini key go to **Google**, not OpenAI. No OpenAI key or subscription is required.

## Executive summary for reviewers

This Python-based customer support agent was developed for the fictional Empório da Música store using the datasets supplied with Artefact's technical case. Dedicated tools retrieve product catalog entries, order information, and store policies. When configured with an API key, Google Gemini uses those tool results to compose grounded customer-facing answers in Brazilian Portuguese.

The implementation provides an interactive command-line interface, automated tests, and a deterministic offline demonstration. It does **not** include a web UI, live inventory integration, or production-grade customer authentication.

**Request flow:** customer message → agent → tool selection (`search_products`, `order_status`, or `search_policy`) → validation and retrieval from CSV/policy text → Brazilian Portuguese response.

See [GitHub publication and verification](PUBLICACAO_GITHUB.md) for repository contents, setup instructions, and the verification status.

## Quick start

Requires Python **3.10+** (tested with 3.12). From the project directory:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Then install:

```bash
python -m pip install -r requirements.txt
```

Try the deterministic demonstration without credentials:

```bash
python app.py --offline
```

For a natural conversation with Gemini, follow [COMECAR_AQUI.md](COMECAR_AQUI.md). In brief: create an API key at [Google AI Studio](https://aistudio.google.com/apikey), copy `.env.example` to `.env`, put the key in `GEMINI_API_KEY`, then run:

```bash
python app.py --check-api
python app.py
```

`--check-api` makes a real request asking for opening hours and checks that the relevant policy section was retrieved before a final answer. It exits with status 1 when that complete path is not confirmed. Ordinary startup says the provider is **configured**, not that an API call has already succeeded.

Type `/sair` to quit, `/limpar` to start a fresh conversation. Environment variables override `.env`. The `.env` file is loaded automatically from the project root and is excluded from version control and deliverable packaging. The distributed project contains no real API key.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `AI_PROVIDER` | `gemini` | `gemini`, `offline`, or explicitly `openai` |
| `GEMINI_API_KEY` | empty | Google key; `GOOGLE_API_KEY` is also accepted when the former is empty |
| `GEMINI_MODEL` | `gemini-3.1-flash-lite` | Configurable Gemini model identifier |
| `OPENAI_API_KEY` | empty | Used only when `AI_PROVIDER=openai` |
| `OPENAI_MODEL` | `gpt-4o-mini` | Used only when `AI_PROVIDER=openai`; this optional provider may incur charges |

With no Gemini key, the CLI explicitly labels its deterministic offline demonstration. An invalid configured key does **not** silently switch to offline or another provider. Authentication, model-access and quota errors receive actionable messages in Portuguese. Automatic SDK retries are disabled, there is a 30-second timeout per request and at most six model rounds per user turn.

## Architecture and choices

The CLI sends customer messages to an `Agent`. The LLM chooses from three tools, then writes a concise Portuguese answer using their results:

| Tool | Data source | Behavior |
| --- | --- | --- |
| `search_products` | Products, categories, promotions CSVs | Matches instrument categories and full model tokens, filters budget and promotions, checks status/stock, supports pagination and unavailable-model lookup |
| `order_status` | Orders and customers CSVs | Requires matching order ID and purchasing email; returns no details on mismatch |
| `search_policy` | Text extracted from the supplied PDF | Retrieves complete relevant sections with source, section and version metadata; excludes internal employee instructions |

**Hybrid retrieval:** structured CSV facts are retrieved directly instead of embedded. That keeps price calculations, inventory filters and order matching deterministic. For this small fixed policy manual, explicit topic aliases plus a lexical fallback are sufficient and easy to inspect. Topic aliases recognize verbs such as “devolver” and concepts such as “reembolso”; generic words such as “prazo” do not determine the answer on their own.

**Lightweight model:** Gemini Flash-Lite is aimed at low-cost, low-latency tasks and supports the tool calling needed for this assistant. Google's OpenAI-compatible endpoint lets the project reuse its existing agent loop and SDK while making the provider change explicit. The CLI is sufficient for the case's requested text interface.

**Prompt:** Brazilian Portuguese, friendly but professional; consult sources for store facts, retain context for follow-up messages, preserve requested model/budget/string count, avoid inventing stock or promises, request missing order identifiers and redirect unrelated questions. Policy answers should identify the relevant section. Internal document text and tool output are treated as data, not new instructions.

**History and errors:** conversation history stays in memory for the process; `/limpar` removes it. Model messages, including provider metadata such as thought signatures, are preserved during function-calling rounds. Tool arguments are validated and malformed calls receive tool-error responses so the model can correct them. A failed API/tool round does not commit a partially completed turn, preventing dangling tool calls from breaking later requests. Unexpected errors are sanitized rather than printing request content.

**Offline mode:** an explicitly limited rules demonstration, not generative AI. It uses the same product/order/policy tools, displays policy excerpts rather than hardcoded policy summaries, and supports collecting an order ID and email in separate messages. It does not handle arbitrary conversational references or recommendations; those belong to LLM mode.

## Data assumptions

- The CSV files are **snapshots**, not live stock, carrier tracking or checkout. Product answers ask customers to reconfirm current availability; order estimates are identified as recorded values.
- Only `status=active` products with positive stock are offered by default. Explicit unavailable-model queries can inspect out-of-stock, discontinued and coming-soon records without describing them as purchasable.
- Prices and discounts use `Decimal` with cent rounding. Only active promotion flags apply; if more than one active discount exists for a product, the highest applies, without stacking. Promotional prices show original price and discount percentage. PIX is not automatically stacked with promotions.
- Money parsing accepts `500,00`, `500.00`, `1.000,50` and `1,000.50`. A sole dot followed by exactly three digits is interpreted as a thousands separator, e.g. `1.000` means one thousand reais. Invalid and non-finite values are rejected.
- Model numbers and hyphenated identifiers are preserved. The search does not assume that an instrument has six strings when the supplied record does not establish that fact.
- Policies are from the supplied June 2025 version 2.1 PDF. The payment table and installment section contain differing minimum-installment conditions; ambiguous checkout cases are referred to staff.
- Order ID plus email reduces casual disclosure but is **not production authentication**. The supplied store/customer records are fictional case data. A real deployment should authenticate customers, restrict access and keep private datasets outside a public repository.

## Validation and examples

Run all tests without an API key or network calls:

```bash
python -m unittest discover -s tests -v
```

The suite covers exact model matching, short identifiers, monetary formats, valid and expired promotions, unavailable products, policy selection, multi-message order identification, rejected credentials, provider configuration, malformed tool arguments, API errors, iteration limits, history recovery and provider metadata preservation.

The supplied project documentation reports a previous local run with **61 tests passed**. This was not independently reproduced during the latest repository documentation update; see the [verification status](PUBLICACAO_GITHUB.md) for the checks performed in that session. The offline CLI was also exercised with multiple messages and `/limpar`.

`tests/test_llm.py` uses the **real installed OpenAI SDK and HTTP serialization** against an in-memory `httpx.MockTransport`. Google responses are simulated. These tests verify the client protocol, routing and tool integration; they do **not** establish the real Gemini model's reasoning quality, credentials or quota.

The five files in `examples/` document reproducible offline demonstrations. They cover budget filtering with decimal-dot notation, a seven-string instrument, active promotions, a refund-policy question and order verification across two messages. Regenerate them with:

```bash
python scripts/generate_examples.py
```

**Live Gemini validation remains pending** until the candidate supplies a local key and runs `python app.py --check-api`, then manually tests a catalog conversation, follow-up references, an order lookup and an out-of-scope question. No live LLM transcripts are claimed or fabricated.

## Limitations and next steps

- Lexical retrieval still has limited typo/synonym coverage. Evaluate it against a larger set of real questions before adding full-text or semantic retrieval.
- No live inventory/order integration, transactions, web UI, identity provider or escalation-ticket system is implemented.
- Prompt rules guide model behavior but cannot guarantee that a small LLM always calls the right tool or interprets policies correctly. Live conversation evaluation is still required.
- History is not persisted and has no summarization/windowing for very long sessions.
- Free-tier availability, quotas, model lifecycle and Google's data-use terms can change. Check the linked documentation and your project's dashboard before running the demonstration.

## AI-assisted development disclosure

OpenAI ChatGPT was used to inspect the case materials, propose the architecture, generate the initial implementation, review it, implement the Gemini configuration and regression fixes, draft documentation and run local validation. The candidate should review the code, reproduce the results, configure credentials locally and explain these choices during the interview. No claim is made that the work was authored or tested independently or that a live Google call has already succeeded.

## Submission checklist

- [ ] Review the implementation and the AI-use disclosure personally.
- [ ] Run the test suite on your machine.
- [ ] Configure a local Gemini key and validate the real tool-calling conversation.
- [ ] Record representative real LLM examples after validation, replacing offline examples as appropriate while retaining 3–5 conversations.
- [ ] Confirm case-data publication permissions before creating the public repository.
- [ ] Create the public GitHub repository with genuine incremental commits; do not fabricate development history.
- [ ] Follow the recruitment email's delivery instructions and deadline. Do not change the repository after submission.

## Official provider references

Checked November 2, 2026:

- [Gemini 3.1 Flash-Lite capabilities](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite)
- [Pricing and free tier](https://ai.google.dev/gemini-api/docs/pricing)
- [OpenAI SDK compatibility and function calling](https://ai.google.dev/gemini-api/docs/openai)
- [API key setup](https://ai.google.dev/gemini-api/docs/api-key)
- [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
