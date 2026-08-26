# Dossier — Demo Video Script (Collaborative Partner track)

**Target runtime: 3:40** (hackathon cap: 4:00 max — hard limit). Upload: YouTube or
Vimeo, **Public or Unlisted**. Everything below points at the real deployed system at
https://dossier-console-qupwgyb5aq-uc.a.run.app — record as one continuous take with
live execution and the Google Cloud Console visible, per the hackathon's submission
requirement.

**Format key:** `SAY` = spoken, natural, not stiff. `SHOW` = exactly what's on screen.
`CAPTION` = on-screen text overlay for the full duration listed — no silent,
uncaptioned stretch anywhere in the video.

---

## 0:00–0:15 — Hook

**SAY:**
> "If you've ever applied for a visa, you know the actual danger isn't the paperwork
> — it's that the rule everyone quotes online is wrong, and you don't find out until
> you're refused."

**SHOW:** Plain title card — "DOSSIER" — or your face. No UI yet.

**CAPTION (0:00–0:15):** `The rule everyone quotes online might be wrong. You find out when you're refused.`

---

## 0:15–0:45 — The real finding, stated plainly

**SAY:**
> "On November 11th, 2025, the UK raised the amount of money a student visa applicant
> has to prove they hold — from about £1,334 a month to £1,529. We checked how many
> public guidance pages actually caught up. Out of six university pages we checked,
> two were still quoting the old, lower number months later. Anyone who trusted those
> pages would under-save by hundreds of pounds and risk a refusal — for following
> advice that used to be correct."

**SHOW:** `docs/GUIDANCE_AUDIT.md` on screen, scrolled to the "Result" section —
"Four pages reflected the current... Two older PDFs displayed previous... figures."

**CAPTION (0:15–0:30):** `Nov 2025: the required amount went up. Not every guide caught up.`
**CAPTION (0:30–0:45):** `2 of 6 pages we checked still showed the old, lower figure.`

---

## 0:45–1:15 — The one sentence and the one clever idea

**SAY:**
> "So Dossier doesn't summarize the internet's summary of the rules. It reads the
> actual UK government rulebook, builds your case with you, and tells you the exact
> date window when you'll qualify. And here's the part that matters: the AI never
> decides whether you meet a legal requirement. That decision runs as plain code,
> against a rule graph where every single number is tied to the exact paragraph it
> came from. The AI only interviews you and explains — it can't invent a rule."

**SHOW:** Briefly open `rulebook/requirements.json` or the rendered rule graph in the
console, showing a node with its `citation` field (e.g. `"ST 12.6"`) visible on
screen for a beat.

**CAPTION (0:45–1:00):** `It reads the actual gov.uk rulebook — not a summary of it.`
**CAPTION (1:00–1:15):** `An LLM never decides if a rule is met. That's plain code. Every number cites its paragraph.`

---

## 1:15–2:05 — Live walkthrough: the Interview and the Notebook

**SAY:**
> "Here's the live app. It asks one question at a time — but not in a fixed order.
> It picks whichever question narrows things down the most. And everything I tell it
> shows up here, in the Notebook — this is it literally taking notes on me."

**SHOW:** Live on `https://dossier-console-qupwgyb5aq-uc.a.run.app` — the Interview
screen. Answer 2–3 real questions on camera (e.g. course location, months already in
the UK, course fee). Point at the Notebook sidebar updating with a new fact after each
answer.

**SAY** (continuing, once you answer the "months already in the UK" question with a
value that triggers the exemption):
> "Watch this — I just told it I've already been in the UK over 12 months. Under the
> actual rule, that waives the entire financial requirement. Watch the checklist
> collapse."

**SHOW:** The moment the exemption fires and dependent questions/requirements
disappear from the Notebook or Dossier view — this is the single most important shot
in the video, let it breathe, don't rush past it.

**CAPTION (1:15–1:35):** `One question at a time — picked by how much it narrows down, not a fixed form.`
**CAPTION (1:35–1:50):** `Every answer becomes a note, visible, with a source.`
**CAPTION (1:50–2:05):** `One answer just waived the entire requirement. Watch the checklist collapse.`

---

## 2:05–2:30 — Correcting it, and watching it actually adapt

**SAY:**
> "And if it gets something wrong — say it inferred my course is in London when it
> isn't — I correct it right here. That's not just fixing a text field. It re-runs the
> whole assessment, and it changes what it asks me next."

**SHOW:** Open a note marked as an `inference`, use its correction control, and show
(a) the Dossier's computed amount/window changing, and (b) the next interview question
being visibly different than it would have been.

**CAPTION (2:05–2:20):** `Correcting an inference re-runs the entire assessment.`
**CAPTION (2:20–2:30):** `It changes the next question too — not just the record.`

---

## 2:30–2:55 — The multimodal moment

**SAY:**
> "It also reads your actual documents. Here's a bank statement — Dossier reads the
> closing balance and the date range straight off the image, then shows me exactly
> what it read before it trusts any of it."

**SHOW:** Upload a sample bank statement image via the extractor, show the extracted
fields (holder, balance, date range) rendered back for confirmation before they're
used.

**CAPTION (2:30–2:45):** `Reads a photo of a bank statement — extracts the numbers that matter.`
**CAPTION (2:45–2:55):** `Always shows you what it read before it trusts it.`

---

## 2:55–3:20 — Proof it runs unattended, on Google Cloud

**SAY:**
> "And this doesn't just run while I'm looking at it. Every night, a Cloud Scheduler
> job on Google Cloud re-checks every open case as the real date moves forward, and
> writes a morning briefing — nobody has to come back and press anything."

**SHOW, live in the Google Cloud Console:**
1. Cloud Run service page for the Dossier console — confirm it's actually deployed.
2. Cloud Scheduler job for the nightly recheck — show its schedule and **last
   execution timestamp**, ideally from the previous night, unattended.
3. Firestore, the case documents — show a stored morning briefing with a real
   timestamp from a night nobody manually triggered.

**CAPTION (2:55–3:10):** `Cloud Run · Firestore · Cloud Scheduler — recomputes every case, every night.`
**CAPTION (3:10–3:20):** `Last unattended run: [read the real timestamp on screen].`

---

## 3:20–3:35 — Close

**SAY:**
> "Dossier: it leads the interview, takes real notes, adapts when you correct it, and
> tells you the truth the internet's summary might have missed."

**SHOW:** Back to the Dossier screen — the final assessment with citations visible.

**CAPTION (3:20–3:35):** `Leads the interview. Takes real notes. Tells you the truth a summary might have missed.`

---

## Recording checklist

- [ ] Confirm the live URL responds and the shared demo case is in a clean, presentable
      state before recording — reset/reseed it if a prior take left it mid-edit.
- [ ] Do **not** enter any real personal data on the live demo (per the README's own
      warning) — use clearly fictional numbers throughout the recording.
- [ ] Confirm Cloud Scheduler's last execution timestamp is genuinely recent before
      claiming "unattended" on camera — if it hasn't fired recently, say so honestly
      rather than implying a fresh unattended run.
- [ ] Confirm the exemption-triggering answer (1:50–2:05) actually produces a visible
      change in a dry run before filming — this is the single most important shot,
      rehearse it once off-camera first.
- [ ] One continuous take if possible; a single clean cut between labeled sections is
      fine — no jump-cut editing within a section.
- [ ] Upload to YouTube/Vimeo as Public or Unlisted (not Private).
- [ ] Confirm final runtime is under 4:00.
