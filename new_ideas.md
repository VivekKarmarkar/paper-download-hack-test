# New ideas for the paper-discovery pipeline

Captured during a brainstorm session, then refined in a follow-up voice
conversation that sharpened the architecture significantly. The original
sketch framed three new skills as additions to the existing pipeline.
The refinement realized they actually form a **shortcut branch** that
bypasses the verify + validate stages entirely.

## The load-bearing insight

The existing pipeline is:

```
discover (memory / web) → verify (OpenAlex) → validate (human gate) → AI-enrich → download
```

The verify and validate stages exist for *specific failure modes of
generative sources*:

- **Verify** catches hallucinations — the candidate from memory or web
  might be a made-up paper.
- **Validate** is the human gate — "do I actually want this paper in
  my corpus?"

For a **PDF that already exists on disk in your folder**, these two
gates collapse for **different reasons** — and the distinction matters:

- **Verify is *strictly* redundant.** A PDF on disk literally cannot
  be a hallucination. It's right there. You can `cat` it. The
  epistemic guarantee is absolute.

- **Validate is only *practically* redundant — NOT strictly.** Files
  on disk *might* have landed there because the user explicitly placed
  them — in which case the "I want this" vote was already cast. But
  they might also have landed there via an autonomous skill running
  with relaxed permissions (e.g. `paper-download-hack` invoked from a
  scheduled job, or a `literature-download-hack` run the user has
  since forgotten about). In that case the file's presence is NOT
  evidence that the user explicitly approved it for their canonical
  corpus. The validate gate's role — "yes, I actually want this paper
  in my library" — is conceptually still meaningful, even if in
  practice the user often won't bother running it.

So the new branch collapses to one step **by default** for convenience:
discover-and-enrich. Walk the disk, hit OpenAlex per PDF, write the
same rich metadata block format `identify-papers-ai` produces. But an
**optional validate step** should remain available — same pattern as
the existing `identify-and-verify-and-validate-papers` skill, which
defaults to approve-all and opens a GTK dialog only when `--interactive`
is passed. The user can choose to curate; they're just not forced to.

The two pipelines side-by-side:

```
GENERATIVE (existing):  discover → verify → validate → AI-enrich → download
                                    └─ strictly required (hallucination defense)
                                              └─ practically required (corpus gate)

ON-DISK    (new):       discover-and-enrich → [optional validate] → (merge)
                        └─ verify collapsed (strict)
                                              └─ validate is opt-in, not absent
```

The generalizable principle, properly stated:

- **A stage is *strictly* redundant** when the input guarantees the
  failure mode the stage was defending against cannot occur. Verify is
  strictly redundant for on-disk sources because hallucination is
  impossible for files that exist.

- **A stage is *practically* redundant** when the user usually doesn't
  bother running it, but the failure mode it defends against is still
  conceptually possible. Validate is practically redundant for on-disk
  sources because autonomous skills can deposit files without the
  user's explicit consent — the human-gate role is still real, even
  if usually skipped.

Strictly redundant stages can be removed. Practically redundant stages
should be made opt-in, not removed. **Match the pipeline's defaults to
typical use, but don't surgically remove gates whose underlying failure
mode can still occur.**

---

## Skill 1 — `/identify-papers-folder <path>`

A **fourth source** of identified papers, the first whose origin is
"what already exists on disk" rather than "what I want to find."

| Skill | Origin of papers | Pipeline path |
|---|---|---|
| `identify-papers-training-data` | Model memory recall | Full (verify + validate + enrich) |
| `identify-papers-websearch` | Live web swarm | Full (verify + validate + enrich) |
| `identify-papers-ai` | Validated list + metadata | Cap-stone of the full path |
| **`identify-papers-folder`** | **PDFs on disk (flat folder)** | **Shortcut (enrich; optional validate)** |
| **`identify-papers-tree`** | **PDFs on disk (tree)** | **Shortcut (enrich; optional validate)** |

### Behavior

1. Take a folder path (no default — explicit is honest about scope).
2. For each `*.pdf` in the folder, run `/paper-metadata`'s `resolve()` —
   which already handles `PDF path → DOI from first page → OpenAlex`
   natively.
3. Write one rich metadata block per resolved PDF to
   `<folder>_bibliography.md`, in the same per-entry format as
   `identified_papers_ai_info.md`.
4. PDFs that can't be resolved go to a **separate** `<folder>_unresolved.md`
   file — NOT as placeholders in the main bibliography. Keep the main
   file clean; let the dead-letter queue catch the failures.

### Resolved design decisions (from voice follow-up)

- **Unresolved PDFs** → separate `unresolved.md` file. No placeholders
  in the main bibliography. Rationale: load-bearing papers will get
  flagged during later refinement; a clean main file beats a noisy one
  cluttered with "title: unknown" rows.
- **Default folder** → no default, require explicit path. Honest about
  scope; the skill genuinely works on any folder, not just `papers/`.
- **Output filename** → `<basename>_bibliography.md` + `<basename>_unresolved.md`,
  both written to the current working directory.

---

## Skill 2 — `/identify-papers-tree <root>`

Recursive variant. **NOT a flag on `identify-papers-folder`** — separate
skill, because the recursive case introduces problems the flat case
never has.

