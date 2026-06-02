# Stack 2 elimination — reasoning

**Decision (2026-06-01): Stack 2 is eliminated. It will not be built.**

Stack 2 (as designed in `new_ideas.md`) was the "sister stack for messy repos":
an automated parallel-agent swarm that scans a whole repository tree,
heuristically classifies which PDFs are papers, then uses a verify gate to catch
the misclassifications the swarm inevitably makes. Four new skills, the most
complex machinery in the whole system.

We discussed it and eliminated it. This file records WHY, so the decision isn't
relitigated later. This **supersedes Stack 2 in `new_ideas.md`** — the system
going forward is Stack 1 (AI) + Stack 3 (user-curated) + the cross-stack merger
(`/merge-paper-lists`).

## Why eliminate it

1. **Worst cost/reliability trade in the system.** Stack 2's discover stage is a
   parallel agent swarm + heuristic classification — the single skill
   `new_ideas.md` itself flags as "most complex, defer until last." High build
   cost, large error surface, slow and expensive to run.

2. **It's an anti-pattern: manufacture a noisy data source, then spend machinery
   cleaning it.** The swarm blindly scans everything (slide decks, manuals,
   receipts included), creating noise, and then the verify gate exists purely to
   remove that self-inflicted noise. Cleaner to never create the noise.

3. **Skills are model-driven, not hard-coded — so classification can be a runtime
   instruction, not coded machinery.** This is the crux. A hard-coded workflow
   couldn't absorb "ignore the things that aren't papers" as an instruction — it
   would need exactly the coded heuristic the swarm represents. Because the
   Stack 3 skills are prose/model-interpreted, **natural-language context IS the
   classifier.** Stack 2's entire reason for existing collapses once the discover
   step can take human judgment as a parameter.

## The two-part replacement (strictly better for the actual workflow)

1. **Human tree discipline — an augmented Unix philosophy for the file system.**
   Keep literature-review trees clean BY CONSTRUCTION:
   - A pure `literature/` tree containing papers only.
   - Separate `experiments/` and `supplementary-information/` trees for podcasts,
     highlight-skill runs, notes, connected-graph images, per-paper experiment
     folders.
   - When you want to tinker with a paper (convert to podcast, read with
     highlighting, take notes), COPY it into an isolated `experiment_*` subfolder
     and work there — the literature tree stays pure.

   A clean source by construction means there is no misclassification to defend
   against in the first place. The same discipline that builds lean, modular
   skills (Unix philosophy) applies to keeping the literature trees lean.

2. **Context-augmented Stack 3 for residual noise (old, already-messy folders).**
   Point `/identify-papers-user` or `/identify-papers-user-tree` at a noisier old
   folder and pass natural-language context — e.g. "some files may not be PDFs and
   some PDFs may not be papers; ignore those." Because the skills are model-driven,
   any session applies that judgment inline while walking the tree. No swarm, no
   heuristic-classification skill, no dedicated verify gate.

   (Demonstrated in the 2026-06-01 scale-test run, where exactly this context was
   passed to a `/generate-bibliography` goal over a real, somewhat-messy tree.)

## What is NOT lost by dropping Stack 2

- The address-union / `Source paths` feature — "do I have duplicate copies of
  this paper, and where do they live?" — already lives in Stack 3. Eliminating
  Stack 2 costs nothing there.

## The one thing Stack 2 uniquely had — and why YAGNI applies

The only capability Stack 2 offered that the replacement doesn't is **massive
parallel throughput on a blind scan of thousands of PDFs**. That is simply not the
workflow: the literature trees are bounded (one human's curated library) and, with
the discipline above, clean. If a genuine huge-blind-scan need ever materializes,
build that capability THEN, scoped to that real need — not speculatively now.
