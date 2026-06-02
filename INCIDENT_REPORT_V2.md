# Incident report — Stack 3-PDF page-1 identifier-extraction failure

## Summary

A PDF in a user-curated folder was misidentified as a different paper.
The wrong paper's metadata propagated through the entire downstream
pipeline (verify → validate → cap-stone bibliography → merged
bibliography → references PDF) and was only caught when a human read
the final deliverable.

## Failure mode

1. The page-1 PDF identifier extractor reads the first page's text
   layer and pattern-matches for DOI / arXiv-ID / title tokens.
2. On a paper whose first page prominently cites prior work, the
   extractor matched a **DOI belonging to a cited reference**, not the
   paper's own DOI.
3. The verify stage looked up that cited-reference DOI on OpenAlex,
   got back a real, well-formed record, and cross-checked author
   surnames between the page-1 text and the resolved record.
4. The cross-check correctly detected weak surname overlap and emitted
   a `SUSPICIOUS` verdict.
5. The validate stage, running in default (non-interactive)
   pass-through mode, carried the `SUSPICIOUS` flag forward without
   blocking the entry.
6. The cap-stone enrichment skill hydrated the wrong-paper record into
   the bibliography with the user-curated source PDF's path attached
   to it — a confidently-presented wrong answer with a real on-disk
   provenance trail.
7. The merge skill deduped on DOI and propagated the bad entry into
   the consolidated bibliography.
8. The LaTeX references-section skill rendered the bad entry as
   reference N of N, with a clickable DOI pointing to a real but
   unrelated paper.

## Where each stage was honest vs. silent

| Stage | Behavior |
|---|---|
| Page-1 extractor | Silent — no signal that the matched DOI might be a citation |
| Verify (OpenAlex cross-check) | **Honest** — emitted `SUSPICIOUS` |
| Validate (default mode) | Silent pass-through by design |
| Cap-stone enrich | Silent — flag was carried but not surfaced |
| Merge | Silent — dedup operates on DOI, not on flag status |
| References PDF | Silent — no visual indicator of flagged entries |

The `SUSPICIOUS` signal was generated at the right place, but every
stage downstream of verify treated it as informational metadata rather
than as a gate. By the time the entry reached the deliverable, the
flag was invisible.

## Root cause

The page-1 text layer is not a reliable identifier source for any PDF
that cites prior work on its first page. The extractor's contract
(first DOI / arXiv ID it finds is the paper's own identifier)
silently breaks on the common case of a paper whose introduction
opens with a citation.

The downstream pipeline compensates for this with the verify-stage
cross-check, but the compensation is advisory, not enforcing.

## Failure surface

This failure mode applies to **every paper** that:

- Has its first-page text layer dominated by a citation rather than
  its own metadata block, **AND**
- Is processed by the page-1 identifier extractor, **AND**
- Reaches a deliverable through the default (non-interactive) validate
  path.

The intersection is not small. Conference papers, workshop papers,
and arXiv preprints frequently open with "Recent work [N] has shown
that..." — exactly the pattern that defeats the extractor.

## What would have caught it earlier

1. **Filename-vs-resolved-title token overlap check.** The source
   PDF's filename usually contains tokens from the real paper's
   title. Comparing the filename against the resolved OpenAlex
   record's title would have flagged this case loudly — the filename
   token set and the resolved title token set had near-zero overlap.
2. **arXiv-as-DOI fallback before page-1 DOI trust.** When a paper's
   filename or page-1 text contains an arXiv-style ID, prefer
   resolving that ID before trusting any other DOI on page 1.
3. **Hard gate on `SUSPICIOUS` in the cap-stone.** The cap-stone
   could refuse to enrich a flagged entry without explicit user
   confirmation. The current pass-through behavior is convenient but
   trades correctness for throughput.
4. **Visible flag in the deliverable.** Even rendering the
   `SUSPICIOUS` tag next to the citation in the references PDF would
   make a human catch it on read-through. The flag exists; surfacing
   it costs nothing.

## What worked

- The verify stage's surname cross-check correctly identified the
  mismatch.
- The flag was persisted all the way through to the cap-stone
  bibliography.
- Once the error was pointed out, finding and substituting the
  correct paper took one OpenAlex query and one in-place edit of
  the LaTeX source.

## What did not work

- No stage between verify and the final PDF treated the flag as
  actionable.
- The user had to be the final QA gate — which defeats the purpose
  of an automated bibliography pipeline.

## Honest assessment

The pipeline is fundamentally correct in its architecture (extract →
verify → validate → enrich → render). The bug is that the
default-mode `SUSPICIOUS` semantics are too permissive: a verdict
generated specifically to flag low-confidence matches is being
treated as a non-blocking annotation by every consumer downstream
of the verify stage. The fix is not in the extractor; it is in the
downstream contract.

Until that contract is tightened, every Stack 3-PDF deliverable
should be assumed to contain at least one misidentified entry per
N papers processed, where N depends on how often first-page
citations dominate the text layer in the corpus. For a small
curated folder (single-digit PDFs), the failure probability per
deliverable is non-trivial.
