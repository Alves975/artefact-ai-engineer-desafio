# Publicação e validação do desafio Artefact

Repositório público de entrega técnica: https://github.com/Alves975/artefact-ai-engineer-desafio

## Instalação

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python app.py --offline
```

Para conectar ao Google Gemini, copie `.env.example` para `.env`, preencha `GEMINI_API_KEY` e execute `python app.py --check-api`.

## Segurança

Não publique `.env` real, credenciais, chaves ou dados privados. O arquivo `.env.example` contém apenas um modelo de configuração.

## Status de publicação

O repositório foi inicialmente criado parcialmente. Antes de enviar para avaliação, confirme que `src/agent.py`, todos os CSVs de `data/`, o texto de políticas e todos os testes existem no GitHub. Os exemplos publicados descrevem execuções offline anteriores; eles não certificam que a versão parcial do repositório funciona.

O PDF do enunciado original não precisa ser publicado. Consulte os direitos de distribuição dos dados do desafio.
