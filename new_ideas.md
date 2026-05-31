# New ideas — the sister stack for the repo source

This document captures the **sister stack**: a parallel set of four new
skills that mirror the existing paper-discovery stack's shape but operate
on a **third source** of papers: the user's local repository tree. The
sister stack runs independently of the existing stack. They share no code.

## The Cardinal Rule constraint

**Don't touch what works.** The existing stack (training-data discovery,
web-search discovery, verify, validate, AI-enrich) is shipped, deployed,
and working. None of those skills get modified, generalized, or extended.
The sister stack consists of FOUR ENTIRELY NEW SKILLS that parallel the
existing stack's shape, each dedicated to the repo source.

The two stacks run independently. Their outputs may be merged at the very
end via a separate skill (a topic for a future conversation), but the
stacks themselves don't intersect.

---

## The sister stack — four new skills

### Stage 1 — DISCOVER: `/identify-papers-repo`

The discover stage for the repo source. Input: a repo root.

**How it works:** spawns a **parallel agent swarm** across the repository
tree. Each agent is assigned a sub-tree and walks it. At every folder, the
agent decides "does this look like a paper-bearing location?" using
heuristics:

- Presence of PDF files
- Filename patterns that suggest paper-author-year naming
- First-page text patterns (DOI present, abstract structure, etc.)

For every PDF the agent thinks is a paper, it records two things:

- The **address** (absolute path to the PDF)
- A **best-effort title** (extracted from first-page text or filename)

**Output:** a candidate list of (address, title) pairs.

**Properties of this output:**

- Hallucination-free — every entry corresponds to a real file on disk.
- BUT can contain misclassifications — slide decks, manuals, course PDFs,
  receipts that the agent thought looked paper-shaped but aren't actually
  research papers.

### Stage 2 — VERIFY: `/identify-and-verify-repo-papers`

Loops through the Stage 1 candidate list, runs OpenAlex on each title,
and drops the misclassifications. This is the sister stack's verify gate.

Importantly: **verify is NOT redundant here.** Earlier brainstorms
suggested it might be (because PDFs on disk can't be hallucinated). That
reasoning held only under the assumption of *manual* paper-bearing folder
specification. Once the discover stage uses an automated parallel agent
swarm with heuristic classification, misclassifications become a real
failure mode — and verify's job is to catch them. Same OpenAlex check as
the existing verify skill, different failure mode being defended against:

- Existing verify (on training-data + websearch): catches hallucinations.
- Sister verify (on repo): catches misclassifications.

**This stage also handles deduplication.**

Repository scans naturally produce duplicates — the same paper can live
at multiple file paths in a single repo (one copy in
`papers/foundational/`, another in `experiments/baseline/refs/`, a third
in `archive/2024/`). The verify stage collapses these into a single
verified entry using the same dedup keys as the existing stack:

- **Primary key:** DOI (regex-extracted: `10\.\d{4,9}/[^\s/]+`)
- **Fallback key:** normalized title (lowercased, non-word chars stripped)

**Resolution rule when duplicates collapse: address-union, NOT first-seen.**
The verified entry's metadata carries ALL the file paths from the
collapsed duplicates as a list. This preserves the repo-location map —
the Marie-Kondo unlock that lets the user later ask "do I have multiple
copies of this paper, and where do they live?"

When a third candidate later dedupes to an existing verified entry, its
address gets appended to the list.

**Output schema addition for the sister stack:** each verified entry's
metadata block gains a `**Source paths:**` list field. For papers that
appear only once in the repo (the common case), the list has length 1
and the format gracefully degrades. For duplicates, the list lengthens.

Example metadata block excerpt:

```
**Source paths:**
  - /papers/foundational/krenn-melvin.pdf
  - /old-backup/krenn-2016.pdf
  - /experiments/baseline/refs/2016-prl-zeilinger.pdf
```

This format extension is **specific to the sister stack** — the existing
stack's per-entry block format stays unchanged (Cardinal Rule honored).
The `Source paths` field carries through Stages 3 and 4, ending up in
the final bibliography written by `/identify-papers-repo-final`.

### Stage 3 — VALIDATE: `/identify-and-verify-and-validate-repo-papers`

The sister stack's human gate. **Default is approve-all** (no UI, the
verified list passes through unchanged) so the sister stack runs safely
in automated pipelines. Pass `--interactive` to open a GTK dialog with
the standard three-button approval pattern (Approve All / Approve None /
Approve Selections + Submit).

