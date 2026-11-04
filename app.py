"""Portuguese CLI: python app.py; python app.py --offline; --check-api."""
from __future__ import annotations

import argparse
import json

from src.agent import Agent


def main() -> int:
    parser = argparse.ArgumentParser(description='Assistente da Empório da Música')
    parser.add_argument('--offline', action='store_true', help='Demonstração sem IA nem chamadas externas')
    parser.add_argument('--check-api', action='store_true', help='Faz uma consulta real curta para verificar a conexão com a IA')
    args = parser.parse_args()
    try:
        agent = Agent(provider='offline' if args.offline else None)
    except (RuntimeError, ValueError) as exc:
        print(str(exc))
        return 1
    print('Empório da Música | /sair para encerrar | /limpar para nova conversa')
    if agent.client:
        print(f'Modo: IA configurada via {agent.provider} | Modelo: {agent.model}')
    else:
        print('Modo: demonstração offline, sem IA. Configure GEMINI_API_KEY no .env para conversar com o Gemini.')
    if args.check_api:
        if not agent.client:
            print('A conexão ainda não foi testada: falta configurar a chave ou selecionar o provedor.')
            return 1
        answer = agent.respond('Qual o horário de funcionamento da loja? Consulte a política antes de responder.')
        print('Assistente:', answer)
        policy_retrieved = False
        for message in agent.messages:
            if message.get('role') == 'tool':
                payload = json.loads(message['content'])
                if isinstance(payload, list) and any(isinstance(p, dict) and p.get('section') == '2' for p in payload):
                    policy_retrieved = True
        succeeded = policy_retrieved and agent.messages[-1].get('role') == 'assistant'
        print('Consulta com ferramenta concluída.' if succeeded else 'A consulta com ferramenta ainda não foi confirmada.')
        return 0 if succeeded else 1
    while True:
        try:
            prompt = input('Você: ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if prompt.casefold() in {'/exit', '/quit', '/sair', 'sair'}:
            break
        if prompt.casefold() in {'/limpar', '/reset'}:
            agent.reset()
            print('Assistente: Nova conversa iniciada.')
        elif prompt:
            print('Assistente:', agent.respond(prompt))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
