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

**3.** This unit I had Cursor score the three-run log against those targets, including the close calls. It pointed out that every written criterion was 5/5 while Calder's "90 square feet" sentence was rank 2, behind the layout paragraph. I checked that against the chunk text before I used it as the diagnosis.

**4.** Before changing search, I asked why BM25 might fail to fix that swap. Equal-weight fusion ties when the two systems exchange rank 1 and 2, and the tie keeps the semantic order. I set the keyword weight to 1.5 from that, then confirmed with `store.py::search` that the size sentence came back first and the other four questions still had their phrase at rank 1.

## Stretch features (claimed before building)

Two extras, both for the CLI. Not doing a second embedding model — that install pulls PyTorch.

**Metadata filtering.** `campus_life` has no dates, so the filter is by source file or topic (`dining`, `housing`, `course`, `admin`, … — the first word of the filename). `--topic dining` or `--source admin_housing_lottery.txt` on `ask` and `retrieve`.

**Conversational memory.** `python app.py ask` with no question keeps the last question. A follow-up like "what about laundry?" is rewritten against that last question before retrieval.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

`python run_eval.py --label before` on 2026-10-03, cache off. Raw file: `results/run_2026-10-03_1900_before.md`, produced by `run_eval.py::main`. That session made 15 model calls. The three answers for a question are not the same text — CS 210's source line is "(or …)", then "(and …)", then "(also found in …)" — so this is three generations. The counts still match across runs because retrieval, the gate, and chunking do not call the model, and every generated answer still contained the `expects` phrase and a filename.

A chunk counts for criterion 1 only if its text contains that question's `expects` phrase. Criterion 4 is `python app.py chunks -n 5`, which walks a fixed stride through `chunker.py::split_documents`, so one print is the measurement and the same count goes in all three columns. Criterion 3 is the same kind of measurement: `run_eval.py::check_out_of_scope` runs once.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunk keeps a topic and its fact together | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Answer has the expected phrase and cites a file that has it | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

### Criterion 1 — retrieved chunk contains the `expects` phrase

Produced by `store.py::search` (chunks from `chunker.py::split_documents`). Distances match run 1 in the results file. The chunk that contains the phrase is quoted; the other retrieved chunks for that question do not, except where noted.

Kestrel Commons, expects `20 to 25`, best distance 0.2359, rank 1, `dining_kestrel_commons_followup.txt`:

```
Re: Kestrel Commons

Adding to what people have said about Kestrel Commons. The wait figure of 20 to 25 minutes between 12:15 and 1:00 matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.
```

Housing lottery, expects `credit hours`, best distance 0.2250, rank 1, `admin_housing_lottery.txt`:

```
On the housing lottery

The housing lottery is not random in the way most people assume. Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly. That means a senior who took summer courses reliably beats a senior who didn't. Numbers come out the second week of March and selection runs over four evenings.
```

Rank 4, `advising_registration.txt`, also contains the phrase, in a sentence about registration times, not the lottery order.

CS 210, expects `8 to 10`, best distance 0.0541, ranks 1 and 2, `course_cs_210.txt` and `course_cs_210_workload.txt`:

```
CS 210 Data Structures

Expect 8 to 10 hours a week outside class.
```

Pass/fail, expects `week eight`, best distance 0.2545, rank 1, `admin_pass_fail_option.txt`:

```
On the pass/fail option

Any course outside your major can be taken pass/fail, and — the part nobody mentions — you can declare it as late as week eight, after you've seen your midterm. A pass needs a C- or better. Two per year, maximum eight across a degree.
```

Calder singles, expects `90 square feet`, best distance 0.3171. Rank 1 is the room-layout paragraph and does not contain the phrase. Rank 2 (distance 0.3362), same file `housing_calder_annexe.txt`, does:

```
Calder Annexe — what it's actually like

The bad: the singles are small — about 90 square feet — and the desks are fixed.
```

5 of 5 on every run. Target was 4 of 5.

### Criterion 2 — every answer names a source

Produced by `generate.py::answer_from_chunks`. Run 1 of each question, from `results/run_2026-10-03_1900_before.md`. Runs 2 and 3 also name a filename; none of the fifteen answers is a refusal.

```
Students state that the wait figure at Kestrel Commons between 12:15 and 1:00 is 20 to 25 minutes. 

Source: dining_kestrel_commons_followup.txt
```

```
In the housing lottery, juniors and seniors are ordered by accumulated credit hours first, with any ties broken randomly. 

Source: admin_housing_lottery.txt
```

```
CS 210 Data Structures takes 8 to 10 hours a week outside class. 

Source: course_cs_210.txt (or course_cs_210_workload.txt)
```

```
A student can declare the pass/fail option as late as week eight, after seeing their midterm (admin_pass_fail_option.txt).
```

```
The singles at Calder Annexe are small, measuring about 90 square feet (housing_calder_annexe.txt).
```

5 of 5 on every run. Target was 5 of 5.

### Criterion 3 — the gate stops out-of-corpus questions

