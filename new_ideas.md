# New ideas — two parallel new stacks

This document captures **two new stacks** that extend the paper-discovery
system. Each runs independently of the existing AI-driven stack and of
each other. Each consists entirely of NEW skills — the Cardinal Rule
applies: **don't touch what works.**

## The three-stack picture

```
STACK 1 (existing, untouched) — generative AI sources
  training-data ─┐
                 ├─→ verify → validate → identify-papers-ai → identified_papers_ai_info.md
  websearch    ─┘

STACK 2 (NEW: sister stack for messy repos) — automated swarm scan
  repo ─→ identify-papers-repo
            → identify-and-verify-repo-papers
              → identify-and-verify-and-validate-repo-papers
                → identify-papers-repo-final → identified_papers_repo_final.md

STACK 3 (NEW: user-curated stack) — manual library scan
  user folder/tree ─→ identify-papers-user-folder
                       → identify-papers-user-tree
                         → identify-papers-user → identified_papers_user.md
```

The three stacks have different **trust postures** toward their sources,
which determines how much pipeline machinery each needs:

| Stack | Source | Hallucination risk | Misclassification risk | Verify? | Validate? |
|---|---|---|---|---|---|
| 1 (existing) | Generative AI | Yes | n/a | Required | Optional |
| 2 (sister) | Auto repo scan | No (file exists) | Yes (heuristic agent) | Required | Optional |
| 3 (user) | Hand-curated folder | No | No (human curated) | Strictly redundant | Strictly redundant |

Stack 3 is the simplest — full trust in the source means the discover →
enrich pipeline collapses to two stages. Stack 2 has medium trust
(misclassifications need filtering). Stack 1 has lowest trust (hallucinations
need full defenses).

## The Cardinal Rule constraint

The existing Stack 1 skills (verify, validate, AI-enrich) are shipped,
deployed, working. They get touched by nothing in Stacks 2 or 3. Both
new stacks consist entirely of NEW skills that **parallel** the existing
stack's shape but **never reuse** its components.

The two new stacks also don't reuse each other — Stack 2 and Stack 3
each get their own independent set of skills, named to mark the source
they serve (`-repo-` or `-user-`).

---

## STACK 2 — The sister stack for messy repos

Use case: **"Inventory all papers buried in my messy project repo, where
I don't know which sub-folders have papers."**

Four new skills, mirroring the existing stack's four stages:

### Stage 1 — DISCOVER: `/identify-papers-repo`

Spawns a **parallel agent swarm** across the repository tree. Each
agent is assigned a sub-tree and walks it. At every folder the agent
decides "does this look like a paper-bearing location?" using heuristics:

- Presence of PDF files
- Filename patterns that suggest paper-author-year naming
- First-page text patterns (DOI present, abstract structure, etc.)

For every PDF the agent thinks is a paper, it records the **address**
(absolute path) and a **best-effort title** (from first-page text or
filename).

**Output:** a candidate list of `(address, title)` pairs.

**Properties:** hallucination-free (files exist), but can contain
**misclassifications** (slide decks, manuals, receipts that the agent
mistook for papers).

### Stage 2 — VERIFY: `/identify-and-verify-repo-papers`

Loops through the Stage 1 candidates, runs OpenAlex on each title,
drops misclassifications.

