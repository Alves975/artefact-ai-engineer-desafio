"""Behavioral regressions reproduced during the review."""
import unittest
from decimal import Decimal

from src.agent import Agent, Store, parse_amount


class RetrievalRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = Store()

    def test_currency_formats_keep_budget(self):
        for text, expected in [('500.00', '500'), ('500,00', '500'), ('1.000', '1000'),
                               ('1.000,50', '1000.50'), ('1,000.50', '1000.50'), ('500', '500')]:
            with self.subTest(text=text):
                self.assertEqual(parse_amount(text), Decimal(expected))

    def test_invalid_budgets_rejected(self):
        for value in [True, -1, float('nan'), float('inf'), 'abc', '1,2,3']:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_amount(value)

    def test_decimal_dot_ceiling_in_sentence(self):
        result = self.store.search_products('Quais opções de violões disponíveis custando até R$500.00?')
        self.assertEqual({p['id'] for p in result}, {'83', '85'})

    def test_sentence_punctuation_is_not_part_of_budget(self):
        result = self.store.search_products('Quero um violão até R$500.')
        self.assertEqual({p['id'] for p in result}, {'83', '85'})

    def test_natural_catalog_question(self):
        result = self.store.search_products('Quais violões vocês têm?')
        self.assertTrue(result)
        self.assertTrue(all(p['category'] == 'Violões' for p in result))

    def test_preserves_kit_number(self):
        result = self.store.search_products('Qual o preço da bateria Yamaha Kit 1?')
        self.assertEqual([p['id'] for p in result], ['139'])

    def test_preserves_hyphenated_model(self):
        self.assertEqual(self.store.search_products('Giannini GF-3D'), [])
        result = self.store.search_products('Giannini GF-3D', include_unavailable=True)
        self.assertEqual([p['id'] for p in result], ['96'])
        self.assertFalse(result[0]['available'])

    def test_discontinued_model_with_positive_stock_not_for_sale(self):
        self.assertEqual(self.store.search_products('Ibanez Bass 2X'), [])
        result = self.store.search_products('Ibanez Bass 2X', include_unavailable=True)
        self.assertEqual([p['id'] for p in result], ['136'])
        self.assertEqual(result[0]['status'], 'discontinued')
        self.assertFalse(result[0]['available'])

    def test_seven_strings_are_not_six(self):
        result = self.store.search_products('violão de 7 cordas')
        self.assertEqual({p['id'] for p in result}, {'109', '110', '111', '112'})

    def test_active_promotions_only(self):
        result = self.store.search_products('Quais produtos estão em promoção?')
        self.assertEqual({p['id'] for p in result}, {'90', '94', '121', '127'})
        self.assertTrue(all(p['discount_percent'] > 0 for p in result))

    def test_exact_promotion_price(self):
        result = self.store.search_products('Crafter HT-100')[0]
        self.assertEqual(result['regular_price_brl'], 'R$ 2.399,00')
        self.assertEqual(result['price_brl'], 'R$ 1.967,18')
        self.assertEqual(result['discount_percent'], 18)

    def test_inactive_promotion_is_not_applied(self):
        result = self.store.search_products('Takamine GD20')[0]
        self.assertEqual(result['discount_percent'], 0)
        self.assertEqual(result['price_brl'], 'R$ 2.199,00')

    def test_promotion_filter_combines_with_price(self):
        result = self.store.search_products('', max_price=400, on_sale=True)
        self.assertEqual([p['id'] for p in result], ['127'])

    def test_pagination_returns_new_products(self):
        first = self.store.search_products('violão', limit=3)
        second = self.store.search_products('violão', limit=3, offset=3)
        self.assertEqual(len(first), 3)
        self.assertEqual(len(second), 3)
        self.assertFalse({p['id'] for p in first} & {p['id'] for p in second})

    def test_refund_question_retrieves_returns_not_shipping(self):
        result = self.store.search_policy('Qual o prazo para reembolso?')
        self.assertEqual([p['section'] for p in result], ['4'])
        self.assertIn('10 dias úteis', result[0]['excerpt'])

    def test_devolver_verb_retrieves_returns(self):
        self.assertEqual([p['section'] for p in self.store.search_policy('Quero devolver')], ['4'])

    def test_policy_response_cites_source(self):
        result = self.store.search_policy('troca')[0]
        self.assertEqual(result['source'], 'políticas_da_loja.pdf')
        self.assertTrue(result['version'])

    def test_policy_query_can_retrieve_multiple_topics(self):
        self.assertEqual({p['section'] for p in self.store.search_policy('pagamento e frete')}, {'3', '5'})

    def test_no_internal_employee_instructions_returned(self):
        result = self.store.search_policy('WhatsApp')[0]
        self.assertNotIn('Tom de voz:', result['excerpt'])
        self.assertNotIn('Fluxo de Atendimento Padrão', result['excerpt'])
        self.assertIn('24 horas úteis', result['excerpt'])

    def test_general_time_word_does_not_return_arbitrary_policies(self):
        self.assertEqual(self.store.search_policy('prazo'), [])