Produced by `run_eval.py::check_out_of_scope`, cutoff 0.55. One pass. The same 5/5 is written in all three run columns.

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.787 | refused |
| How do I change the oil in a diesel engine? | 0.923 | refused |
| Who won the 1994 World Cup? | 0.847 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.849 | refused |
| How do I write a for loop in Rust? | 0.860 | refused |

Refused 5 of 5. Target was 4 of 5.

### Criterion 4 — a chunk keeps a topic and its fact together

Produced by `chunker.py::split_documents`, printed by `app.py::cmd_chunks` (`python app.py chunks -n 5`). 183 chunks, stride sample of 5. Each one names a topic and a number or deadline, and each sentence ends inside the chunk.

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

Topic: add/drop deadline. Facts: second week, week six, week two.

```
CS 340 Databases — assessment

Start the term project in week three, not week eight; everyone learns this the hard way.
```

Topic: CS 340. Facts: week three, week eight.

```
Workload for PHYS 130 Mechanics

People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time, not optimistic time.
```

Topic: PHYS 130. Facts: 7 hours, 3 on lab weeks.

```
Re: Verrill Street Grill

Also worth saying: one register, so the queue is a single line no matter how busy. Nobody tells you this at orientation.
```

Topic: Verrill Street Grill. Fact: one register. Counted, because the criterion asks for a number in the same chunk as the place name. It is the thinnest of the five.

```
Morrow House — what it's actually like

The good: cheapest housing tier by about $900 a year, and the singles are real singles.
```

Topic: Morrow House. Fact: $900 a year.

5 of 5. Target was 4 of 5. Same sample every time this command is run.

### Criterion 5 — the answer contains the phrase and cites a file that contains it

Same run-1 answers as criterion 2, checked against the chunk text above. Each answer contains the `expects` phrase, and the filename it names is a file whose text also contains that phrase.

| Question | Phrase in the answer | File named | Phrase in that file |
|---|---|---|---|
| Kestrel Commons wait | 20 to 25 | dining_kestrel_commons_followup.txt | yes |
| Housing lottery order | credit hours | admin_housing_lottery.txt | yes |
| CS 210 hours | 8 to 10 | course_cs_210.txt | yes |
| Pass/fail week | week eight | admin_pass_fail_option.txt | yes |
| Calder singles | 90 square feet | housing_calder_annexe.txt | yes |

Runs 2 and 3 name the same files and contain the same phrases. 5 of 5. Target was 4 of 5.

## Verdicts

Targets are the ones in `criteria.md` from unit 1. A criterion is MET only if the target held on every run, not on the best one. Nothing was revised: each check could be repeated the same way, and a miss would stay a miss.

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer (4 of 5) | MET | All three runs were 5/5, counting a question only when a retrieved chunk contained its `expects` phrase; Calder counts because rank 2 of `housing_calder_annexe.txt` contains "90 square feet" (rank 1 does not). |
| 2 | Every answer names a source (5 of 5) | MET | All 15 answers include a filename, which is the whole target, so one answer without one would have been a miss; pass/fail names `admin_pass_fail_option.txt` in parentheses on runs 1 and 2 and on a Source line on run 3. |
| 3 | Gate stops out-of-corpus questions (4 of 5) | MET | `run_eval.py::check_out_of_scope` refused 5 of 5, and the closest, Mongolia at 0.787, is still above the 0.55 cutoff, so the same 5/5 goes in every run column. |
| 4 | Chunk keeps a topic and its fact together (4 of 5) | MET | Four of the five printed chunks pair a topic with a price, a number of hours, or a named week, and no sentence is cut; Verrill's "one register" is the close fifth, and leaving it out still leaves 4 of 5. |
| 5 | Answer has the expected phrase and cites a file that has it (4 of 5) | MET | Every run's answer contains the `expects` phrase and names a file whose text also contains it, including Calder citing `housing_calder_annexe.txt`, the file that has "90 square feet." |

## Diagnoses

Nothing missed. All five criteria held on every run, so there is no failure to pin on loading, chunking, embedding, retrieval, or generation.

The targets were set so that could happen. Four of the five are 4 of 5, and criterion 1's reason for stopping there was that the Calder size question might miss. It did not miss under the check I wrote. Rank 1 for "How large are the singles at Calder Annexe?" is the layout paragraph in `housing_calder_annexe.txt` (distance 0.317): "Rooms are mostly singles, some doubles, in clusters of six around a lounge." The sentence with "90 square feet" is rank 2 in the same file (distance 0.336). The criterion counts any retrieved chunk, and top-k is 5, so rank 2 is a pass. Criterion 4 has the same kind of slack: Verrill's "one register" can be dropped and 4 of 5 still meets the target.

I would tighten criterion 1 to: for all 5 of 5 questions, the top-ranked chunk contains that question's `expects` phrase. On this log that is a miss, and the miss is at retrieval. The chunker kept "90 square feet" in one chunk with the building name, the embedder put that chunk 0.019 behind the layout paragraph, and search returned it inside the top 5. Generation then quoted the right fact and the right file. The written target treats "the fact is in the list" and "the fact is first" as the same success, which is why a first try could clear it.

