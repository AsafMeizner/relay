import unittest
from relay.evidence import Source, validate_brief

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.sources = [Source('log-1', '14:02 deploy started. 14:05 error rate 12%.')]

    def check(self, citation):
        return validate_brief({'claims': [{'text': 'Errors increased', 'citations': [citation]}]}, self.sources)

    def test_exact_quote_requires_human_review(self):
        result = self.check({'source_id': 'log-1', 'quote': 'error rate 12%'})
        self.assertEqual(result['blocked'], 0)
        self.assertEqual(result['claims'][0]['status'], 'needs_review')
        self.assertTrue(result['review_required'])

    def test_fabricated_quote_blocked(self):
        self.assertEqual(self.check({'source_id': 'log-1', 'quote': 'error rate 0%'})['blocked'], 1)

    def test_unknown_source_blocked(self):
        self.assertEqual(self.check({'source_id': 'invented', 'quote': 'error rate 12%'})['blocked'], 1)

    def test_missing_citations_blocked(self):
        self.assertEqual(validate_brief({'claims': [{'text': 'Recovered'}]}, self.sources)['blocked'], 1)

    def test_duplicate_sources_rejected(self):
        with self.assertRaises(ValueError):
            validate_brief({}, self.sources * 2)

    def test_malformed_citation_blocked(self):
        self.assertEqual(self.check(None)['blocked'], 1)

    def test_empty_quote_blocked(self):
        self.assertEqual(self.check({'source_id': 'log-1', 'quote': ''})['blocked'], 1)

    def test_quote_does_not_prove_claim(self):
        result = validate_brief({'claims': [{'text': 'Everything is fixed', 'citations': [{'source_id': 'log-1', 'quote': 'deploy started'}]}]}, self.sources)
        self.assertEqual(result['claims'][0]['status'], 'needs_review')

if __name__ == '__main__':
    unittest.main()
