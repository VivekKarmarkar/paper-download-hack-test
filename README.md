# paper-download-hack-test

Test workspace and reference artifacts for the **literature-discovery pipeline** — a chain of six composable [Claude Code](https://claude.com/claude-code) skills that turn a topical context into a folder of downloaded research PDFs.

The skills themselves live in [VivekKarmarkar/claude-code-os](https://github.com/VivekKarmarkar/claude-code-os/tree/main/skills). This repo is the **test bed**: it captures the per-stage markdown artifacts that the pipeline produces, frozen at the moment the corpus was generated, so the data flow between stages is auditable end-to-end.

## The pipeline

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

## The test corpus

Topical context used to drive this run:

> *AI narrows the experimental configuration space: AI algorithms can discover optimal experimental configurations. Example: Mario Krenn at Max Planck (advisor: Anton Zeilinger) using AI to find quantum entanglement experiment setups.*

Resulting corpus in `identified-papers/`:

| File | Contents | Count |
|---|---|---|
| `identified_papers_training_data.md` | Memory-only candidates from model training data | 10 |
| `identified_papers_websearch.md` | Web-swarm candidates (general web + Scholar + lab pages) | 22 |
| `identified_and_verified_papers_info.md` | OpenAlex-VERIFIED entries from both files, deduped + sorted chronologically | 24 |
| `identified_and_verified_and_validated_papers_info.md` | Approved entries (this run used the default approve-all) | 24 |
| `identified_papers_ai_info.md` | Full OpenAlex metadata block per entry (authors with affiliations, year, venue, type, citations, OA status, topics, concepts, full abstract) | 24 entries / 501 lines |

The `identified_papers_info.md` and `identified_papers_user_info.md` files are placeholder slots from earlier brainstorm rounds, kept for the sake of a faithful audit trail.

## Empirical results from the download stage

Running [`literature-download-hack`](https://github.com/VivekKarmarkar/claude-code-os/tree/main/skills/literature-download-hack) over the 24 verified entries produced this 3-tier hit pattern:

| Tier | Path | Hits | Notes |
|---|---|---|---|
| 1 | Publisher-direct + Unpaywall | 14/24 | Nature, Springer, Quantum journal, APS papers with green/gold OA |
| 2 | arXiv preprint | 6/10 of the rest | The Krenn group puts everything on arXiv — promoting this tier ahead of Sci-Hub means most modern papers never need the shadow library |
| 3 | Sci-Hub via Playwright | 4/10 of the rest | Older paywalled papers (NJP 2016, PNAS 2018, RPP 2018, PNAS 2019) |
| **Total** | | **24/24** | |

The actual PDFs are **not** committed here (gitignored — copyright + 110MB). This repo only contains the metadata trail.

## Files in this repo

```
.gitignore                              # Excludes papers/, affection.md, .playwright-mcp/, .claude/
README.md                               # This file
approve_papers_dialog.py                # The original one-off GTK approval dialog (later
                                        # generalized into the validate skill's helper)
identified-papers/                      # The pipeline's intermediate + final markdown artifacts
   ├── identified_papers_training_data.md
   ├── identified_papers_websearch.md
   ├── identified_and_verified_papers_info.md
   ├── identified_and_verified_and_validated_papers_info.md
   ├── identified_papers_ai_info.md
   ├── identified_papers_info.md         # Placeholder (kept for audit trail)
   └── identified_papers_user_info.md    # Placeholder (kept for audit trail)
```

## What's intentionally NOT in this repo

- `papers/` — 35 downloaded PDFs (~110 MB). Mostly Sci-Hub-sourced; copyright-restricted; gitignored.
- `affection.md` — personal notes. Gitignored.
- `.playwright-mcp/` — browser snapshots from the Sci-Hub navigation step.
- `.claude/` — local Claude Code project state.

## Reproducing this corpus

In a fresh project directory:

```bash
# Make sure the 6 pipeline skills are installed (clone claude-code-os and copy
# the 6 identify-* / literature-* folders into ~/.claude/skills/), then:

claude
> /literature-download-hack <your topical context here>
```

That single command bootstraps the pipeline from scratch: runs the two discovery channels in parallel, verifies via OpenAlex, validates (default approve-all), enriches with metadata, then downloads via the 3-tier cascade. The intermediate artifacts land in `identified-papers/`, the PDFs land in `papers/`.

For the curated walkthrough variant — where a GTK dialog opens mid-flow and you tick which papers proceed to download — pass `--interactive`:

```bash
> /literature-download-hack --interactive <context>
```

## Tech stack

- **Python 3** with `urllib`, `subprocess`, `re`, `json` (no third-party deps for the helpers)
- **PyGObject (Gtk 3)** for the validation dialog
- **OpenAlex API** for verification + metadata
- **Unpaywall API** for OA-copy lookup
- **arXiv** for preprint fallback
- **Sci-Hub via Playwright (MCP)** for paywalled long-tail papers
- **Claude Code** as the orchestration layer

## License

No license file. Treat the artifacts in this repo as illustrative test data; the actual skill source is in [claude-code-os](https://github.com/VivekKarmarkar/claude-code-os) under whatever license that repo carries.
