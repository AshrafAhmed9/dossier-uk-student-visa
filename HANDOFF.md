# HANDOFF FOR CODEX — build Dossier from scratch

Everything below is what a fresh agent needs to execute without re-deriving context.
This is a **new, empty repo** — greenfield build, not an extension of anything.

## 0. Orientation

**Repo:** `/Users/ashraf/Desktop/PROJECTS/All Things Agentic Hackathon/dossier-visa-copilot`
(git initialized, empty, its own repo nested inside the hackathon folder — NOT a
submodule, just a plain sibling `.git`. The parent folder's own git (Crucible) will not
track this directory's contents; that's intentional.)

**Sibling project in the parent folder (reference only, do not modify):**
`/Users/ashraf/Desktop/PROJECTS/All Things Agentic Hackathon/` (the parent of this repo)
— Crucible, a separate hackathon submission by the same author, for a different track.
It has an uncommitted work-in-progress from a concurrent Codex session — **do not touch
any file outside this `dossier-visa-copilot/` directory.** You may *read*
`../agents/shared/vertex.py` there as a porting reference (see Section 2).

Both submissions living in one parent folder is deliberate — same author, same
hackathon, two entries, easy for Ashraf to find both. Never let this repo's git commands
(`git add`, `git commit`, etc.) touch anything outside `dossier-visa-copilot/`.

**What this is:** Dossier — an agent that builds a UK student visa financial-requirement
case with the user over several days: interviews them, reads uploaded documents
(multimodal), and tells them the exact date window when they'll qualify to apply. A
deterministic, paragraph-cited rules engine (not the LLM) decides eligibility. A nightly
job re-checks the case as dates roll forward and produces a morning briefing — this is
the autonomy/async proof for the hackathon's theme.

**Hackathon:** "All Things Agentic," Google-sponsored, deadline 2026-08-31 5pm PDT.
Today: 2026-08-24. This is submission #2, for the **Collaborative Partner** track
($20k pool). Track brief (verbatim): *"Build an agent that leads the way and takes
notes. It should ask clarifying questions, guide the user step-by-step, and have a
clear way to capture feedback, so it constantly adapts to the user's unique way of
thinking."*

**Required tech stack (verified from official rules):** Gemini 3.5+ via Vertex AI, AND
at least one Google Agent Framework (we use the GenAI SDK, same as Crucible — this
satisfies it), AND at least one Google Cloud infrastructure service.

**Status: nothing built yet. This is the first build session.**

## 1. The one sentence and the one clever idea — do not lose these while building

> **It builds your UK student visa application from the actual immigration rules — not
> the outdated summaries — and tells you the exact date window when you'll qualify.**

> An LLM must never decide what the law requires. Requirements are extracted once from
> the real published rulebook into a deterministic, versioned, paragraph-cited
> `RequirementGraph`. Eligibility and all date arithmetic run as **plain Python** over
> that graph. Gemini interviews the user, reads their documents, and explains — **it
> never adjudicates whether a rule is met.** Every number Dossier shows traces to a
> paragraph the user can click.

This is the single most important architectural rule in this build: **no LLM call may
ever sit in the path that decides whether a requirement is satisfied.** If you are
tempted to have Gemini "just check if this looks right," stop — that decision belongs
in `engine/gaps.py`, in plain Python, full stop.

## 2. Environment

```bash
cd "/Users/ashraf/Desktop/PROJECTS/All Things Agentic Hackathon/dossier-visa-copilot"
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
```

Auth is already done globally (`gcloud auth application-default login` was run for the
sibling project and should still be valid). You will need a **separate GCP project**
from Crucible's `second-unit-505818` — do not deploy into that project. Create a new
GCP project under the same Free Trial account (never upgrade to paid billing — see
Section 6). Pick a project ID, e.g. `dossier-visa-copilot`, and use it consistently.

**Port `agents/shared/vertex.py` from the parent repo as a starting point** —
`../agents/shared/vertex.py` (i.e.
`/Users/ashraf/Desktop/PROJECTS/All Things Agentic Hackathon/agents/shared/vertex.py`).
Read it, then write a fresh copy here adapted to this project's ID. It already solves
three non-obvious problems, keep them:
- Vertex serves current Gemini models **only from `location="global"`** — regional
  endpoints (`us-central1`) 404 even though the model appears in the regional catalog.
  This cost a full debugging session on Crucible. Do not "fix" it back to a region.
- `call_with_retry()` — exponential backoff on 5xx/429, but raises immediately (no
  retry) on a per-day quota error since waiting won't help same-day.
- Model split: `gemini-3.5-flash` for high-volume interview turns, a Pro model for
  extraction/briefings (low volume, higher reasoning quality).

**Model names to use:** `gemini-3.5-flash` and `gemini-3.1-pro-preview` (same as
Crucible — verified working via Vertex on 2026-08).