**Verify is NOT redundant here.** Earlier brainstorms suggested it might
be (PDFs on disk can't be hallucinated). That reasoning held only under
the assumption of *manual* paper-bearing folder specification. Once the
discover stage uses an automated parallel agent swarm with heuristic
classification, misclassifications become a real failure mode — and
verify's job is to catch them. Same OpenAlex check as the existing
verify skill, different failure mode defended against:

- Existing verify (training-data + websearch): catches hallucinations.
- Sister verify (repo): catches misclassifications.

**This stage also handles deduplication.**

Repository scans naturally produce duplicates — the same paper can live
at multiple file paths in a single repo. Verify collapses these using:

- **Primary key:** DOI (regex `10\.\d{4,9}/[^\s/]+`)
- **Fallback key:** normalized title (lowercased, non-word chars stripped)

**Resolution rule: address-union, NOT first-seen.** When duplicates
collapse, the verified entry's metadata carries ALL the file paths from
the collapsed duplicates as a list. Preserves the repo-location map —
the Marie-Kondo unlock that lets the user later ask "do I have multiple
copies of this paper, and where do they live?"

**Output schema addition:** each verified entry's metadata block gains
a `**Source paths:**` list field. Length 1 in the common case (no
duplicates); the format gracefully degrades. Example:

```
**Source paths:**
  - /papers/foundational/krenn-melvin.pdf
  - /old-backup/krenn-2016.pdf
  - /experiments/baseline/refs/2016-prl-zeilinger.pdf
```

This format extension is **sister-stack-only** — the existing stack's
per-entry block format stays untouched. The field carries through Stages
3 and 4 into the final bibliography.

### Stage 3 — VALIDATE: `/identify-and-verify-and-validate-repo-papers`

Optional human gate. **Default approve-all** (no UI, the verified list
passes through unchanged) so the sister stack runs safely in automated
pipelines. Pass `--interactive` to open a GTK dialog with the standard
three-button approval pattern (Approve All / Approve None / Approve
Selections + Submit).

### Stage 4 — CAP-STONE: `/identify-papers-repo-final`

The sister stack's enrichment cap-stone. Loops through the validated
repo entries, hits OpenAlex per paper, writes the rich metadata block
per entry (authors with affiliations, year, venue, type, citations, OA
status, topics, full abstract). Output file:
`identified_papers_repo_final.md`.

The `Source paths` field from Stage 2 carries through and ends up in
the final bibliography, preserving the repo-location map.

---

## STACK 3 — The user-curated stack for clean libraries

Use case: **"Inventory my carefully-organized reference folder where I
personally put every paper and there's no noise."**

Three new skills (NOT four — verify and validate are strictly redundant
when the user has hand-curated the source).

### Why no verify, no validate

Stack 3's source is assumed to be **clean by construction**. The user has
manually organized a folder (or a tree of folders) such that every PDF
in scope IS a research paper they want in their library. Under that
assumption:

- **Verify is strictly redundant.** There's no misclassification risk
  because no automated heuristic ever decided "this PDF looks paper-ish"
  — the human did the deciding. And papers obviously can't be
  hallucinated when they exist on disk.
- **Validate is strictly redundant.** The "do I want this paper in my
  corpus?" gate was already passed when the user manually placed the
  PDF in their curated folder. The act of organizing IS the validation.

This is the key distinction from Stack 2 — Stack 2's discover stage uses
an automated agent swarm that DOES misclassify, so verify earns its keep.
Stack 3 trusts the source completely because a human curated it.

### Stage 1 — DISCOVER (flat): `/identify-papers-user-folder`

Foundational skill. Input: one curated folder path. Walks the flat folder,
records every PDF as a `(address, title)` candidate. No heuristic
filtering — every PDF IS a paper by assumption.

**Output:** candidate list, same `(address, title)` shape as Stack 2's
discover output.

### Stage 2 — DISCOVER (recursive): `/identify-papers-user-tree`

Recursive variant. Input: one tree root containing curated paper folders.
**Builds on `/identify-papers-user-folder`** — walks the tree, calls
the folder skill at each level that contains PDFs, concatenates results.

Symlinks off by default to avoid loops; opt-in via `--follow-symlinks`.

**Output:** candidate list, same shape, with addresses now spanning
multiple folders within the tree.

### Stage 3 — CAP-STONE: `/identify-papers-user`

The user-curated stack's enrichment cap-stone. Name mirrors
`/identify-papers-ai` (the Stack 1 cap-stone) — captures the parallel
relationship between the two non-sister cap-stones (AI-source vs
User-source, each producing the canonical enriched bibliography for its
stack).

**What it does:**

1. Loops through the candidate list from `/identify-papers-user-folder`
   or `/identify-papers-user-tree`.
2. Hits OpenAlex per candidate via `/paper-metadata`'s resolver to
   extract the rich metadata block (authors with affiliations, year,
   venue, type, citations, OA status, topics, full abstract).
3. Dedupes by DOI (primary) or normalized title (fallback). Same
   address-union resolution as Stack 2 — when the same paper exists at
   multiple curated paths, the entry's `**Source paths:**` field is
   the union of all addresses.
4. Writes the canonical bibliography to `identified_papers_user.md`.

**Important clarification:** "no verify" does NOT mean "no OpenAlex." The
cap-stone still talks to OpenAlex — that's how the rich metadata gets
attached to each entry. "Verify" was the gate that REJECTED entries
based on OpenAlex misses; the cap-stone uses OpenAlex purely for
ENRICHMENT (every entry passes through, decorated with whatever OpenAlex
returns).

If OpenAlex can't resolve a specific paper (rare in the curated case
but possible for obscure papers, books, theses), the entry still goes
through with whatever metadata could be extracted from the PDF itself
(title from first page, etc.). No dead-letter queue — every PDF the
user curated lands in the bibliography.

