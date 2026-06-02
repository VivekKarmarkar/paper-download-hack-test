# Questions — Zotero investigation

A slow, step-by-step evaluation of whether (and how) Zotero fits into / replaces /
complements the paper→bibliography system. One question at a time.

---

## Question 1 — Can Zotero replace `/user-bibliography` + `/generate-bibliography`?

**Setup.** On local disk I have my papers stored in a tree of folders — possibly
complicated, many branches. It houses *mainly* research-paper PDFs, but there may be
the occasional PDF that is not a paper, and (rarely) a file that is not a PDF.

**What our skills do today.** `/user-bibliography` + `/generate-bibliography` take that
tree and produce `bibliography.tex` (LaTeX) + `bibliography.pdf` (compiled, with
clickable DOIs). Tested yesterday on a real ~87-paper literature-review tree: **86 of 87
references exactly correct** (author, title, DOI), including an obscure 1949 paper.

**The question.** Given the same input (the tree) and the same desired output
(`bibliography.tex` + `bibliography.pdf`, clickable DOIs), can **Zotero** achieve it?
If we removed those two skills and replaced them with Zotero, would we get **86/87 — or
better (87/87)** — on a corpus like this?

*(Discussion held 2026-06-02. Verdict below.)*

---

## Verdict (2026-06-02): do NOT pursue Zotero. Path closed.

The fit assessment lands cleanly on "drop it" — checked rigorously, not as motivated
reasoning. What Zotero *uniquely* offers, against this project's reality:

- **A browsable, synced GUI library across devices** → already solved your way: the
  disk tree IS your library, and it's MORE transparent (human-readable folders) than
  Zotero's opaque hashed internal storage.
- **Cite-while-you-write in Word / Google Docs** → you write in LaTeX, voice-driven.
  Not a need.
- **Capture-at-discovery + library upkeep** → already subsumed by
  `/identify-papers-ai-ur`, and `/identify-papers-all-ur` goes further (skip
  re-discovery for papers already on disk).

So every unique Zotero offering is either already solved your way or something you
don't want. The killer-feature comparison is also favorable: ours is
**cite-while-you-SPEAK via an AI agent** (a rung above cite-while-write), with
discovery pipelines built in.

**Why this is the same decision-shape as Stack 2 elimination:** don't build OR adopt a
complex thing whose grain runs opposite to your need just because it exists.
Zotero's grain is *capture-at-discovery, metadata-first, GUI-library* — the temporal
and structural opposite of "I already have a finished disk-tree archive; batch it to a
bibliography." Investigating deeper (pyzotero, building a Zotero MCP) would be effort
against a bad fit — the precise waste a bottom-up philosophy exists to avoid.

**Key technical reason it's not even an OpenAlex competitor:** the Zotero API is a
*library* API (CRUD on your own shelf), not a *resolution* API (query the global
scholarly graph for any paper). It can only hand back what you already filed, with
metadata its weaker recognizer produced at ingest. So it could at most be an
*integration target* (push output into a Zotero library), never a replacement for the
OpenAlex resolution slot.

**Back-pocket trigger (not now):** if cross-device sync, a visual browsable library, or
collaborators who write in Word ever become real needs, Zotero is the tool *for that
day*. Until that trigger fires, YAGNI. The current system is tested (86/87 + two smaller
tests) and practically good to use.

