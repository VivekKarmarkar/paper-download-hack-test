# Finishing touches — next steps

Two remaining items after the AI stack (Stack 1) and user-curated stack (Stack 3)
shipped. (The scale test is already running, and Stack 2 is decided — eliminated,
nothing to build; its reasoning lives in `stack2_elimination_reasoning.md`.)

---

## 1. Ship the routing layer + 2nd-generation voice-writing-sample

Two NEW skills (Cardinal Rule: build new, don't modify). Both are thin wrappers
that COMPOSE existing skills — no new heavy machinery.

**`/identify-papers-all`** — an intelligent wrapper over `/identify-papers-ai`
(and its restricted sibling) with a **disk-preference**:

- First check whether a faithful, tested bibliography already exists on disk for
  the papers in scope.
- The "is it faithful?" gate must be a REAL check, **not** "a file exists" (a
  stale/partial bibliography is a footgun). **Reuse `/cross-check-papers-user`** —
  it already reconciles the on-disk PDF set against a bibliography. If cross-check
  says the on-disk bibliography faithfully represents the papers → pull straight
  from it (cheap, no re-resolve).
- Else fall back to `/identify-papers-ai-ur` (run the real pipeline + the
  user-restriction layer).

**2nd-gen `voice-writing-sample`** — same composer as today, but its
paper-discovery step calls `/identify-papers-all` instead of `/identify-papers-ai`
directly. So when a faithful bibliography already exists on disk, the writing flow
reuses it instead of rediscovering from scratch.

## 2. Investigate Zotero

Compare this system against Zotero (a reference manager) before deciding whether
any of it should be offloaded.

- Zotero overlaps on the BACK half: store PDFs + metadata, dedup/merge,
  identifier → metadata (paste DOI / arXiv / PMID), and citation rendering in
  thousands of CSL styles (genuinely better than our LaTeX builder at styling).
- Zotero does NOT do the FRONT half: discovery from a topic / vague description,
  hallucination-verification against OpenAlex, vague natural-language reference
  resolution ("the Horstmeyer microscope paper"), the download cascade
  (paper-download-hack), or agent / voice-driven orchestration composable into
  other skills.
- Verdict so far (base knowledge only): **complementary, not a replacement.**
  Possible hybrid worth probing — our pipeline does discover → verify → restrict,
  then export to Zotero / BibTeX (via `pyzotero`) for library management +
  citation styling. The investigation: does Zotero's API / translators cover
  enough of the back half to be worth the external dependency, given the whole
  system is otherwise self-contained and voice-driven?
