"""Model reply compatibility must preserve strict JSON rejection."""
import json
import unittest
from relay.evidence import Source
from relay.workflow import ModelClient, parse_json_object


class ModelReplyTests(unittest.TestCase):
    def test_supported_wrappers(self):
        brief = {'claims': [{'text': 'Errors observed', 'citations': [{'source_id': 'log', 'quote': 'errors 12%'}]}], 'open_questions': ['Cause?'], 'suggested_actions': ['Investigate']}
        raw = json.dumps(brief)
        for content in [raw, '  ' + raw + '\n', '```json\n' + raw + '\n```', '<think>Reasoning omitted</think>\n' + raw, '<think>Reasoning omitted</think>\n```json\n' + raw + '\n```']:
            with self.subTest(content=content):
                client = ModelClient('https://example.invalid/v1', 'placeholder', 'test', lambda _: {'choices': [{'message': {'content': content}}]})
                self.assertEqual(client.generate([Source('log', 'errors 12%')]), brief)

    def test_extraneous_or_malformed_content_rejected(self):
        for content in [None, {}, '', 'Here is the result: {}', '{} trailing', '{} {}', '<think>unfinished {}', '```json\n{}', '```json {} ```', '```json\n{}\n``` trailing']:
            with self.subTest(content=content):
                with self.assertRaises(ValueError):
                    parse_json_object(content)

    def test_wrappers_do_not_bypass_schema(self):
        for raw in ['[]', '{}', '{"claims": []}', '{"claims": [{}], "open_questions": "bad", "suggested_actions": []}']:
            client = ModelClient('https://example.invalid/v1', 'placeholder', 'test', lambda _: {'choices': [{'message': {'content': '```json\n' + raw + '\n```'}}]})
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    client.generate([Source('log', 'errors 12%')])
