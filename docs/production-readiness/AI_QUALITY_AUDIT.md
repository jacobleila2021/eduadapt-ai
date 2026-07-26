# AI Quality Audit

AI quality readiness score: 38/100.

## Strengths

- Prompts state that deterministic engine results and official answers are authoritative.
- Subject-scope rules discourage cross-subject content.
- Retrieval and official question injection now have deterministic relevance gates.
- Failed verified-content QA is quarantined from user delivery paths.
- OpenAI calls have bounded timeout/retry behavior.
- Model-authored complex SVG is not trusted for lesson rendering.

## Blocking findings

- The production teaching branch runs before the complete verified engine chain.
- There is no verified multi-subject corpus for the requested six-subject production claim.
- Tutor grounding, Socratic quality, misconception correction, hint progression, and refusal behavior lack an end-to-end live evidence set.
- Generated assessment answers cannot be considered official outside verified banks.
- Live canaries were not run because fixture prerequisites failed; model output would not establish curriculum correctness.

## Required canary protocol

After curriculum and orchestration gates pass, run one budgeted canary per subject. Record model, prompt hash, source IDs, engine payload hashes, tokens, cost, latency, refusals, citations, answer-key equivalence, adaptation invariance, and human curriculum verdict.

Any changed deterministic result, unsupported citation, grade/subject leak, or official-answer invention is a hard publication failure.
