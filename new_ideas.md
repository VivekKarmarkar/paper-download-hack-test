# New ideas for the paper-discovery pipeline

Captured during a brainstorm session. Both ideas extend the existing
`discover → verify → validate → AI-enrich → download` pipeline by adding
two new *sources* of identified papers (folders and repo trees) plus a
combinator that merges multiple bibliography files into one canonical view.

The driving insight: every existing `identify-papers-*` skill produces the
same per-entry line format. **The line format IS the contract.** Any new
input source that produces lines in that format gets free composition with
every downstream tool (`identify-and-verify-papers`, `merge-paper-lists`,
`paper-download-hack`, etc.). No schema changes, no parser glue.

---

## Idea 1 — `/identify-papers-folder <path>`

A **fourth source** of identified papers, alongside the existing three:

| Skill | Origin of papers |
|---|---|
| `identify-papers-training-data` | Model memory recall |
| `identify-papers-websearch` | Live web swarm |
| `identify-papers-ai` | Validated list + OpenAlex metadata |
| **`identify-papers-folder`** | **PDFs already on disk in a flat folder** |

This is the **first source whose origin is "what already exists" rather than
"what I want to find."** Every other discover-* skill is forward-looking
(memory or search). This one is a librarian for stuff you forgot you had.

### Behavior

1. Take a folder path. Default: `papers/` (so it composes ergonomically with
   `literature-download-hack` output).
2. For each `*.pdf` in the folder, run `/paper-metadata`'s `resolve()` —
   which already handles `PDF path → DOI from first page → OpenAlex` natively.
3. Write the same per-entry block format used everywhere else to
   `<folder>_bibliography.md` (e.g. `papers_bibliography.md`).

### Three real design questions

These have actual trade-offs:

1. **What happens when a PDF can't be resolved?** Books, internal reports,
   very old papers, scanned-without-OCR PDFs → OpenAlex returns nothing.
   Options:
   - (a) Record as `status: unresolved` with filename + best-effort title,
     mirroring `verify-citation`'s `HALLUCINATED` block pattern.
   - (b) Skip silently with a summary count.
   - (c) Emit a separate `unresolved.md` file for human triage.

   **Lean (a)** — visible in the artifact, not silently lost. Preserves the
   "honest about failure" property the pipeline has elsewhere.

2. **Default folder vs explicit path?** Defaulting to `papers/` makes the
   common case (catalog the output of `literature-download-hack`) ergonomic
   but obscures that the skill works on any folder. Explicit-path is more
   honest about scope.

3. **Output filename convention.** `<folder>_bibliography.md` works for
   `papers/` → `papers_bibliography.md`. But what about `~/Downloads/`?
   `Downloads_bibliography.md`? Or always `bibliography.md` in CWD?

---

## Idea 2 — `/identify-papers-tree <root>`

Recursive variant. **NOT a flag on `identify-papers-folder`** — separate
skill, because the recursive case introduces problems the flat case never has.

### Why this is its own skill, not a `--recursive` flag

A flag would force one skill to carry two very different scopes of concern:
scanning *a known folder* vs *foraging a repo*. Each genuinely separate
problem the recursive case introduces:

| Concern | Flat folder | Tree |
|---|---|---|
| Which subfolders to descend into | n/a | Skip `.git/`, `node_modules/`, `.venv/`, `__pycache__/`, etc. |
| Symlink handling | n/a | Off by default; opt-in `--follow-symlinks` |
| PDF-is-a-paper filter | Assume yes | **Required** — repos have manuals, slide decks, course PDFs, receipts |
| Provenance | Filename only | **Path matters** — `papers/foundational/X.pdf` carries semantic meaning |
| Performance | 20–100 PDFs | 5000+ possible; needs `(mtime, sha1) → DOI` cache |
| Output format extension | Same as family | Same — **plus** `**Source path:**` field in metadata block |

### The unlock the recursive version gives you

A **map of your repo's papers**. The bibliography file becomes a *physical
layout*: "the Krenn-Melvin paper exists at three places — `papers/`,
`experiments/baseline-old/refs/`, and `archive/2024-Q3/`. Pick which to keep."

That's only possible when path is a first-class field, and only meaningful
when traversal is non-flat. The flat version never sees this.

Also: with the recursive version you can finally answer "do I have multiple
copies of the same paper scattered across this repo?" — a real
Marie-Kondo-for-academic-PDFs moment that's been silently impossible until
now.

### Heuristics for "is this PDF a paper?"

Necessary because recursive scans pick up false positives:
- First-page text contains a DOI pattern → YES
- OpenAlex title-search returns hit above some overlap threshold → YES
- Filename contains an author+year pattern → MAYBE (best-effort)
- None of the above → flag for human review, don't pollute the bibliography

---

## Idea 3 — `/merge-paper-lists <out.md> <in1.md> <in2.md> ...`

The combinator. Concatenates multiple bibliography-format `.md` files into
one canonical view, deduping by DOI (primary) or normalized title
(fallback) — the exact same key used elsewhere in the pipeline.

### One real design question

When the same DOI appears in two source files, **which entry wins**?

- (a) **First file listed wins** — predictable, user-controllable via argument order
- (b) **Longest line wins** — more metadata
- (c) **Prefer files with a specific suffix** (e.g. `_ai_info.md` over
  `_bibliography.md`, because the AI-info file has the curated original line
  vs the auto-synthesized one)

Each has different semantics for "what should the canonical entry look like."

---

## What this composition unlocks

Concretely, three workflows that don't exist today:

1. **"What's in my advisor's old paper folder?"** — point
   `/identify-papers-folder` at it, get a bibliography of what's there.

2. **"Are any papers in my library missing from my literature pipeline?"** —
   diff the bibliography file against `identified_papers_ai_info.md`. Papers
   in the library but not the pipeline are *unindexed* knowledge; papers in
   the pipeline but not the library are *undownloaded* targets.

3. **"Give me one bibliography that includes both my old library AND new
   discoveries."** —
   ```
   /identify-papers-tree ~/research
   /literature-download-hack "<topic>"
   /merge-paper-lists all_papers.md research_tree_bibliography.md identified_papers_ai_info.md
   ```

The pipeline graduates from "tool for discovering new papers about a topic"
to "tool for managing a literature corpus that spans both my history and my
future."

---

## Status

Brainstorm only. Nothing built. Filed here so the design discussion isn't
lost across sessions. When ready to build, start with `/identify-papers-folder`
(simpler, lower blast radius, validates the format-contract assumption),
then `/merge-paper-lists` (immediately useful), then `/identify-papers-tree`
(highest payoff but most failure modes).
