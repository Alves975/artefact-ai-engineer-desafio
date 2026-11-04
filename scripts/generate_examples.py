"""Regenerate the five real, deterministic offline transcripts."""
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from src.agent import Agent


def main():
    examples = [
        ('Budget filtering', ['Quais opções de violões disponíveis custando até R$500.00?'],
         'The decimal-dot budget remains R$500, and only products within that ceiling are returned.'),
        ('Seven-string instrument', ['Tem violão de 7 cordas?'],
         'An instrument with seven strings is recognized as a product rather than a separate accessory.'),
        ('Active promotions', ['Quais produtos estão em promoção?'],
         'Only active promotion flags are used, with original price, promotional price and discount percent.'),
        ('Refund policy', ['Qual o prazo para reembolso?'],
         'The returns section is retrieved from the supplied policy text instead of shipping policies.'),
    ]
    agent = Agent(provider='offline', env_file=None)
    order = agent.store.orders[0]
    owner = next(c for c in agent.store.customers if c['customer_id'] == order['customer_id'])
    examples.append(('Order lookup over two messages',
                     ['Qual o status do pedido ' + order['order_id'] + '?', 'Meu e-mail é ' + owner['email']],
                     'No order detail is shown until the supplied ID and purchasing email match the fictional customer dataset.'))
    output = BASE / 'examples'
    output.mkdir(exist_ok=True)
    for index, (title, queries, explanation) in enumerate(examples, 1):
        agent = Agent(provider='offline', env_file=None)
        lines = [f'# Interaction {index}: {title}', '',
                 '**Execution mode:** real deterministic offline run; no LLM call or generated transcript.', '']
        for query in queries:
            lines.extend(['**Customer (Portuguese):** ' + query, '', '**Assistant (Portuguese):**', '',
                          agent.respond(query), ''])
        lines.extend(['**Why this matters:** ' + explanation, ''])
        (output / f'interaction_{index:02}.md').write_text('\n'.join(lines), encoding='utf-8')
    print('Updated five reproducible offline examples.')


if __name__ == '__main__':
    main()
