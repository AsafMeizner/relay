"""Deterministic evidence checks for AI-generated incident handoffs."""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Source:
    id: str
    text: str


def validate_brief(brief: dict, sources: list[Source]) -> dict:
    """Validate traceability, never infer that a citation proves a claim.

    Model output and source text are untrusted. Exact excerpts establish
    provenance only; a human still assesses whether they support the claim.
    """
    index = {}
    for source in sources:
        if not source.id or source.id in index:
            raise ValueError('Source IDs must be nonempty and unique')
        index[source.id] = source.text
    claims = brief.get('claims', [])
    if not isinstance(claims, list):
        raise ValueError('claims must be a list')
    results = []
    for claim in claims:
        errors = []
        if not isinstance(claim, dict):
            results.append({'claim': claim, 'status': 'blocked', 'errors': ['invalid_claim']})
            continue
        if not isinstance(claim.get('text'), str) or not claim['text'].strip():
            errors.append('missing_claim_text')
        citations = claim.get('citations', [])
        if not isinstance(citations, list) or not citations:
            errors.append('missing_citations')
            citations = []
        for citation in citations:
            if not isinstance(citation, dict):
                errors.append('invalid_citation')
                continue
            source_id = citation.get('source_id')
            quote = citation.get('quote')
            if not isinstance(source_id, str) or source_id not in index:
                errors.append('unknown_source')
            elif not isinstance(quote, str) or not quote.strip():
                errors.append('missing_quote')
            elif quote not in index[source_id]:
                errors.append('quote_not_in_source')
        results.append({'claim': claim, 'status': 'blocked' if errors else 'needs_review', 'errors': errors})
    return {'claims': results, 'blocked': sum(r['status'] == 'blocked' for r in results),
            'review_required': True, 'sources': [asdict(s) for s in sources]}
