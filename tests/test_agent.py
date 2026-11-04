import unittest
from src.agent import Store, Agent, policy_sections

class AgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = Store()

    def test_catalog_loaded(self):
        self.assertEqual(len(self.store.products), 65)

    def test_active_stock_only(self):
        self.assertTrue(all(x['stock_quantity'] > 0 for x in self.store.search_products('violão')))

    def test_price_ceiling(self):
        products = self.store.search_products('violão', max_price=1000)
        self.assertTrue(products)
        for p in products:
            price = float(p['price_brl'].replace('R$ ', '').replace('.', '').replace(',', '.'))
            self.assertLessEqual(price, 1000)

    def test_promotion_source(self):
        p = next(p for p in self.store.products
                 if any(x['product_id'] == p['product_id'] and x['is_active'] == '1'
                        for x in self.store.promotions))
        _, pct = self.store.effective_price(p)
        self.assertGreater(pct, 0)

    def test_order_privacy(self):
        self.assertIn('error', self.store.order_status('1', 'wrong@example.com'))
        self.assertIn('error', self.store.order_status('9999', 'test@example.com'))

    def test_order_owner(self):
        order = self.store.orders[0]
        owner = next(c for c in self.store.customers
                     if c['customer_id'] == order['customer_id'])
        self.assertEqual(self.store.order_status(order['order_id'], owner['email'])['order_id'],
                         order['order_id'])

    def test_policy_extraction(self):
        self.assertEqual(len(policy_sections()), 10)
        self.assertTrue(self.store.search_policy('devolução'))

    def test_out_of_scope(self):
        self.assertIn('instrumentos musicais',
                      Agent(self.store, provider='offline').offline_respond('Faça minha declaração de imposto'))

    def test_no_order_without_email(self):
        self.assertIn('e-mail', Agent(self.store, provider='offline').offline_respond('Qual o status do pedido 1?'))

    def test_closed_hours(self):
        answer = Agent(self.store, provider='offline').offline_respond('Qual o horário?')
        self.assertIn('sábado', answer.casefold())
        self.assertIn('09:00 às 13:00', answer)

    def test_no_accessory(self):
        self.assertIn('não com acessórios',
                      Agent(self.store, provider='offline').offline_respond('Vocês vendem palhetas?'))

if __name__ == '__main__':
    unittest.main()