### Why it's its own skill, not `--recursive`

A flag would force one skill to carry two very different scopes of
concern: scanning *a known folder* vs *foraging a repo*.

| Concern | Flat folder | Tree |
|---|---|---|
| Which subfolders to descend into | n/a | Skip `.git/`, `node_modules/`, `.venv/`, `__pycache__/`, etc. |
| Symlink handling | n/a | **Off by default** (avoids infinite loops on cyclic symlinks) |
| PDF-is-a-paper filter | Assume yes | **Required** — repos have manuals, slide decks, course PDFs, receipts |
| Provenance | Filename only | **Path matters** — `papers/foundational/X.pdf` carries semantic meaning |
| Performance | 20–100 PDFs | 5000+ possible; needs `(mtime, sha1) → DOI` cache |
| Output format extension | Same as family | Same — **plus** a `**Source path:**` field in metadata block |

### Resolved design decisions (from voice follow-up)

- **Depth** → full traversal, root to every leaf. No limit.
- **Symlinks** → off by default to prevent infinite recursion on cyclic
  symlinks (common in messy repos with build artifacts). Symlinked
  branches just don't get descended into. Opt-in `--follow-symlinks`
  flag for the rare case where you want them.
- **Unresolved PDFs** → same as flat folder, separate `unresolved.md`
  file (with source paths preserved so you can find them again).

### The unlock the tree version gives you

A **map of your repo's papers**. The bibliography file becomes a
*physical layout*: "the Krenn-Melvin paper exists at three places —
`papers/`, `experiments/baseline-old/refs/`, and `archive/2024-Q3/`.
Pick which to keep."

That's only possible when path is a first-class field, and only
meaningful when traversal is non-flat. The flat version never sees this.

Also: with the recursive version you can finally answer "do I have
multiple copies of the same paper scattered across this repo?" — a real
Marie-Kondo-for-academic-PDFs moment that's been silently impossible
until now.

### Heuristics for "is this PDF a paper?"

Necessary because recursive scans pick up false positives:

- First-page text contains a DOI pattern → YES
- OpenAlex title-search returns hit above some overlap threshold → YES
- Filename contains an author+year pattern → MAYBE (best-effort)
- None of the above → goes to `unresolved.md`, doesn't pollute the
  main bibliography

---

## Skill 3 — `/merge-paper-lists <out.md> <in1.md> <in2.md> ...`

The combinator. Concatenates any number of bibliography-format `.md`
files into one canonical view, deduping by DOI (primary) or normalized
title (fallback) — the exact same key used elsewhere in the pipeline.

### Resolved design decision (from voice follow-up)

- **Dedup winner** → first-seen wins. Source provenance doesn't matter,
  frequency doesn't matter, "which version of the entry has more
  metadata" doesn't matter. A duplicate is a duplicate — pick one,
  any one, deterministically. First-seen is the simplest deterministic
  rule and gives the user control via argument order if they care.

---

## What this composition unlocks

Three workflows that don't exist today:

1. **"What's in my advisor's old paper folder?"** — point
   `/identify-papers-folder` at it, get a bibliography of what's there.

2. **"Are any papers in my library missing from my literature pipeline?"** —
   diff the bibliography file against `identified_papers_ai_info.md`.
   Papers in the library but not the pipeline are *unindexed* knowledge;
   papers in the pipeline but not the library are *undownloaded* targets.

3. **"Give me one bibliography that includes both my old library AND
   new discoveries."**

   ```
   /identify-papers-tree ~/research
   /literature-download-hack "<topic>"
   /merge-paper-lists all_papers.md research_tree_bibliography.md identified_papers_ai_info.md
   ```

The pipeline graduates from "tool for discovering new papers about a
topic" to "tool for managing a literature corpus that spans both my
history and my future."

---

## Status

Brainstorm + refinement complete. Architecture is fully spec'd, all
resolved design questions documented. Nothing built yet.

**One open implementation question** (added in the strict-vs-practical
refinement): how should the *optional validate step* be plugged into the
on-disk branch? Two viable options:

- **(a)** Folder/tree skills grow their own `--interactive` flag that
  opens the GTK dialog on the produced bibliography before writing.
- **(b)** The existing `identify-and-verify-and-validate-papers` skill
  is generalized to operate on any bibliography file, not just the
  verified one — making it a standalone validate-pass step that can be
  composed with anything.

Lean (b) for Unix-philosophy reasons (one skill, one job, composable),
but defer the call to build time.

**Suggested build order:**

1. **`/identify-papers-folder`** — simplest, lowest blast radius.
   Validates the shortcut-branch assumption (that the OpenAlex
   resolution + same-format output actually work end-to-end on real
   PDFs). Also validates that `/paper-metadata`'s `resolve()` does
   what we think it does when called in bulk.

2. **`/merge-paper-lists`** — immediately useful as soon as folder works,
   because you'll want to combine the new folder-bibliography with the
   existing `identified_papers_ai_info.md`.

3. **`/identify-papers-tree`** — highest payoff but most failure modes
   (skip-list calibration, symlink handling, paper-vs-not-paper
   heuristics, caching). Build after the simpler two have shaken out
   the OpenAlex-bulk-resolve patterns.
