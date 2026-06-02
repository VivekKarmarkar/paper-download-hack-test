# paper-download-hack-test

Test workspace, reference artifacts, and design record for the **Paper → Bibliography OS** — a family of composable [Claude Code](https://claude.com/claude-code) skills that turn paper discovery (or an existing PDF library) into downloaded PDFs, compiled citation-rich bibliographies, and voice-dictated academic writing samples.

The skills themselves live in [VivekKarmarkar/claude-code-os](https://github.com/VivekKarmarkar/claude-code-os/tree/main/skills). This repo is the **test bed**: it captures the per-stage markdown artifacts the pipeline produces (frozen at generation time, so the data flow is auditable end-to-end), the rendered sample bibliographies, the one-page command guide, and the full design/decision trail — what was built, what was deliberately *not* built, and what was investigated and closed.

## The commands you actually run

Three (well, four) load-bearing commands; everything else is plumbing they call. See `bibliography_os_guide.pdf` for the color-coded one-pager.

| When | Command | Result |
|---|---|---|
| **I already have everything** | `/generate-bibliography <folder>` | A folder/tree of PDFs → `bibliography.pdf`, one merged, deduplicated, clickable-DOI references PDF. One shot, in the background. |
| **Talk in batches, then merge** | `/identify-papers-ai-ur <papers>` ×N → `/generate-bibliography-cumulative <folder>` | Resolve the papers you name across a session (accumulating), then merge with your on-disk folder. |
| **Walk-and-talk a section (disk-aware)** | `/voice-writing-sample-all` | Dictate a draft over Telegram; it discovers (reusing what's already on disk), resolves, writes the section, and emails a PDF whose references are numbered `[1],[2]…` in order of first citation. |

## Under the hood — the discovery pipeline

Each load-bearing command fans out into ~20 single-purpose skills. The original discovery→download chain:

```
discover (training-data + websearch swarm)
   ↓
verify (OpenAlex match per entry)
   ↓
validate (default approve-all, or GTK dialog with --interactive)
   ↓
AI-enrich (OpenAlex metadata block per entry)
   ↓
download (3-tier cascade: publisher-direct + Unpaywall → arXiv → Sci-Hub)
```

Each arrow is a separate globally-available skill, doing one thing well. Each writes a flat human-readable markdown file that the next stage consumes — no JSON schemas, no config glue, just lines you can hand-edit between stages if you want to take the wheel.

| Stage | Skill | Output file |
|---|---|---|
| Discover (memory) | [`identify-papers-training-data`](https://github.com/VivekKarmarkar/claude-code-os/tree/main/skills/identify-papers-training-data) | `identified_papers_training_data.md` |
| Discover (web swarm) | [`identify-papers-websearch`](https://github.com/VivekKarmarkar/claude-code-os/tree/main/skills/identify-papers-websearch) | `identified_papers_websearch.md` |
| Verify | [`identify-and-verify-papers`](https://github.com/VivekKarmarkar/claude-code-os/tree/main/skills/identify-and-verify-papers) | `identified_and_verified_papers_info.md` |
| Validate | [`identify-and-verify-and-validate-papers`](https://github.com/VivekKarmarkar/claude-code-os/tree/main/skills/identify-and-verify-and-validate-papers) | `identified_and_verified_and_validated_papers_info.md` |
| AI-enrich | [`identify-papers-ai`](https://github.com/VivekKarmarkar/claude-code-os/tree/main/skills/identify-papers-ai) | `identified_papers_ai_info.md` |
| Download | [`literature-download-hack`](https://github.com/VivekKarmarkar/claude-code-os/tree/main/skills/literature-download-hack) | `papers/<sanitized-DOI>.pdf` (gitignored here) |

## The three stacks

The system grew into parallel stacks that share the same shape but differ by source/trust, then a bibliography + writing layer on top:

- **Stack 1 — AI** (`identify-papers-ai` / `-ai-ur`): generative discovery → verify → validate → OpenAlex-enrich. Hallucination-defended.
- **Stack 3 — user** (`identify-papers-user*`): a hand-curated disk library → OpenAlex-enrich. No verify/validate (curation *is* the validation).
- **`-all` stack** (`identify-papers-all-ur`, `all-bibliography*`, `voice-writing-sample-all*`): disk-preferring + user-restricted + abstract-free. Reuses papers already cited in an on-disk `bibliography.tex`, falling back to the AI stack only for the rest; feeds the voice-writing-sample skills with `[1],[2]`-by-appearance citations.
- **Bibliography + writing layer**: `*-bibliography` renderers (MD → LaTeX → PDF, clickable DOIs), `merge-*` mergers, the `generate-bibliography*` umbrellas, and `voice-writing-sample-all*`.
- **Stack 2** (an automated messy-repo swarm) was designed and then **eliminated** — see `stack2_elimination_reasoning.md`.

## The test corpus (discovery run)

Topical context used to drive the captured discovery run:

> *AI narrows the experimental configuration space: AI algorithms can discover optimal experimental configurations. Example: Mario Krenn at Max Planck (advisor: Anton Zeilinger) using AI to find quantum entanglement experiment setups.*

Resulting corpus in `identified-papers/`:

| File | Contents | Count |
|---|---|---|
| `identified_papers_training_data.md` | Memory-only candidates from model training data | 10 |
| `identified_papers_websearch.md` | Web-swarm candidates (general web + Scholar + lab pages) | 22 |
| `identified_and_verified_papers_info.md` | OpenAlex-VERIFIED entries from both files, deduped + sorted chronologically | 24 |
| `identified_and_verified_and_validated_papers_info.md` | Approved entries (this run used the default approve-all) | 24 |
| `identified_papers_ai_info.md` | Full OpenAlex metadata block per entry (authors, year, venue, type, citations, OA status, topics, concepts, abstract) | 24 entries |

The `identified_papers_info.md` and `identified_papers_user_info.md` files are placeholder slots from earlier brainstorm rounds, kept for a faithful audit trail.

## Empirical results from the download stage

Running [`literature-download-hack`](https://github.com/VivekKarmarkar/claude-code-os/tree/main/skills/literature-download-hack) over the 24 verified entries produced this 3-tier hit pattern:

| Tier | Path | Hits | Notes |
|---|---|---|---|
| 1 | Publisher-direct + Unpaywall | 14/24 | Nature, Springer, Quantum journal, APS papers with green/gold OA |
| 2 | arXiv preprint | 6/10 of the rest | The Krenn group puts everything on arXiv — promoting this tier ahead of Sci-Hub means most modern papers never need the shadow library |
| 3 | Sci-Hub via Playwright | 4/10 of the rest | Older paywalled papers (NJP 2016, PNAS 2018, RPP 2018, PNAS 2019) |
| **Total** | | **24/24** | |

The actual PDFs are **not** committed here (gitignored — copyright + ~110 MB). This repo only contains the metadata trail.

## What's in this repo

- **`identified-papers/`** — the per-stage discovery artifacts above.
- **`identified_papers_ai_cumulative.md`** — the cumulative AI list accumulated across runs by a PostToolUse hook.
- **`test-example/`** — sample rendered bibliographies (user / ai-cumulative / merged) with clickable DOIs.
- **`bibliography_os_guide.{pdf,tex}`** — the one-page, color-coded command reference.
- **`approve_papers_dialog.py`** — the original one-off GTK approval dialog (later generalized into the validate skill's helper).
- **Design & decision record:**
  - `new_ideas.md` — the three-stack architecture sketch.
  - `finishing_touches.md` — live next-steps (now: just the capstone website).
  - `stack2_elimination_reasoning.md` — why the messy-repo swarm was dropped.
  - `questions_zotero.md` — the Zotero investigation + verdict (not pursued).
  - `insights.md` — essential-vs-accidental complexity, agentic debugging, "presentation conditions the solver."
  - `documentation_ideas.md` — plan for the capstone project website.
  - `INCIDENT_REPORT*.md` — debugging write-ups.

## What's intentionally NOT in this repo

- `papers/` — downloaded PDFs (~110 MB, mostly Sci-Hub-sourced; copyright-restricted). Gitignored.
- `affection.md` — personal notes. Gitignored.
- `.playwright-mcp/` — browser snapshots from the Sci-Hub navigation step.
- `.claude/` — local Claude Code project state.

## Reproducing the discovery corpus

In a fresh project directory, with the pipeline skills installed (clone `claude-code-os` and copy the relevant `identify-*` / `literature-*` folders into `~/.claude/skills/`):

```bash
claude
> /literature-download-hack <your topical context here>
```

That single command bootstraps the pipeline from scratch: runs the two discovery channels in parallel, verifies via OpenAlex, validates (default approve-all), enriches with metadata, then downloads via the 3-tier cascade. Pass `--interactive` for the GTK dialog where you tick which papers proceed.

## Status

- ✅ **86 / 87** references exactly correct on a real ~87-paper literature-review tree via `/generate-bibliography` (incl. an obscure 1949 paper), generated in the background in ~40 minutes.
- ✅ **`/voice-writing-sample-all` validated end-to-end** — a dictated inverse-problem argument became a compiled, correctly-cited 4-page academic note; disk-aware OpenAlex resolution even fixed voice-garbled author names.
- ✅ Stack 2 eliminated; Zotero investigated and closed.

## Tech stack

- **Python 3** (`urllib`, `subprocess`, `re`, `json` — no third-party deps for the helpers)
- **PyGObject (Gtk 3)** for the validation dialog
- **OpenAlex API** for verification + metadata, **Unpaywall** for OA lookup, **arXiv** for preprints, **Sci-Hub via Playwright (MCP)** for the paywalled long tail
- **LaTeX (pdflatex + hyperref)** for the rendered bibliographies and writing samples
- **Claude Code** as the orchestration layer (voice in via Telegram)

## License

No license file. Treat the artifacts here as illustrative test data; the skill source lives in [claude-code-os](https://github.com/VivekKarmarkar/claude-code-os) under whatever license that repo carries.