## The Improvement

**What I changed:** `store.py::search` still retrieves by meaning, then reranks those candidates with BM25 (`store.py::_hybrid_order`). Cosine distance is unchanged, and the gate still reads the closest distance in the returned set. The keyword weight is 1.5. Weight 1.0 ties when the two systems swap rank 1 and 2, and that tie keeps the semantic order, which is the Calder miss.

**Why I picked it:** The diagnosis said retrieval already had the "90 square feet" sentence and had ranked the layout paragraph 0.019 ahead of it, so a keyword rerank is the change that can put the size sentence first without touching chunking or the prompt.

### Run Log — After

`python run_eval.py --label after` on 2026-10-03, cache off. Raw file: `results/run_2026-10-03_1933_after.md`, produced by `run_eval.py::main`. 15 model calls. The before log is above, under Run Log — Before.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunk keeps a topic and its fact together | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Answer has the expected phrase and cites a file that has it | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Criterion 4 is the same five chunks as the before log. I ran `python app.py chunks -n 5` again; `chunker.py::split_documents` printed the same text, starting with "On the add/drop deadline" and ending with Morrow House's "$900 a year." This change does not touch chunking.

The other four criteria are from the after file. Run 1 of each answer, produced by `generate.py::answer_from_chunks`:

```
Students state that the wait time at Kestrel Commons is 20 to 25 minutes between 12:15 and 1:00. This is mentioned in `dining_kestrel_commons.txt` and `dining_kestrel_commons_followup.txt`.
```

```
Juniors and seniors are ordered by accumulated credit hours first, with ties broken randomly. 

Source: admin_housing_lottery.txt
```

```
CS 210 Data Structures takes 8 to 10 hours a week outside class. 

Source: course_cs_210.txt (and course_cs_210_workload.txt)
```

```
A student can declare the pass/fail option as late as week eight, after seeing their midterm. 

Source: admin_pass_fail_option.txt
```

```
The singles at Calder Annexe are small, measuring about 90 square feet. 

Source: housing_calder_annexe.txt
```

Runs 2 and 3 also contain the `expects` phrase and a filename whose text contains it. The gate, from `run_eval.py::check_out_of_scope`, still refused 5 of 5:

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.826 | refused |
| How do I change the oil in a diesel engine? | 0.934 | refused |
| Who won the 1994 World Cup? | 0.847 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.849 | refused |
| How do I write a for loop in Rust? | 0.860 | refused |

**Did it help?** The five written targets were already 5/5 and they are still 5/5, so that table does not move. It helped the miss the diagnosis named. Before, Calder's top chunk was the layout paragraph and did not contain "90 square feet." After, `store.py::search` returns the size sentence first:

```
#1  distance 0.3362  housing_calder_annexe.txt#2
The bad: the singles are small — about 90 square feet — and the desks are fixed.

#2  distance 0.3171  housing_calder_annexe.txt#0
Second-year here. Built 2003. Rooms are mostly singles, some doubles, in clusters of six around a lounge.
```

The gate's best distance stays 0.317, because it uses the closest cosine in the set, and the layout paragraph is still rank 2. One side effect: Mongolia's best distance in the top 5 moved from 0.787 to 0.826, and diesel from 0.923 to 0.934, because the rerank dropped the nearest semantic chunk out of the five the gate sees. Both are still over 0.55, so criterion 3 stays met.

## What's Still Broken

None of the five written criteria is missed. After the rerank they are all still 5/5 against the targets in `criteria.md`. Two gaps are left, and the targets do not show them.

The gate's reported distance is no longer always the nearest semantic chunk. Mongolia moved from 0.787 to 0.826, and the diesel question from 0.923 to 0.934, because BM25 dropped the closest chunk out of the five the gate sees. Both are still above 0.55, so criterion 3 stays met. I would keep the semantic nearest neighbor in the set the gate measures, and let BM25 reorder only the chunks the model reads. I stopped because that is a second change, and these five refusals still hold.

The keyword weight of 1.5 exists to win Calder's rank swap. I do not have a question where meaning is right and the keywords point at a different chunk by a similar margin. That question could flip the wrong way, and criterion 1 would still pass as long as the right phrase stayed somewhere in the top 5. I stopped because this unit allows one change, and on these five test questions the phrase is now in rank 1.

## What I'd Do Differently

Criterion 1. I would write: for all 5 questions, the top-ranked chunk contains that question's `expects` phrase. The version in `criteria.md` counts any of the top 5 and allows one miss. That passed on the before log while the size sentence was rank 2, so the table could not show the failure this unit's change was for.

Criterion 3 I would keep at 4 of 5, and I would replace one probe with a campus question the corpus does not contain. Mongolia and the diesel question sit so far from 0.55 that dropping the true nearest neighbor still looks like a clean refusal.
