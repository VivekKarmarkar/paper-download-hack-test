# Finishing touches — next steps

Status after the AI stack (Stack 1), user-curated stack (Stack 3), and the `-all` stack
all shipped. Closed: Stack 2 (eliminated — see `stack2_elimination_reasoning.md`) and the
Zotero path (investigated + CLOSED, not pursued — verdict in `questions_zotero.md`).

**The `-all` stack is now fully validated end-to-end** (see "Done" below), so the only
remaining active item is the capstone project website.

---

## 1. Project website + interactive architecture diagrams (capstone)

Now that the architecture is frozen, build the project website: an interactive diagram of
the skill architecture (dashboard → plumbing, color-coded by stack, with the substrate
strata visible) plus an insight / reflection section. The act of diagramming doubles as
consolidation — a reachability pass from the 4 load-bearing commands sorts every skill into
live plumbing vs. fossils. Full plan in `documentation_ideas.md`. The OS already has
`project-showcase-website` / `makewebpage` skills to make it efficient.

---

## Done

- **`-all` stack BUILT** (2026-06-02, Cardinal-Rule-clean): `/identify-papers-all-ur`
  (+ cumulative hook), `/all-bibliography` (+ `-cumulative`), `/voice-writing-sample-all`
  (+ `-cumulative`), and the shared `build_writing_bibliography.py` helper.
- **`-all` stack VALIDATED END-TO-END** (2026-06-02). `/voice-writing-sample-all` was run
  for real: Vivek dictated his "superposition without redundancy" inverse-problem argument
  as voice messages; the skill produced a genuine 4-page academic note
  ("Superposition Without Redundancy: How a Summed-Force Experiment Reshapes the Loss
  Landscape in Mechanical Inverse Problems") and emailed it. Confirmed working:
  references `[1]`–`[7]` in exact order of first citation; the proof
  (`L_new = 2·L_old + 2⟨ε1,ε2⟩`) correct; disk-aware OpenAlex resolution fixed
  voice-garbled author names (Bauman→Bouman, Ullman→Uhlmann, Alan Blanchett→
  Allen-Blanchette, "deviolate"→Dirichlet); disk-reuse path ran; honest provenance note.
- **86/87 real-world scale test** of `/generate-bibliography` on the 87-paper review.
- **Stack 2** eliminated; **Zotero** investigated and closed.
