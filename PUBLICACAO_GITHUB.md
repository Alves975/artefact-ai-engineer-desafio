# Publicação e validação — Desafio Artefact

**Repositório:** https://github.com/Alves975/artefact-ai-engineer-desafio

O repositório está criado e os 26 arquivos de código, configuração, testes, exemplos e dados necessários à aplicação foram publicados. O PDF original `data/políticas_da_loja.pdf` **não foi incluído**: o agente utiliza `data/policies_extracted.txt`, que já está no repositório. Se a empresa exigir o PDF original, ele precisará ser anexado separadamente, após confirmar permissão para redistribuí-lo.

## Executar localmente

Requisitos: Python 3.10 ou superior.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python app.py --offline
```

Para usar o Google Gemini, copie `.env.example` para `.env`, configure `GEMINI_API_KEY` e execute `python app.py --check-api`. A chave não deve ser enviada ao GitHub.

## Estado da validação

- Compilação sintática com `python -m compileall -q app.py src tests scripts`: **aprovada** em 4 de novembro de 2026.
- Demonstração offline usando o catálogo: **aprovada**.
- 41 testes unitários e de regressão (sem o SDK externo): **aprovados**.
- Testes completos com SDK OpenAI e serialização simulada: **não executados nesta sessão**. A dependência `openai` não estava instalada no ambiente e não havia acesso à rede para instalá-la.
- Chamada externa real ao Gemini: **não verificada nesta sessão**; exige chave de API e acesso à rede.

Esta documentação relata apenas validações efetivamente executadas. Não equipare a disponibilidade dos arquivos à aprovação dos testes completos.
