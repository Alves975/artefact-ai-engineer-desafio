"""Real SDK and HTTP serialization; provider responses are simulated, not live."""
import json
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout

import httpx
from openai import OpenAI

from src.agent import Agent
from src.config import DEFAULT_GEMINI_MODEL, GEMINI_BASE_URL, Settings


def tool_call(name='search_products', args='{"query":"Takamine GD20"}', call_id='call_1'):
    return {'id': call_id, 'type': 'function', 'function': {'name': name, 'arguments': args}}


def completion(content=None, calls=None):
    message = {'role': 'assistant', 'content': content}
    if calls:
        message['tool_calls'] = calls
    return {'id': 'test-completion', 'object': 'chat.completion', 'created': 0,
            'model': DEFAULT_GEMINI_MODEL,
            'choices': [{'index': 0, 'finish_reason': 'tool_calls' if calls else 'stop', 'message': message}]}


class ScriptedAPI:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def __call__(self, request):
        self.requests.append({'url': str(request.url), 'auth': request.headers.get('authorization'),
                              'body': json.loads(request.content)})
        result = next(self.responses)
        if isinstance(result, Exception):
            raise result
        status, body = result if isinstance(result, tuple) else (200, result)
        return httpx.Response(status, json=body)


class LLMConversationTests(unittest.TestCase):
    def make_agent(self, responses):
        api = ScriptedAPI(responses)
        http_client = httpx.Client(transport=httpx.MockTransport(api))
        client = OpenAI(api_key='test-only-not-a-real-key', base_url=GEMINI_BASE_URL,
                        http_client=http_client, max_retries=0)
        self.addCleanup(client.close)
        agent = Agent(provider='gemini', client=client, env_file=None)
        return agent, api

    def test_gemini_endpoint_and_tool_round_trip(self):
        agent, api = self.make_agent([completion(calls=[tool_call()]), completion('Resposta simulada')])
        self.assertEqual(agent.respond('Quanto custa o Takamine GD20?'), 'Resposta simulada')
        self.assertEqual(len(api.requests), 2)
        first = api.requests[0]
        self.assertEqual(first['url'], GEMINI_BASE_URL + 'chat/completions')
        self.assertEqual(first['auth'], 'Bearer test-only-not-a-real-key')
        self.assertEqual(first['body']['model'], DEFAULT_GEMINI_MODEL)
        second = api.requests[1]['body']['messages']
        result = json.loads(second[-1]['content'])
        self.assertEqual(second[-1]['role'], 'tool')
        self.assertEqual(result[0]['name'], 'Takamine GD20 Dreadnought Natural')
        self.assertEqual(result[0]['price_brl'], 'R$ 2.199,00')

    def test_follow_up_retains_previous_messages(self):
        agent, api = self.make_agent([completion('Olá!'), completion('Tudo certo.')])
        agent.respond('Oi')
        agent.respond('Você lembra do meu oi?')
        messages = api.requests[1]['body']['messages']
        self.assertEqual([m['role'] for m in messages], ['system', 'user', 'assistant', 'user'])
        self.assertEqual(messages[1]['content'], 'Oi')

    def test_invalid_calls_get_complete_tool_responses(self):
        calls = [tool_call(args='{"query":null}', call_id='null'),
                 tool_call(args='{invalid', call_id='json'),
                 tool_call(args='[]', call_id='array'),
                 tool_call(name='read_all_customers', args='{}', call_id='unknown'),
                 tool_call(args='{"query":"violão","extra":true}', call_id='extra')]
        agent, api = self.make_agent([completion(calls=calls), completion('Vou reformular a consulta.')])
        self.assertEqual(agent.respond('Busque um instrumento'), 'Vou reformular a consulta.')
        returned = [m for m in api.requests[1]['body']['messages'] if m['role'] == 'tool']
        self.assertEqual({m['tool_call_id'] for m in returned}, {c['id'] for c in calls})
        self.assertTrue(all('error' in json.loads(m['content']) for m in returned))

    def test_model_can_correct_bad_arguments(self):
        agent, api = self.make_agent([
            completion(calls=[tool_call(args='{"query":null}')]),
            completion(calls=[tool_call(call_id='corrected')]), completion('Consulta concluída.')])
        self.assertEqual(agent.respond('Quanto custa o Takamine?'), 'Consulta concluída.')
        self.assertEqual(len(api.requests), 3)
        result = json.loads(api.requests[2]['body']['messages'][-1]['content'])
        self.assertEqual(result[0]['id'], '95')

    def test_provider_extras_survive_serialization(self):
        call = tool_call()
        call['extra_content'] = {'google': {'thought_signature': 'test-signature'}}
        agent, api = self.make_agent([completion(calls=[call]), completion('Resposta')])
        agent.respond('Preço?')
        request_messages = api.requests[1]['body']['messages']
        assistant = next(m for m in request_messages if m.get('tool_calls'))
        self.assertEqual(assistant['tool_calls'][0]['extra_content']['google']['thought_signature'], 'test-signature')

    def test_rate_limit_mid_turn_rolls_back_only_failed_turn(self):
        agent, api = self.make_agent([
            completion('Olá!'), completion(calls=[tool_call()]),
            (429, {'error': {'message': 'test-only-secret', 'type': 'rate_limit_error'}}),
            completion('Podemos continuar.')])
        agent.respond('Oi')
        history = list(agent.messages)
        failure = agent.respond('Preço?')
        self.assertIn('limite de uso', failure)
        self.assertNotIn('test-only-secret', failure)
        self.assertEqual(agent.messages, history)
        self.assertEqual(len(api.requests), 3)  # No automatic retries consume quota.
        self.assertEqual(agent.respond('Tente de novo'), 'Podemos continuar.')
        self.assertFalse(any(m.get('tool_calls') for m in api.requests[-1]['body']['messages']))

    def test_invalid_api_key_has_safe_actionable_error(self):
        agent, api = self.make_agent([(401, {'error': {'message': 'private detail', 'type': 'authentication_error'}})])
        answer = agent.respond('Oi')
        self.assertIn('.env', answer)
        self.assertNotIn('private detail', answer)
        self.assertEqual(len(agent.messages), 1)

    def test_unavailable_model_does_not_fall_back_to_paid_provider(self):
        agent, api = self.make_agent([(404, {'error': {'message': 'model unavailable', 'type': 'not_found_error'}})])
        answer = agent.respond('Oi')
        self.assertIn('não está disponível', answer)
        self.assertEqual(len(api.requests), 1)
        self.assertEqual(agent.provider, 'gemini')

    def test_unexpected_tool_failure_leaves_history_usable(self):
        agent, api = self.make_agent([completion(calls=[tool_call()]), completion('Retomando.')])
        with patch.object(agent.store, 'search_products', side_effect=RuntimeError('private internal data')):
            answer = agent.respond('Preço?')
        self.assertNotIn('private internal data', answer)
        self.assertEqual(len(agent.messages), 1)
        self.assertEqual(agent.respond('Vamos continuar'), 'Retomando.')

    def test_max_iterations_does_not_keep_unresolved_calls(self):
        agent, api = self.make_agent([completion(calls=[tool_call(call_id=str(i))]) for i in range(6)])
        answer = agent.respond('Consulte repetidamente')
        self.assertIn('Não consegui finalizar', answer)
        self.assertEqual([m['role'] for m in agent.messages], ['system', 'user', 'assistant'])

    def test_tool_orders_require_matching_customer_email(self):
        agent, api = self.make_agent([
            completion(calls=[tool_call('order_status', '{"order_id":"1","email":"wrong@example.com"}')]),
            completion('Confira seu número e e-mail.')])
        agent.respond('Consultar pedido 1')
        result = json.loads(api.requests[1]['body']['messages'][-1]['content'])
        self.assertIn('error', result)
        self.assertNotIn('tracking_code', result)

    def test_cli_connection_check_confirms_policy_tool_round_trip(self):
        import app
        agent, api = self.make_agent([
            completion(calls=[tool_call('search_policy', '{"topic":"horário"}')]),
            completion('Segunda a sexta, das 9h às 18h.')])
        output = io.StringIO()
        with patch('sys.argv', ['app.py', '--check-api']), patch('app.Agent', return_value=agent), redirect_stdout(output):
            result = app.main()
        self.assertEqual(result, 0)
        self.assertIn('Consulta com ferramenta concluída.', output.getvalue())

    def test_cli_check_does_not_report_success_without_policy_lookup(self):
        import app
        agent, api = self.make_agent([completion('Resposta sem consulta.')])
        output = io.StringIO()
        with patch('sys.argv', ['app.py', '--check-api']), patch('app.Agent', return_value=agent), redirect_stdout(output):
            result = app.main()
        self.assertEqual(result, 1)
        self.assertIn('ainda não foi confirmada', output.getvalue())