Validate is *practically* redundant for the repo source — most of the time
the user won't bother running it interactively — but the option is preserved
because a paper landing on disk via an autonomous skill doesn't always
mean the user explicitly approved it for their canonical corpus.

### Stage 4 — CAP-STONE: `/identify-papers-repo-final`

The sister stack's enrichment cap-stone. Loops through the validated repo
entries, hits OpenAlex per paper, and writes the rich metadata block per
entry (authors with affiliations, year, venue, type, citations, OA status,
topics, full abstract). Output file: `identified_papers_repo_final.md`.

The role mirrors the existing cap-stone, but on the repo branch only.
Could not be called `/identify-papers-ai` (Cardinal Rule + name doesn't
fit — AI isn't the source for repo).

---

## The two-stack picture

```
EXISTING STACK (untouched):
  training-data ─┐
                 ├─→ verify → validate → identify-papers-ai → identified_papers_ai_info.md
  websearch    ─┘

SISTER STACK (new, parallels the shape):
  repo  ─→  identify-papers-repo
                  → identify-and-verify-repo-papers
                      → identify-and-verify-and-validate-repo-papers
                          → identify-papers-repo-final
                              → identified_papers_repo_final.md
```

The two stacks produce two separate output files. They never share state.
A future skill may merge their outputs, but that's a separate concern.

---

## Why this shape (architectural notes)

1. **Sister-stack rather than reuse** — Cardinal Rule. The existing
   verify, validate, and AI-enrich skills don't get touched, generalized,
   or extended. The sister stack stands on its own.

2. **Parallel agent swarm at discover** — repositories can be huge.
   Sequential per-PDF processing is too slow. The discover stage spawns
   agents over sub-trees so the traversal happens in parallel.

3. **Verify earns its keep on the repo branch** — even though PDFs on
   disk can't be hallucinated, automated heuristic classification at
   discover time WILL produce false positives. Verify catches them via
   OpenAlex. Different failure mode than the existing stack's verify,
   same defensive role.

4. **Validate stays opt-in** — same pattern as the existing validate
   skill. Default is no-UI approve-all so the sister stack composes
   safely in automated pipelines; `--interactive` opens the GTK dialog
   for users who want to curate.

5. **`-final` suffix on the cap-stone** — captures the role (terminal
   output of the sister stack) without baking in source assumptions the
   way the existing `-ai` suffix did. If a future source is added (e.g.
   Zotero, arXiv feed), the naming pattern generalizes: `-<source>-final`.

---

## Status

Design captured. Nothing built.

**Suggested build order:**

1. `/identify-papers-repo` first — without the discover stage producing
   output, the rest of the sister stack has nothing to operate on.
   Validates the parallel-agent-swarm pattern + the heuristic
   classification before downstream stages are built.

2. `/identify-and-verify-repo-papers` — once stage 1 produces candidate
   files, the verify gate is the next thing to validate (does OpenAlex
   correctly reject the misclassifications?).

3. `/identify-and-verify-and-validate-repo-papers` — defer until stages
   1 and 2 are working. The GTK dialog is well-understood (sister to
   the existing validate skill's dialog), so this is mostly a thin
   wrapper.

4. `/identify-papers-repo-final` — the cap-stone. Easy once the
   metadata-enrichment pattern is fluent (same shape as the existing
   AI-enrich skill, different source).

## Out of scope for this document

- **Merging sister-stack output with the existing stack's output.**
  This is a separate skill, separate conversation.
- **Folder-only and tree-only variants from the earlier brainstorm.**
  Subsumed into `/identify-papers-repo`'s parallel-agent traversal —
  the discover stage walks the whole repo tree by default. If targeted
  scans of a single folder or single tree root become useful later,
  they'd be additional sister-stack-style skills, not modifications
  to the four above.