## 3. Non-negotiable rules

- **R1 — No LLM in the adjudication path.** `engine/gaps.py` must not import anything
  from `agents/`. Write a test that asserts this via static import inspection. This is
  the project's central claim; a change that lets the model decide eligibility
  destroys it.
- **R2 — Every requirement node is paragraph-cited.** `citation` (e.g. `"ST 12.6"`),
  `source_url`, `retrieved_at`, and verbatim rule text, on every node in the
  `RequirementGraph`. No node without a citation.
- **R3 — Never fabricate results.** If the guidance audit (Section 8) finds nothing
  wrong, report that honestly. If a test scenario doesn't reproduce a published
  worked example, say so and fix the engine — don't adjust the test to pass.
- **R4 — Never give legal advice.** Every screen states this is evidence assembly and
  gap-checking, not legal advice. Every requirement shown links to its official gov.uk
  source. Nothing is ever auto-submitted anywhere — this is a read-only advisory tool.
- **R5 — The rulebook graph is a reviewed artifact, not raw model output.** LLM-assisted
  extraction is fine for a first pass, but the committed `RequirementGraph` must be
  something a human (Ashraf) reviewed line-by-line against the actual gov.uk pages
  before it's trusted. Flag this clearly when the extraction step is done so it doesn't
  get silently skipped.
- **R6 — Match Crucible's engineering style**: module docstrings explaining *why*,
  dataclasses for structured data, no new heavy frameworks, no new deps beyond what's
  needed (`fastapi`, `google-genai`, `google-cloud-firestore`, `pytest` — same as the
  sibling project).

## 4. Scope — locked. This is the highest-leverage thing in this document.

**Build only the financial-requirement piece of the UK Student visa route.** Not the
whole visa, not other routes, not other countries. It's the leading cause of refusal,
it's arithmetic-heavy so the deterministic engine visibly earns its place, and it fits
a 4-minute demo video.

