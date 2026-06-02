# Incident Report — Bibliography Hallucinations from `/identify-papers-user` Stack

**Date:** 2026-05-31
**Session CWD:** `/home/vivekkarmarkar/Python Files/merge-skill-t7`
**Outcome:** Compiled `bibliography.pdf` contained 3 hallucinated entries out of 4 from the user-curated `goodpapers/` folder (75% failure rate on that stack).

---

## 1. What the user expected

The user had a folder `goodpapers/` containing PDFs they had personally curated:

The user invoked `/identify-papers-user @goodpapers/` and reasonably expected: *"these PDFs are legit — figure out what each one is and put it in the bibliography."*

The natural reading of "identify a paper from a PDF" is: open the PDF, look at the title block on page 1, extract title + authors (and ideally the DOI printed on the page), then enrich via OpenAlex.

## 2. What the pipeline actually did

Two components were involved:

### 2a. `/identify-papers-user-tree` → `helpers/extract_tree_candidates.py`

For each `*.pdf` found, this helper produced a "candidate title" by:

1. Calling `pdfinfo` and reading its **`Title` metadata field** — an embedded PDF property that authors and exporters often leave blank, set to a garbage default, or fill with a working name unrelated to the paper.
2. **Falling back to the filename slug** (filename minus extension, underscores → spaces) when `pdfinfo` returned an empty Title.

This produced GARBAGE

**Critically, `pdftotext` was never invoked on the PDF body.** The actual page-1 title block, author list, DOI banner, and abstract — all sitting in plain text inside each PDF — were never read.

### 2b. `/identify-papers-user` → `helpers/enrich_user_candidates.py`

This helper took each candidate's title string and passed it to `/paper-metadata`'s `resolve()`, which:

1. Hits `https://api.openalex.org/works` with the title as a fuzzy search query
2. Accepts whatever OpenAlex returns as the top hit
3. Returns that record's metadata (DOI, authors, year, venue, abstract)

No score threshold. No author cross-check. No DOI verification against the PDF. No "did we even find the right paper" gate.

The skill description explicitly states this is by design:

> Stack 3 has no verify gate. Stack 3 trusts the source. Every PDF the user curated lands in the bibliography.

The fatal assumption: "trusting the source" was interpreted as "trusting the filename string we generated to match a real paper in OpenAlex's index." But filenames are not paper identities — they're whatever the user named the file.

## 3. Root cause

**The skill is mis-named relative to what it does.**

`/identify-papers-user` and `/identify-papers-user-tree` claim to "identify papers." A reasonable reading of that phrase is *figure out which paper each PDF actually is*. The implementation instead does *fuzzy-match a filename-derived string against OpenAlex and accept the top hit*. Those are different operations. The former reads the PDF; the latter doesn't.

The actual identification signal — title text, author block, DOI banner, arXiv ID — lives **inside the PDF**, on page 1, accessible via `pdftotext -l 1`. The pipeline never reads it.

This is not a bug in any single line of code. It is a design choice in the skill spec that becomes catastrophic when the user's filenames don't happen to be high-fidelity titles. For a researcher's curated folder, where files are named based off convenience, this is the common case, not the edge case.

## 4. My culpability on top of the design flaw

I did notice two of the four mismatches during the `/identify-papers-user` step. My output at that time included:

> **Flagging two suspect resolutions** (no action taken — Stack 3 trusts the source)

I correctly identified the mismatches. I then **proceeded to compile both wrong entries into the merged bibliography and into the final PDF anyway**, deferring to the skill's "Stack 3 trusts the source" rule.

This was the wrong call. When the user instructs "just identify these papers," the implicit contract is that obviously wrong matches should be corrected — not shipped with a footnote. The correct response when I saw the mismatch was: stop, open the PDF, extract the real title, re-resolve. That would have taken under a minute per entry and would have produced an accurate bibliography.

I did not catch the third mismatch because the OpenAlex result was author-matched and title-close enough to look right at a glance. Only reading the PDF banner reveals the wrong year. This one was a silent failure — no flag, just wrong.

I also did not catch the fourth issue because the authors matched and the title matched. The PDF header banner makes the correct citation unambiguous, but only if you open the PDF.

## 5. What would have prevented this

A single change in `extract_tree_candidates.py`:

Replace the `pdfinfo` Title extraction with a `pdftotext -l 1 <pdf>` call, then either:

- **Option A — DOI-first:** Regex-scan the page-1 text for `10\.\d{4,9}/[^\s]+`. If found, skip OpenAlex title search entirely and look up the DOI directly. This would have nailed the Beber paper (DOI in the IEEE header banner) and would not have hurt the others.

- **Option B — Real title:** Take the first 1–3 substantive non-whitespace lines of page-1 text as the candidate title. These are almost always the real title and author list.

- **Option C — Both, with arXiv ID as a third probe:** Regex `arXiv:\d{4}\.\d{4,5}` on page 1, look up via OpenAlex's `doi:10.48550/arXiv.<id>` shortcut.

Any of these three would have correctly identified all four `goodpapers/` PDFs without changing any other part of the pipeline. The candidate-line format stays the same, the enrichment step stays the same, the merge step stays the same. Only the title-extraction step changes.

The work to read a PDF's page-1 text is trivial. Skipping it produced a bibliography that misattributes, not a useful bibliography.

## 6. Honest summary

The pipeline did exactly what its code said to do. The code does not do what the skill name says it does. I noticed two of the three failures in real time, named them out loud, and shipped them anyway because the skill rules said to. That last step — shipping known-wrong entries — was on me, not on the skill.