class OfflineRegressions(unittest.TestCase):
    def setUp(self):
        self.agent = Agent(provider='offline', env_file=None)

    def test_seven_string_instrument_not_accessory(self):
        answer = self.agent.respond('Tem violão de 7 cordas?')
        self.assertIn('Tagima TW-7', answer)
        self.assertNotIn('não com acessórios', answer)

    def test_separate_strings_still_out_of_scope(self):
        answer = self.agent.respond('Vocês vendem cordas para violão?')
        self.assertIn('não com acessórios', answer)

    def test_preserves_budget_in_rendered_answer(self):
        answer = self.agent.respond('Quais opções de violões disponíveis custando até R$500.00?')
        self.assertIn('R$ 429,90', answer)
        self.assertNotIn('R$ 549,00', answer)

    def test_policy_answer_is_retrieved_not_hardcoded(self):
        self.agent.store.policies = [{'section': '4', 'title': 'Política de Trocas',
                                     'text': '4.1 Direito de Arrependimento\nFixture atualizada: prazo de teste.'}]
        answer = self.agent.respond('Quero devolver')
        self.assertIn('Fixture atualizada', answer)
        self.assertNotIn('10 dias úteis', answer)

    def test_two_turn_order_lookup(self):
        order = self.agent.store.orders[0]
        owner = next(c for c in self.agent.store.customers if c['customer_id'] == order['customer_id'])
        first = self.agent.respond('Qual o status do pedido ' + order['order_id'] + '?')
        self.assertIn('e-mail', first)
        second = self.agent.respond('Meu e-mail é ' + owner['email'])
        self.assertIn('Pedido #' + order['order_id'], second)
        self.assertIn(order['status'], second)

    def test_wrong_email_does_not_disclose_order(self):
        answer = self.agent.respond('pedido 1, e-mail wrong@example.com')
        self.assertIn('Não consegui validar', answer)
        self.assertNotIn('Rastreamento:', answer)

    def test_changing_order_requires_email_again(self):
        self.agent.respond('pedido 1 wrong@example.com')
        answer = self.agent.respond('pedido 2')
        self.assertIn('envie o número', answer)
        self.assertNotIn('Rastreamento:', answer)

    def test_reset_clears_pending_lookup_and_history(self):
        self.agent.respond('pedido 1')
        self.agent.reset()
        self.assertEqual(len(self.agent.messages), 1)
        answer = self.agent.respond('wrong@example.com')
        self.assertNotIn('Rastreamento:', answer)

    def test_discontinued_model_is_identified(self):
        answer = self.agent.respond('Qual o preço do violão descontinuado Shelby SN-7C?')
        self.assertIn('Shelby SN-7C', answer)
        self.assertIn('indisponível', answer)

    def test_unknown_model_has_no_invented_price(self):
        answer = self.agent.respond('Quanto custa o Yamaha MODELO-INEXISTENTE?')
        self.assertIn('Não encontrei', answer)
        self.assertNotIn('R$', answer)


if __name__ == '__main__':
    unittest.main()