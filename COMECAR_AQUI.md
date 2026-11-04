# Conversar com o Gemini

O projeto já está preparado para o **Gemini 3.1 Flash-Lite**, um modelo leve para conversas e consultas às ferramentas. Ele possui opção gratuita com limites de uso. A gratuidade depende do plano e da cota do projeto no Google; não é acesso ilimitado.

## 1. Criar a chave

1. Abra [Google AI Studio — chaves de API](https://aistudio.google.com/apikey).
2. Entre na sua conta Google e aceite os termos, se solicitado.
3. Use **Criar chave de API / Create API key**. Se já existir uma chave no projeto padrão, também pode usá-la. Se precisar, crie um projeto pelo próprio painel.
4. Para experimentar a opção gratuita, mantenha um projeto no nível gratuito. Ativar faturamento não é necessário para o teste gratuito desse modelo.
5. Copie a chave para o arquivo local descrito abaixo. **Não precisa enviar a chave pelo chat.**

## 2. Instalar e configurar no computador

Extraia o ZIP e abra o terminal dentro da pasta `artefact_agent_project`, onde estão `app.py` e `requirements.txt`.

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Usar o executável da pasta `.venv` dispensa ativar scripts do PowerShell. Se `python` não for encontrado, tente `py` no primeiro comando ou instale o Python 3.10 ou superior.

No arquivo aberto, deixe estas linhas e cole sua chave depois de `GEMINI_API_KEY=`:

```dotenv
AI_PROVIDER=gemini
GEMINI_API_KEY=COLE_SUA_CHAVE_AQUI
GEMINI_MODEL=gemini-3.1-flash-lite
```

Salve o arquivo como **`.env`**, na mesma pasta de `app.py`. O nome não pode terminar em `.txt`. O arquivo de exemplo é apenas um modelo: a chave real deve ficar no `.env`.

No macOS/Linux, a instalação equivalente é:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` com seu editor e preencha as mesmas três linhas.

## 3. Testar a conexão e conversar

Windows:

```powershell
.\.venv\Scripts\python.exe app.py --check-api
.\.venv\Scripts\python.exe app.py
```

macOS/Linux:

```bash
.venv/bin/python app.py --check-api
.venv/bin/python app.py
```

O primeiro comando faz uma consulta real sobre os horários e verifica o caminho IA → ferramenta de políticas → resposta. O segundo abre a conversa.

Experimente, em sequência:

1. `Quais violões vocês têm até R$ 500?`
2. `E de 7 cordas, quais vocês têm?`
3. `Quais produtos estão em promoção?`
4. `Qual o prazo para reembolso?`
5. `Qual o status do pedido 1?` — informe o e-mail correspondente ao cliente fictício quando o assistente pedir.

Use `/limpar` para começar uma nova conversa e `/sair` para encerrar.

## Se aparecer um erro

| Mensagem | O que fazer |
| --- | --- |
| Demonstração offline | Confira o nome `.env`, sua localização e a linha `GEMINI_API_KEY`. Feche e abra o programa novamente. |
| A IA não autorizou o acesso | Confira se a chave foi copiada inteira e se o projeto tem permissão para usar a API Gemini. |
| Modelo não disponível | Confira os modelos disponíveis para sua chave no AI Studio e ajuste `GEMINI_MODEL` para um modelo com opção gratuita. |
| Limite de uso atingido | Confira a cota no painel e aguarde a liberação. Se a cota for zero, revise a disponibilidade do nível gratuito para o projeto/modelo. O programa não ativa cobrança nem troca de provedor. |
| Falha de conexão | Confira a internet e tente novamente. A conversa anterior permanece preservada. |

Para testar sem chave nem internet, use `app.py --offline`. Esse modo é uma demonstração por regras; a conversa natural exige a chave do Gemini.

Depois de testar, pode informar somente se funcionou ou copiar a mensagem de erro. Não inclua a chave em mensagens ou capturas de tela.
