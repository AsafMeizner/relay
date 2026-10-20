import unittest
from relay.evidence import Source
from relay.workflow import Incident, ModelClient
import json

class WorkflowTests(unittest.TestCase):
    def client(self, quote='errors 12%'):
        brief = {'claims': [{'text': 'Errors observed', 'citations': [{'source_id': 'log', 'quote': quote}]}], 'open_questions': ['Cause?'], 'suggested_actions': ['Investigate deployment']}
        def transport(payload):
            self.assertEqual(payload['messages'][0]['role'], 'system')
            self.assertIn('sources', json.loads(payload['messages'][1]['content']))
            return {'choices': [{'message': {'content': json.dumps(brief)}}]}
        return ModelClient('https://example.invalid/v1', 'test-placeholder', 'test-model', transport)

    def test_draft_and_explicit_acceptance(self):
        incident = Incident([Source('log', '14:05 errors 12%')])
        self.assertEqual(incident.draft(self.client())['blocked'], 0)
        self.assertFalse(incident.accepted)
        with self.assertRaises(ValueError):
            incident.accept(reviewer='Owner', reviewed_claims=[])
        result = incident.accept(reviewer='Owner', reviewed_claims=[0])
        self.assertEqual(result['status'], 'accepted')

    def test_fabrication_cannot_be_accepted(self):
        incident = Incident([Source('log', 'errors 12%')])
        incident.draft(self.client('errors 0%'))
        with self.assertRaises(ValueError):
            incident.accept(reviewer='Owner', reviewed_claims=[0])

    def test_regeneration_invalidates_acceptance(self):
        incident = Incident([Source('log', 'errors 12%')])
        incident.draft(self.client())
        incident.accept(reviewer='Owner', reviewed_claims=[0])
        incident.draft(self.client('invented'))
        self.assertFalse(incident.accepted)

    def test_non_json_rejected(self):
        client = ModelClient('https://example.invalid/v1', 'placeholder', 'test', lambda _: {'choices': [{'message': {'content': 'not json'}}]})
        with self.assertRaises(ValueError):
            client.generate([Source('log', 'errors 12%')])

    def test_http_rejected(self):
        with self.assertRaises(ValueError):
            ModelClient('http://example.invalid', 'placeholder', 'test')

if __name__ == '__main__':
    unittest.main()
