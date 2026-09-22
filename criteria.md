# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
I will count a retrieved chunk as containing the answer only if it includes
that question's `expects` phrase from `questions.py`. One of the five asks
how large Calder Annexe singles are — that number lives in one sentence in
one file, while other Calder posts talk about laundry and noise instead. 4
of 5 leaves room for that miss. 5 of 5 would pretend a one-file fact is as
easy as Commons wait times, which two documents repeat. 3 of 5 would pass
even if retrieval regularly returned the wrong dining hall or dorm.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
All five, not four. The prompt already hands the model each chunk labeled
with its filename and tells it to name the file. On these five in-corpus
questions the gate should pass, so a missing source is the model ignoring
that instruction, not a close call. 4 of 5 would let that slide. A refusal
on an in-corpus question does not count as "an answer the system produces"
for this check — that miss belongs to criterion 1 or 3.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

**Why this target:**
Measured in Milestone 4: the five in-corpus questions had best distances
0.05–0.32; the five `OUT_OF_SCOPE` questions (Mongolia, diesel oil, the
1994 World Cup, ibuprofen, Rust) had best distances 0.79–0.92. I put the
cutoff at 0.55, in that gap. 4 of 5 allows one weird nearest-neighbor if
an out-of-scope question later lands closer. 5 of 5 would treat a single
embedding accident as a failed cutoff. 3 of 5 would accept a gate that
barely works.

---

## 4. Chunks keep a topic and its fact together

When I print 5 chunks with `python app.py chunks -n 5`, at least 4 of them
include both a topic name (a building, course, dining hall, or admin rule)
and a concrete fact (a price, a time, a number, or a named deadline) in the
same chunk, and no sentence is cut at either end.

**Why this target:**
The campus_life posts I read are 1–3 short paragraphs, about 317 characters
on average. The useful sentence is the one with the number — "$2.00 wash",
"week eight", "90 square feet" — and it only helps if the building or course
name is still in the same chunk. 4 of 5, not 5 of 5, because a sampled
chunk could be a short aside (a follow-up that only repeats a wait time).
3 of 5 would pass a chunker that splits "Calder Annexe" off from "90 square
feet", which is the failure this criterion is for.

---

## 5. The answer contains the expected phrase and cites a file that has it

For at least 4 of my 5 test questions, the answer contains that question's
`expects` phrase from `questions.py`, and it names a source filename whose
document text also contains that phrase.

**Why this target:**
Criterion 2 only checks that *a* source was named. I care that the named
file actually holds the fact. Laundry prices in this corpus look alike
across halls; a system could say "90 square feet" and cite a Calder laundry
post that never mentions room size. 4 of 5 matches criterion 1: the Calder
size question is the one I expect to miss. 5 of 5 would ignore that. 3 of 5
would pass a system that regularly cites the wrong file.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
