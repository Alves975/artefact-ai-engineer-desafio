# Empório da Música — AI Customer Support Agent

> Desafio técnico de AI Engineer / Full-Stack para Aplicações com IA Generativa — Artefact.

Assistente de atendimento em **Python** para uma loja fictícia de instrumentos musicais. O objetivo é responder a perguntas sobre o catálogo, pedidos e políticas comerciais com **Google Gemini e chamadas de ferramentas (function calling)**, usando arquivos locais fornecidos no desafio como fonte de dados.

## Funcionalidades

- Busca de instrumentos por nome, categoria, termos e faixa de preço.
- Consulta de promoções e precificação.
- Verificação de pedidos com conferência dos dados do cliente.
- Recuperação de políticas da loja (entrega, trocas, horário, pagamento e garantia).
- Conversa em português no terminal e demonstração determinística **offline**.
- Tratamento de configurações por variáveis de ambiente e testes automatizados.

## Arquitetura

```text
Cliente (terminal/CLI)
  -> app.py
    -> src/agent.py (orquestração)
       -> Gemini via OpenAI-compatible API (opcional)
       -> Ferramentas de catálogo, pedidos e políticas
          -> data/*.csv e data/policies_extracted.txt
    -> resposta em português
```

O aplicativo **não tem site ou interface gráfica**, banco de dados remoto, estoque em tempo real nem implantação em produção. Os arquivos CSV representam o conjunto de dados do exercício.

## Tecnologias

Python 3.10+, Google Gemini (modelo configurável), SDK OpenAI como cliente para endpoint compatível do Google, python-dotenv, CSV e unittest.

## Instalação

```bash
git clone https://github.com/Alves975/artefact-ai-engineer-desafio.git
cd artefact-ai-engineer-desafio
python -m venv .venv
# Windows:
.venv\Scripts\python.exe -m pip install -r requirements.txt
# Linux / macOS:
# .venv/bin/python -m pip install -r requirements.txt
```

**Sem chave de API:** `python app.py --offline`

**Conversação com IA:** copie `.env.example` para `.env`, configure `GEMINI_API_KEY` obtida no [Google AI Studio](https://aistudio.google.com/apikey) e execute:

```bash
python app.py --check-api
python app.py
```

Comandos no terminal: `/limpar` inicia conversa nova e `/sair` encerra a sessão.

## Testes

```bash
python -m unittest discover -s tests -v
```

A execução offline não depende de credenciais. Testes que dependem da API externa exigem uma chave válida, internet e cota disponível. Não interprete a presença de testes como comprovação de que todos foram executados neste repositório.

## Segurança e limitações

- Nunca versionar `.env` ou chaves de API.
- Dados de pedidos devem ser consultados somente após checagem da identidade do cliente.
- Não inventar produtos, preços ou informações de políticas não encontradas.
- Diferenciar informações estáticas de disponibilidade atual.
- Revalidar cotas, versão do modelo e custos na documentação do Google.

## Estrutura do projeto

```text
app.py                  CLI
src/config.py           Configuração dos provedores
src/agent.py            Agente e ferramentas da loja
data/                   Catálogo e documentos de apoio
tests/                  Testes
examples/               Conversas demonstrativas
.env.example            Modelo de configuração
COMECAR_AQUI.md         Guia detalhado de execução
```

**Observação sobre dados do desafio:** antes de compartilhar ou reutilizar dados fornecidos pela empresa, verifique as permissões de divulgação. Este repositório é uma entrega de exercício técnico e não representa integração comercial real com a loja.

## Autor

Desafio técnico preparado para avaliação na Artefact.
