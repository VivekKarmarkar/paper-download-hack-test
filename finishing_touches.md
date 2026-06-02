# Finishing touches — next steps

Remaining items after the AI stack (Stack 1) and user-curated stack (Stack 3) shipped,
and after the `-all` stack was built on 2026-06-02. (Stack 2 is eliminated — see
`stack2_elimination_reasoning.md`. The Zotero path was investigated and CLOSED on
2026-06-02 — not pursued; reasoning + verdict in `questions_zotero.md`.)

---

## 1. Test the `-all` stack (BUILT — testing remains, on Vivek's end)

The disk-preferring, user-restricted `-all` stack is BUILT and unit-tested on real
data (Cardinal-Rule-clean — composes existing skills, modifies nothing). What was
shipped (2026-06-02):

- **`/identify-papers-all-ur`** → `identified_papers_all.md` (+ `identified_papers_all_cumulative.md`
  via a PostToolUse hook). Checks `bibliography.tex` in the CWD root ONCE: reuses each
  user-referenced paper already cited there (no re-resolve), falls back to
  `/identify-papers-ai-ur` for the rest (full fallback if no `bibliography.tex`).
  Output is abstract-free.
- **`/all-bibliography`** + **`/all-bibliography-cumulative`** → render the `-all`
  list(s) to `all_bibliography(.tex/_cumulative.tex)+pdf` (clones of the ai-bibliography
  pair; cumulative dedupes by DOI).
- **`/voice-writing-sample-all`** + **`/voice-writing-sample-all-cumulative`** →
  `-all` sisters of `/voice-writing-sample`. Discovery via `/identify-papers-all-ur`;
  references rendered by `/all-bibliography(-cumulative)` and embedded as a keyed
  `\begin{thebibliography}` fragment (`writing_bibliography.tex`) so the compiled PDF
  numbers references `[1],[2],...` in ORDER OF FIRST CITATION (native `\cite`, NO bibtex).

**REMAINING (Vivek, ~2026-06-03):** test `/voice-writing-sample-all` end-to-end by
hand — write a short fresh piece (walk-and-talk style) in the separate project where a
bibliography has already been generated (so `bibliography.tex` exists at the CWD root and
the disk-preference path actually runs), then confirm the emailed PDF cites correctly with
`[1],[2]`-by-appearance references. Everything is unit-tested; this is the real-world,
end-to-end validation. Expect to debug live and course-correct.

## 2. Project website + interactive architecture diagrams (capstone)

After the architecture is frozen (i.e. after the `/voice-writing-sample-all` test
above), build the project website: an interactive diagram of the skill architecture
(dashboard → plumbing, color-coded by stack, with the substrate strata visible) plus an
insight / reflection section. The act of diagramming doubles as consolidation — a
reachability pass from the 4 load-bearing commands sorts every skill into live plumbing
vs. fossils. Full plan in `documentation_ideas.md`. The OS already has
`project-showcase-website` / `makewebpage` skills to make it efficient.

*(The Zotero investigation that previously sat here was completed and CLOSED — not
pursued. See `questions_zotero.md` for the verdict.)*
