# Devpost — Project Details (copy/paste into the form)

## About the project

## Inspiration

Applying for a UK student visa comes down to one narrow, arithmetic-heavy
requirement: prove you've held enough money, for a specific number of consecutive
days, ending within a specific window before you apply. The rule itself is public.
What isn't reliable is the internet's summary of it.

On 11 November 2025, the UK raised the required monthly amounts. We checked six
real, published university guidance pages against the actual current rule. **Two of
the six still quoted the old, lower figures** months later. Someone who trusted
either page would under-save by hundreds of pounds and risk a refusal — for
following advice that used to be correct. Full method and result, reported
honestly: `docs/GUIDANCE_AUDIT.md` in the repo.

That's the reason Dossier exists in this shape: not another chat assistant that
paraphrases visa rules, but something that reads the actual rulebook and refuses to
guess.

## What it does

Dossier interviews you, builds a case for the UK student visa financial requirement,
and tells you the exact date window when you'll qualify — with every number tied to
the paragraph it came from.

The requirement is split across two official documents in a way nobody holds in
their head: Appendix Student sets the amounts (£1,529/month in London, £1,171
outside, capped at nine months) and the 28-day holding period; Appendix Finance sets
the 31-day evidence-recency limit and how the holding period is counted backward
from your statement's closing date. Dossier computes the intersection: *"Your
statement closes 2 Sept. You qualify from 2 Sept — your evidence expires 3 Oct.
Apply in that window."*

One rule collapses the entire requirement: if you've already held UK permission for
12+ months, none of the financial evidence is needed at all. Answer that one
question and the whole checklist visibly re-evaluates to "not applicable," each row
citing the exact reason.

The eligibility decision itself runs as **plain Python, never an LLM call** — a test
in the repo asserts the assessment engine imports nothing from the agent code, so
that's an enforced guarantee, not a claim. Gemini's only job is asking the next best
question and explaining the result in plain language.

A Cloud Scheduler job recomputes every open case nightly as the real date moves
forward and writes a morning briefing, so a case that read "not yet eligible" one
day can read "eligible as of today" the next, without anyone opening the app.

It also reads real documents: upload a photo of a bank statement and Gemini extracts
the account holder, institution, closing balance, and closing date — then shows you
exactly what it read, editable, before any of it becomes a fact the engine relies on.

## How we built it

- **Google Vertex AI** (Gemini 3.5 Flash) drives the interview — the model picks the
  phrasing, but the engine, not the model, picks which unresolved requirement to ask
  about next, ranked by how much answering it would prune.
- **A committed `RequirementGraph`** — every node (`ST 12.1`, `ST 12.3`, `ST 12.6`,
  `FIN 7.1`, `FIN 7.2`, ...) carries its citation, source URL, and verbatim rule
  text, extracted from the real gov.uk pages and manually reviewed against them
  before being trusted — see `docs/RULEBOOK_REVIEW.md`.
- **A pure-Python gap engine** handles all date arithmetic and the ST 12.1 exemption
  pruning, with zero network calls and zero LLM calls, so it's fully unit-testable
  and fast.
- **Cloud Run + Firestore** host the two-screen console and persist case state.
- **Cloud Scheduler** fires the nightly recheck.
- A budget alert is live on the project from day one; the deterministic engine and
  full test suite also run entirely free, locally, with no cloud dependency at all.

## Challenges we ran into

- **Two rule documents, one interaction, and no summary source gets it right.**
  Appendix Student sets the amounts and the 28-day rule; Appendix Finance sets the
  31-day recency limit and the counting method. Getting the boundary cases right —
  day 27 vs 28 vs 29, day 30 vs 31 vs 32 — needed real gov.uk-published worked
  examples as test fixtures, not assumptions.
- **We built more than we finished wiring up in one part of the system, and we're
  saying so rather than quietly overclaiming it.** The notebook data model supports
  a third note kind — `inference`, a value the system derives rather than one the
  user confirms — with a correction path designed for it. The live console doesn't
  create or surface these notes yet; user-confirmed facts and a question-style
  preference are wired in today, and editing each one has a genuinely different,
  tested effect (a fact re-runs the whole assessment, a preference changes only
  phrasing). That's a real, scoped next step, not vaporware — see "What's next" in
  the README. The multimodal document reading, by contrast, is fully wired: upload
  a bank-statement image and Gemini's extraction genuinely populates an editable
  confirmation screen before anything is trusted.
- **Finding the actual discovery took manual, tedious checking** — six real
  university pages, checked by hand against the current rule, not scraped or
  automated. Slower, but it's the only way to be sure the result is real.

## Accomplishments that we're proud of

- A real, checkable discovery: two of six real public guidance pages we checked
  quoted outdated figures — reported honestly, without naming an institution before
  giving it a chance to correct it.
- An eligibility engine whose independence from the LLM is enforced by a test, not
  just described in a README.
- A genuinely async product: a case's status can change overnight, unattended, which
  is rare for anything in the "helps you fill out a form" category.

## What we learned

That the most defensible engineering decision here was also the simplest one:
**never let the model decide what the law requires.** Every ambiguous case — what
counts as "held," how the 28 and 31-day windows interact, whether ST 12.1 applies —
gets resolved by code that can be tested against the government's own text, not by
asking a model to reason it out fresh each time.

## What's next for Dossier

Surface `inference` notes in the UI with a real per-note correction control,
matching what facts and preferences already do. Widen the guidance audit past six
pages, and extend the rule graph to the student-loan and official-sponsorship
routes it currently excludes.

---

## Built With

```
python
google-gemini
google-vertex-ai
google-cloud-run
google-cloud-firestore
google-cloud-scheduler
fastapi
pytest
```

## Try it out links

```
Live demo:   https://dossier-console-qupwgyb5aq-uc.a.run.app
GitHub repo: https://github.com/AshrafAhmed9/dossier-uk-student-visa
```

## Video demo link

Paste the uploaded YouTube/Vimeo URL once it's live (Public or Unlisted, not
Private).

## Image gallery — what to upload (3:2 ratio, up to 15)

1. `docs/thumbnail.png`
2. `docs/architecture.png`
3. A screenshot of the live Dossier screen showing the apply-date window and cited
   requirement table
4. A screenshot of `docs/GUIDANCE_AUDIT.md` rendered on GitHub (the finding)
5. A screenshot of the Cloud Scheduler job showing `ENABLED` and a recent last-run
   timestamp
