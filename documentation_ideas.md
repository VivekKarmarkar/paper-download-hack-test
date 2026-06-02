# Documentation ideas — for the eventual project website / architecture write-up

Captured 2026-06-02. This is the plan for using the (future, capstone) project website
not just as a showcase but as a consolidation-and-reflection artifact. Verbatim seed
from the conversation, lightly tidied.

---

**Diagramming IS the consolidation — not just a place to reflect.**

You can't draw an accurate architecture diagram without tracing what connects to
what, so it forces a **reachability pass**: start from the 4 load-bearing commands,
follow the edges, and every skill sorts itself into one of two piles —

- **Live plumbing** — reachable from the dashboard (justified, load-bearing).
- **Fossils** — nothing live calls them anymore (the wrong-substrate attempts).

The diagram does the live-vs-vestigial sort almost mechanically. That's consolidation,
done by drawing.

**"Right stack-template, wrong substrate" — why the set sprawled.**

The STACK SHAPE (discover → verify → validate → enrich; folder/tree × pdf/vision) was
correct and stable. The SUBSTRATE — *how you actually read the paper*: text-extract →
PDF-parse → vision-with-background-agents — was wrong early, so each substrate iteration
spawned a whole parallel stack. The skills came in stacks because the **template held
while the substrate changed underneath**. So the set has **STRATA** — sedimentary
layers, one per substrate epoch — and the Cardinal Rule (never delete) preserved them
all. The diagram will literally show this as parallel same-shape stacks, and you mark
which substrate won.

**The insight section.**

Its natural home is the website: essential-vs-accidental complexity, the clever hacks,
"presentation conditions the solver," with the real examples. `insights.md` is the seed;
the website is where it becomes narrative + illustrated, which lands harder than prose.

**It closes the "why so many skills?" loop completely.**

Some skills are live plumbing (justified). Some are fossils of the climb to the right
substrate (explained, not waste — they were the cost of finding it). Naming the dead
ends is its own closure.

**Why this goes LAST.**

You want the substrate decisions final before you map the strata, or you'll diagram a
layer that's about to fossilize. Sequence: **test → Zotero → then this capstone.**

---

## Concrete documentation deliverables (when we get there)

1. **Interactive architecture diagram** — the dashboard (4 load-bearing commands) on
   top, the plumbing fanning out below, color-coded by stack (AI / user / all), with the
   substrate strata visible and the "winning substrate" marked. Reachability from the 4
   commands distinguishes live plumbing from fossils.
2. **An insight / reflection section** — the essential-vs-accidental taxonomy, agentic
   debugging as a new literacy, and presentation-conditions-the-solver, each with a
   concrete example from this project (the greedy-author-regex bug, the cumulative
   double-append, the inverse-problem cross term, the general-incident-report technique).
3. **A "strata" / archaeology view** — the wrong-substrate epochs as honest history:
   what we tried first, why it was the wrong substrate, what the right one turned out to
   be, and which skills are fossils of each epoch.

Related: `insights.md`, `finishing_touches.md`, project memory (`all-stack-architecture`).
