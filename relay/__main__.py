"""Run a local evidence-check example or an OpenAI-compatible model draft."""
import argparse
import json
import os
from relay.evidence import Source
from relay.workflow import Incident, ModelClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Call the configured model API')
    args = parser.parse_args()
    sources = [Source('deployment', '14:02 deployment v42 started.'),
               Source('monitor', '14:05 checkout error rate 12%. At 14:09 error rate 3%.'),
               Source('oncall', '14:06 rollback requested. Completion is not confirmed.')]
    incident = Incident(sources)
    if args.live:
        provider = os.environ.get('LLM_PROVIDER', 'nebius')
        key_name = 'NEBIUS_API_KEY' if provider == 'nebius' else 'OPENAI_API_KEY'
        key = os.environ.get(key_name)
        model = os.environ.get('RELAY_MODEL')
        base = os.environ.get('RELAY_BASE_URL', 'https://api.tokenfactory.nebius.com/v1')
        if not key or not model:
            parser.error(f'Live mode requires {key_name} and RELAY_MODEL; no request made')
        client = ModelClient(base, key, model)
    else:
        brief = {'claims': [
            {'text': 'Checkout errors were observed after deployment started; causation is unconfirmed.',
             'citations': [{'source_id': 'deployment', 'quote': '14:02 deployment v42 started.'},
                           {'source_id': 'monitor', 'quote': '14:05 checkout error rate 12%.'}]},
            {'text': 'Rollback completion is unconfirmed.',
             'citations': [{'source_id': 'oncall', 'quote': 'Completion is not confirmed.'}]}],
            'open_questions': ['Did rollback complete?', 'What caused the checkout errors?'],
            'suggested_actions': ['Ask the incident commander to verify rollback status.']}
        client = ModelClient('https://example.invalid/v1', '', 'fixture',
                             lambda _: {'choices': [{'message': {'content': json.dumps(brief)}}]})
    validation = incident.draft(client)
    print(json.dumps({'mode': 'live' if args.live else 'offline fixture (no AI call)',
                      'accepted': incident.accepted, 'brief': incident.brief,
                      'validation': validation}, indent=2))


if __name__ == '__main__':
    main()
