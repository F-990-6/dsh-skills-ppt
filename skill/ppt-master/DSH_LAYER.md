## DSH Layer — Evidence Narrative (local addition)

**Status**: added by the `dsh-skills-ppt` plugin; upstream ppt-master does not ship
this section. It governs every Generate PPTX run in this install: each run classifies
itself against it, and where the layer applies it outranks a mode preset's own
skeleton. It governs *what the deck argues*; routes, gates, layout craft, and export
mechanics stay exactly as written below.

**Classify once, before routing.** Use the evidence narrative when the deck must
persuade a named audience that something is worth doing, trusting, or paying for —
客户演示、产品评审、立项 / 结项、路演、复盘、竞品对比、提案、卖点介绍, or any
"why this exists / why it wins" request. Do not impose it on teaching, reference,
status, minutes, or archival decks unless the user asks for a pitch. The decision is
part of the plan, never left to page authoring:

- Default (Generate PPTX): §III Theme Style carries `- **Narrative spine**: dsh-evidence-arc`,
  or `- **Narrative spine**: off — <reason>`. Every Default deck records one of the
  two; `off` with a reason is a first-class answer, not a skip.
- Quick: a persuasion deck records the same line at the head of its `narrative.md`
  (see below); a non-persuasion Quick deck decides in context and writes no artifact.

**The four beats — one page each, in this order.** Additional pages may sit between
them; each beat appears exactly once.

| Beat | Page job | The page must carry |
|---|---|---|
| `hook` | Make the scale concrete in one number | One traceable number plus the outcome as a promise, not a category |
| `conflict` | Show why a human cannot win this by hand | Two opposed, quantified costs — what the person pays vs what the window allows — and the loss that follows |
| `method` | Answer each cost, item by item | One ordered unit per cost, each naming the cost it removes (`Mapping:`), never a feature inventory |
| `evidence` | Prove it with real operation data, then concede the boundary | Measured statistics with window and source, plus an explicit non-claim: what the numbers do not prove and what failed |

**Hard rules** — a deck on this path is not deliverable until all hold:

1. **No number without provenance** — measured values cite `Fact IDs` from
   `sources/*.facts.json` or a `Source:` line (origin + measurement window);
   estimates and demo figures say `Data class: scenario`. Never an absolute success
   claim without a denominator ("31 场全中" is the closed example).
2. **The boundary is mandatory** — the evidence page states what failed, why, and
   what the figure does not mean. Omitting it is a content failure, not a style choice.
3. **Every method unit maps to a conflict cost** — a unit that removes no named cost
   is a feature, and features do not belong on the method page.
4. **No visual-only submission** — a deck that carries style without number-backed
   argument is judged unqualified, however good the pages look.

**Read and check**:

- Before the Stage-1 recommendations (Default) or before the roster (Quick), read
  `${SKILL_DIR}/references/dsh-narrative.md` — it owns the per-beat contract, the exact
  §IX / `narrative.md` syntax, the checker codes, the worked example, and the closed
  failure cases.
- Default: after `design_spec.md` exists (Gate 1), run
  `python3 ${SKILL_DIR}/scripts/dsh_narrative_check.py <project_path> --require`.
- Quick: write `narrative.md` before authoring pages, then run the same command
  before export.
- Non-zero → repair the plan artifact (§IX, or `narrative.md`), never the page SVG;
  rerun before continuing. A recorded `off` deck passes as not applicable, with or
  without `--require`.

**Quick `narrative.md`** — an argument contract, not a design spec: the spine line,
then one `## Slide NN — <beat>` block per beat with `Beat`, `Source` / `Fact IDs`,
`Mapping` (method page), `Boundary` (evidence page), and the one-sentence page claim.
No layout, composition, resource plan, or resumable design state.