---

## Cross-stack merger: `/merge-paper-lists`

Purpose: combine any subset of the three stack output files into one
canonical bibliography.

**Inputs (any subset):**
- `identified_papers_ai_info.md` (Stack 1)
- `identified_papers_repo_final.md` (Stack 2)
- `identified_papers_user.md` (Stack 3)

**Output:** `all_papers.md`

**Logic:**
- Dedup: DOI primary, normalized title fallback. Same key strategy used
  elsewhere in the pipeline.
- One entry per unique paper. First-seen wins. **No source tracking. No
  frequency counter.**
- `Source paths` fields (if present in inputs from Stacks 2 or 3) get
  unioned in the merged entry.

That's it.

---

## Architectural notes (covering both new stacks)

1. **Sister-stack rather than reuse** — Cardinal Rule. The existing
   verify, validate, and AI-enrich skills don't get touched, generalized,
   or extended.

2. **Parallel agent swarm at Stack 2's discover** — repositories can be
   huge. Sequential per-PDF processing is too slow. Stack 3 doesn't need
   this because the user-curated case is bounded by what a human can
   reasonably organize manually.

3. **Verify's role differs across stacks** — same OpenAlex check, but
   defending against different failure modes (hallucinations in Stack 1,
   misclassifications in Stack 2). In Stack 3 it's strictly redundant
   because the source itself eliminates both failure modes.

4. **Validate stays opt-in in Stack 2, omitted in Stack 3** — Stack 2
   carries the human gate because users may want to curate the
   auto-scan output. Stack 3 has no validate stage because curation
   already happened upstream (by the user, by hand, when they organized
   the folder).

5. **`-final` suffix on Stack 2's cap-stone, no suffix on Stack 3's** —
   Stack 2 picked `-final` because the four-stage chain needed a clear
   terminal marker. Stack 3's cap-stone parallels the Stack 1
   convention (`/identify-papers-ai` → `/identify-papers-user`),
   marking the two non-sister cap-stones as a matched pair.

6. **Source paths field is shared across both new stacks** — repository
   path information matters for both auto-scan and user-curated cases.
   The same metadata block extension applies. Existing stack format
   stays unchanged.

---

## Status

Design captured for both new stacks. Nothing built.

**Suggested build order:**

1. **`/identify-papers-user-folder`** first — simplest of all the new
   skills (flat folder + OpenAlex enrichment per PDF, no heuristics, no
   swarm). Validates that bulk OpenAlex resolution + the same-format
   output works end-to-end.

2. **`/identify-papers-user-tree`** — adds tree-walking on top of the
   folder skill. Symlink handling is the only new complexity.

3. **`/identify-papers-user`** — the Stack 3 cap-stone. Mostly
   composition of the above two with the metadata-enrichment loop;
   pattern is well-understood from Stack 1's `/identify-papers-ai`.

4. **`/identify-papers-repo`** — Stack 2's discover stage. Most complex
   single skill (parallel agent swarm + heuristic classification).
   Defer until Stack 3 has validated the metadata-enrichment patterns.

5. **`/identify-and-verify-repo-papers`** — once Stage 1 produces output,
   the verify gate is next. Dedup + address-union live here.

6. **`/identify-and-verify-and-validate-repo-papers`** — thin wrapper,
   well-understood GTK pattern.

7. **`/identify-papers-repo-final`** — Stack 2 cap-stone. Easy by the
   time everything else is built.

8. **`/merge-paper-lists`** — the cross-stack merger. Build last, after
   all three stacks have produced sample outputs to merge against.

## Out of scope for this document

- **Hybrid scans.** A repo that has both a hand-curated `papers/` folder
  AND messy sub-folders is currently handled by running BOTH Stack 3
  (on the curated folder) and Stack 2 (on the whole repo, accepting that
  it'll re-discover the curated stuff and the merge step will dedupe).
  A dedicated hybrid skill is not in scope.
