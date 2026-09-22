# The Unofficial Guide

richardcodes25 — corpus: `campus_life`

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

The Unofficial Guide answers questions from 88 short `campus_life` posts — dining wait times, housing lottery rules, course hours, pass/fail deadlines, and what a dorm is actually like. You type a plain question; the system retrieves the closest chunks and writes a short answer that names the file it used. It is built for questions with a checkable fact ("how large are Calder singles?", "until which week can I declare pass/fail?"), not for "which dining hall is good." If nothing comes back closer than distance 0.55, it stops and says it doesn't have enough information instead of guessing.

## Chunking Strategy

**Chunk size:** 420 characters (a cap, not a sliding window)
**Overlap:** 40 characters (the post title, repeated on every chunk)

The starter reported 88 documents → 88 chunks, average 317 characters (shortest 178, longest 549). Nothing reached 800, so it never split a post. I first thought one post should stay one chunk. Then I reread the housing and course files: Calder Annexe puts room size, laundry, and noise in separate paragraphs; CS 210 puts weekly hours in one paragraph and "front-loaded" in the next. A whole-post chunk buries the sentence that actually answers the question.

So I split on blank lines instead of character windows. The first short line is the title and gets prepended to every body paragraph, which is the overlap — "90 square feet" still says Calder Annexe. 420 is just above the longest body paragraph I measured (373, the housing-lottery post) plus a ~40-character title, so a complete admin paragraph is not cut mid-sentence. 40 is the title length (titles run 10–47 characters). If a paragraph ever exceeds 420, the chunker cuts on sentence ends and carries 40 characters forward.

Result: 183 chunks, average 167, shortest 63, longest 397. No 2-character tails.

## Sample Chunks

From `python app.py chunks -n 5`.

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_340_exams.txt#1` — produced by: `chunker.py::split_documents`

```
CS 340 Databases — assessment

Start the term project in week three, not week eight; everyone learns this the hard way.
```

**Chunk 3** — source: `course_phys_130_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for PHYS 130 Mechanics

People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time, not optimistic time.
```

**Chunk 4** — source: `dining_verrill_street_grill_followup.txt#1` — produced by: `chunker.py::split_documents`

```
Re: Verrill Street Grill

Also worth saying: one register, so the queue is a single line no matter how busy. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_morrow_house.txt#1` — produced by: `chunker.py::split_documents`

```
Morrow House — what it's actually like

The good: cheapest housing tier by about $900 a year, and the singles are real singles.
```

## Sample Answer

**Question:** How are juniors and seniors ordered in the housing lottery?

**Answer:**

```
  (best distance 0.225, cutoff 0.55)

Juniors and seniors are ordered by accumulated credit hours first, with ties broken randomly in the housing lottery.

Source: admin_housing_lottery.txt

Sources retrieved: admin_housing_lottery.txt, advising_registration.txt, housing_aldridge_hall.txt, housing_calder_annexe.txt, housing_morrow_house.txt
```

Off-topic check, same cutoff: `What is the capital of Mongolia?` returned `I don't have enough information about that.` (best distance 0.787, no model call).

**My relevance cutoff:** 0.55

I kept top-k at 5. The Calder size question puts the sentence with "90 square feet" at rank 2 (distance 0.336); rank 1 is the same file's room-layout paragraph (0.317). k=1 would miss the number. k=5 still brings in other dining-hall follow-ups on the Commons question — those share the word "wait" — so I tightened the grounding instruction to use only the excerpt about the place named in the question.

In-corpus bests were 0.05–0.32. Out-of-scope bests were 0.79–0.92. The gap is 0.32 to 0.79. 0.55 sits in the middle. 0.3 would refuse Calder. 0.9 would answer Mongolia.

| Question | In corpus? | Best distance |
|---|---|---|
| Wait times at Kestrel Commons between 12:15 and 1:00 | yes | 0.236 |
| How juniors and seniors are ordered in the housing lottery | yes | 0.225 |
| Weekly hours outside class for CS 210 | yes | 0.054 |
| Latest week to declare pass/fail after a midterm | yes | 0.254 |
| Size of Calder Annexe singles | yes | 0.317 |
| What is the capital of Mongolia? | no | 0.787 |
| How do I change the oil in a diesel engine? | no | 0.923 |
| Who won the 1994 World Cup? | no | 0.847 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.849 |
| How do I write a for loop in Rust? | no | 0.860 |

## How I Used AI

**1.** I asked Cursor to write a paragraph chunker for `campus_life` and to merge any leftover short paragraph into the next one so titles would not become their own chunks. The first draft treated anything under 50 characters as leftover. That would have glued "Expect 8 to 10 hours a week outside class" (42 characters) onto the next paragraph and buried the number our CS 210 question needs. I listed every short body paragraph first, saw they were complete facts, and changed the rule: only the first short line is a title, and it gets prepended to every body chunk.

**2.** I pasted the five acceptance-criterion sentences and asked: for each one, say exactly how you would test it using only what the sentence says — don't suggest improvements. Criterion 1 failed that test. "Contains the answer" is not defined in the sentence, so two people could score the same run differently. I left the starter wording (the assignment wrote that one) and put the check in the Why: a chunk counts only if it contains that question's `expects` phrase from `questions.py`.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