**Explicitly out of scope — do not build these even if they seem easy:**
- OpenTelemetry / Cloud Trace (that served Crucible's track brief, not this one)
- Live rulebook diff-monitoring / re-fetch-and-alert (can't be honestly demoed in days
  since the rules won't change during the build — the guidance audit in Section 8
  delivers the same "we watch for drift" idea with real evidence instead)
- Multiple visa routes or countries — pitch it as one instance of a general engine,
  don't generalize the code
- Auth, multi-tenancy, payments, real form submission to any government system
- PDF generation — clean printable HTML is sufficient for "the Dossier" artifact
- More than two console screens (Interview screen, Dossier screen)

If you find yourself building something not in the "Components" list below, stop and
check it against this section first.

## 5. The rulebook — the two source documents

These are real, public, UK government pages. Fetch and re-verify exact current text
before extracting (rules can be amended; work from the live page, not from this doc):

- `https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-finance`
- `https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-student`

Known paragraph references as of 2026-08-24 (re-verify, do not trust blindly):
- **ST 12.3** — maintenance amounts: £1,529/month inside London, £1,171/month outside,
  up to 9 months, plus any outstanding course fees per the CAS (Confirmation of
  Acceptance for Studies)
- **ST 12.6** — funds must be held for a **consecutive 28-day period**
- **ST 12.1** — if the applicant has held permission to be in the UK for **12+ months**
  at the date of application, the entire financial requirement is waived
- **FIN 7.1** — the most recent financial evidence must be dated within **31 days**
  before the date of application
- **FIN 7.2** — the 28-day period is calculated by **counting back from the closing
  balance date** on the most recent evidence

**The finding this project is built around:** on 11 November 2025 these maintenance
amounts increased from £1,334/£1,023 to the current £1,529/£1,171. Some published
third-party guidance (university pages, agent/adviser sites) still shows the old,
lower, pre-November-2025 figures — meaning an applicant following that guidance would
under-save and risk refusal. This is real and checkable, not invented; it's what makes
this project's premise ("the internet's summary of the rules is wrong, read the actual
rules") concretely true rather than just clever-sounding. See Section 8.

## 6. Architecture

```
gov.uk Appendix Student + Appendix Finance   (real, third-party, public)
        │
        ▼
  RULEBOOK INGEST ──► RequirementGraph  (committed, human-reviewed, every node cited)
                             │
                             ▼
   ┌────────── GAP ENGINE (pure Python — the core claim) ──────────┐
   │  satisfied / unsatisfied / blocked-until-DATE  + apply window  │
   └────────────────────────┬──────────────────────────────────────┘
              ▲             │ unresolved nodes, ranked by how much they prune
              │             ▼
        CASE FACTS ◄─── INTERVIEWER (Gemini) ──► asks the next best question
              ▲             │
              │             ▼
   EVIDENCE EXTRACTOR   NOTEBOOK  ← the literal "takes notes" the track brief asks for
   (multimodal: photo      │  facts · inferences · preferences, each with
    of bank statement)     │  provenance and a "that's wrong" correction control
                           ▼
                  NIGHTLY CASEWORKER (Cloud Scheduler)
                  rolls dates, recomputes the window, writes a briefing
                           │
                           ▼
                    THE DOSSIER  ← the visible artifact judges see
```

### Components to build, in this order

1. **`rulebook/ingest.py`** — fetch both gov.uk pages, extract requirement nodes into a
   `RequirementGraph` (dataclass-based: `id`, `citation`, `source_url`, `retrieved_at`,
   `rule_text`, `depends_on: list[str]`, `kind` — e.g. `amount`, `duration`,
   `recency`, `exemption`). LLM-assisted extraction is fine, but **serialize the result
   to a committed JSON/Python file and flag it for human review** (R5) rather than
   re-extracting live on every run.

2. **`engine/gaps.py`** — pure Python, **zero imports from `agents/`, zero network
   calls**. Input: graph + a `CaseFacts` object (bank balance, closing date, course
   location, months in UK, course fee, etc). Output: per-node status
   (`satisfied` / `unsatisfied` / `blocked_until: date`) and the computed apply-date
   window (earliest date the 28-day holding period is satisfied AND still within 31
   days of application). Handle the ST 12.1 exemption by pruning the entire
   ST 12.3/12.6/FIN-7.x subtree when `months_in_uk >= 12`.

3. **Unit tests for the engine, before anything else touches it.** Cover: London vs
   non-London amounts, the 28-day boundary (27/28/29 days), the 31-day recency
   boundary (30/31/32 days), the ST 12.1 exemption pruning, and at least 3–5 worked
   examples pulled from real third-party university guidance pages (search for
   "[university name] student visa 28 day rule example" — several UK universities
   publish worked date examples; use them as ground truth the way Crucible used
   Firestore data as ground truth, not LLM opinion).

4. **`agents/interviewer.py`** — Gemini picks the phrasing of the next question; **the
   engine picks which unresolved graph node to ask about**, ranked by how many
   descendant nodes resolving it would prune (i.e. ask the highest-information
   question first — this is what makes it "lead the way" rather than a static form).

5. **`agents/notebook.py`** — the user model. Three note kinds: `fact` (stated by
   user), `inference` (derived, with a `derived_from` pointer), `preference` (how they
   like being asked things). Each note has a correction control. **Correcting an
   inference must re-run the gap engine; correcting a preference must change how the
   next interview question is phrased** — both effects need to be visibly different in
   the UI, not just a silent data update. This is the track's literal "capture
   feedback so it constantly adapts" requirement — it must be demonstrable, not just
   claimed in the README.

6. **`agents/extractor.py`** — multimodal. Take a photo/scan of a bank statement or CAS
   letter, extract structured fields (account holder name, institution, closing
   balance, statement date range) via Gemini's vision input. Always render what it
   extracted back to the user for confirmation before feeding it into `CaseFacts` —
   never silently trust OCR-style extraction.

7. **`jobs/nightly.py`** + Cloud Scheduler — re-run the gap engine for every open case
   as the current date advances, write a morning briefing (`CaseFacts` + graph state →
   short human-readable summary of what changed and what's now true that wasn't
   yesterday). This is the autonomy proof — **stand this up on day 1** even as a
   near-empty stub that just re-runs the engine against one seeded case, so genuine
   history accumulates every day of the build rather than being backfilled later
   (backfilling would be dishonest — see R3).

8. **`console/main.py`** — FastAPI on Cloud Run, two screens only: Interview (with the
   Notebook visible in a sidebar) and the Dossier itself. Design the Dossier as a
   document a person would actually hand to a visa adviser — clear sections, citations
   as clickable links, the apply-date window prominent — not a debug/log view.

### The one seeded demo case — set this up on day 1

Seed a single persona case (e.g. a student whose bank statement closing balance is
currently *below* the required amount, but will cross it partway through the build
week if the numbers are set up right) such that **the apply-date window opens for real,
sometime between now and 2026-08-30, driven only by the nightly job re-running against
the real current date** — not by manually editing the case. The demo/video moment is:
day 1, Dossier says "you don't qualify yet, earliest date is X." Later in the week, the
scheduled job fires unattended and the morning briefing flips to "you qualify as of
today." That transition, happening on its own, is the single most important thing to
capture on video — plan the seeded numbers so it happens before demo day, with margin.

## 7. Google Cloud surface

Vertex AI (Gemini 3.5 Flash for interview turns + extraction, Pro for briefings),
Cloud Run (the console), Firestore (case facts, notebook, graph, briefings — same
access pattern as Crucible's `curator.py`, reference it), Cloud Scheduler (the nightly
job). `min-instances=0` everywhere. This satisfies "at least one Google Cloud
infrastructure service" many times over.

## 8. The guidance audit (do this — it's the project's differentiator)

**~4 hours.** Collect ~15–20 published UK student-visa guidance pages (university
international-office pages, visa-agent blogs, adviser sites — search "UK student visa
28 day rule maintenance funds"). Check each page's stated maintenance figures against
the committed `RequirementGraph` (i.e. against ST 12.3's real current £1,529/£1,171).

Rules for this, mirroring the sibling project's disclosure discipline:
- **Beware false positives.** A page based in/for London that states only the £1,529
  figure with no non-London mention is a legitimate simplification for its own
  audience, **not an error** — only flag pages that state a maintenance figure
  inconsistent with current ST 12.3 amounts (most commonly, pre-11-November-2025
  figures of £1,334/£1,023).
- **Notify before publishing anything.** If a genuinely outdated page is found, draft
  (do not send without Ashraf's approval) a short, factual email to the page's owner
  citing the specific paragraph and the correct current figure — helpful, not
  adversarial.
- **Do not name-and-shame publicly.** Report the aggregate pattern (e.g. "X of 18 pages
  checked showed pre-November-2025 figures") in the README/writeup; only name a
  specific institution if it was notified first and given time to respond, and even
  then only with Ashraf's explicit sign-off — same disclosure discipline as the
  sibling project's Bug Hunters report.
- **A null result is a fine result.** If every page checked turns out current, write
  that up honestly (R3) — do not manufacture a finding.
- The audit corpus doubles as the engine's third-party validation set (Section 6,
  step 3) — worked date examples from these same pages become test fixtures.

## 9. Cost discipline — same structural guarantee as Crucible

- **Free Trial GCP project, never manually upgraded to paid billing** — this alone
  makes overspend structurally impossible (Google auto-closes Free Trial billing on
  credit exhaustion/90 days; it does not silently start charging).
- Set a budget alert (e.g. ₹800/mo or equivalent) as soon as the project exists.
- Reference (read-only) `/Users/ashraf/Desktop/PROJECTS/All Things Agentic
  Hackathon/infra/kill-switch/` and `../infra/terraform/` in the parent repo as a
  pattern for a billing-detach Cloud Function and Terraform layout — port, don't copy
  blindly, since project IDs differ.
- `min-instances=0` on every Cloud Run service. No always-on resources.

## 10. Build order

| Day | Work |
|---|---|
| **1 (Aug 24)** | New GCP project + budget alert first, before any code. Port `vertex.py`. Ingest both appendices → `RequirementGraph` (flag for Ashraf's review). Stand up `jobs/nightly.py` even as a near-stub against one seeded case — history must start accruing today. |
| **2** | `engine/gaps.py` + full test suite against real worked examples. Run the guidance audit (Section 8); draft any notification emails for Ashraf's approval, don't send them yourself. |
| **3** | Interviewer + Notebook, including the correction→re-run and correction→re-phrase behaviors. |
| **4** | Multimodal extractor. Console (two screens). Design the Dossier as a real document. |
| **5** | Deploy to Cloud Run. README (quickstart, architecture diagram, citations, legal-advice disclaimer, cost notes) + architecture diagram matching the ASCII one in Section 6. |
| **6** | Reserved for Ashraf to film video and handle submission — not a Codex task. |

## 11. Verification before hand-back

```bash
pytest tests/ -v          # engine tests must all pass, including boundary cases
python3 -c "import ast, pathlib; ..."   # or an equivalent static check that engine/ imports nothing from agents/
python3 -m jobs.nightly    # or equivalent manual trigger, confirm it recomputes correctly
gcloud run deploy dossier-console --project=<your-new-project-id> --source=. --region=us-central1 --quiet
curl -s <live-url>/       # confirm it's up
```
Confirm the Cloud Scheduler job shows `ENABLED` and has genuinely fired at least once
unattended (check Firestore/logs for a timestamp nobody manually triggered).

**Commit style:** explain *why*, note honest caveats (e.g. "guidance audit found N of M
pages current" — whatever the real number is). Small, frequent commits over one giant
one — this makes it easy for Ashraf to review what happened.

**Out of scope for Codex:** the demo video and Devpost submission — Ashraf handles both,
after this build is deployed and verified.

## 12. If something in this doc turns out wrong

The paragraph numbers and figures in Section 5 were verified against the live gov.uk
pages on 2026-08-24 but immigration rules can be amended. If the live page text
disagrees with anything cited here, **the live gov.uk page is authoritative** — update
the `RequirementGraph` and note the discrepancy in a commit message, don't silently
follow this document over the real source.