class ConfigurationTests(unittest.TestCase):
    def test_default_is_gemini_with_free_tier_model(self):
        with patch.dict(os.environ, {}, clear=True):
            config = Settings.from_env(env_file=None)
        self.assertEqual(config.provider, 'gemini')
        self.assertEqual(config.model, 'gemini-3.1-flash-lite')
        self.assertEqual(config.base_url, GEMINI_BASE_URL)

    def test_missing_gemini_key_does_not_use_openai_key(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'not-a-real-key'}, clear=True):
            agent = Agent(env_file=None)
        self.assertIsNone(agent.client)
        self.assertEqual(agent.provider, 'gemini')

    def test_dotenv_loads_key_and_model(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {}, clear=True):
            path = Path(temp) / '.env'
            path.write_text('AI_PROVIDER=gemini\nGEMINI_API_KEY=test-only-key\nGEMINI_MODEL=test-model\n')
            config = Settings.from_env(env_file=path)
            self.assertEqual(config.api_key, 'test-only-key')
            self.assertEqual(config.model, 'test-model')

    def test_environment_wins_over_dotenv(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {'GEMINI_MODEL': 'external-model'}, clear=True):
            path = Path(temp) / '.env'
            path.write_text('GEMINI_MODEL=file-model\n')
            self.assertEqual(Settings.from_env(env_file=path).model, 'external-model')

    def test_explicit_offline_never_constructs_network_client(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-only-key'}, clear=True):
            agent = Agent(provider='offline', env_file=None)
        self.assertIsNone(agent.client)

    def test_openai_is_explicit_opt_in(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-only-key'}, clear=True):
            config = Settings.from_env(provider='openai', env_file=None)
        self.assertEqual(config.provider, 'openai')
        self.assertEqual(config.api_key, 'test-only-key')

    def test_placeholder_is_not_treated_as_key(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'cole_sua_chave_aqui'}, clear=True):
            self.assertFalse(Settings.from_env(env_file=None).api_key)


if __name__ == '__main__':
    unittest.main()