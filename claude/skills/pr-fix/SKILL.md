---
name: pr-fix
description: "Work the review feedback on a change: fix what is settled, grill what is open, discuss the rest, then reply to and close every thread."
argument-hint: "<PR id> or nothing"
disable-model-invocation: true
---

# Work the review feedback

Read the review feedback on a change, settle what it asks for, land the fixes, and close every thread. `pr-review` is the other half of the loop: it posts the findings this skill works.

Call the Skill tool with `pr` first, for the forge vocabulary and the operation contract every step below calls by name. **The split** and the four end states are this skill's own words: every finding carries one label from each, and the labels decide which step handles it.

## The subject

The skill's argument names the feedback to work:

- **A PR id**: every live thread on it is in scope
- **A pair**: every live thread across both sides is in scope, and a fix in one repo can settle a finding in its sibling
- **Nothing**: read `pr.queue` for what is waiting on the user, offer it, and ask which before reading. With no user to ask, `pr` says to report the queue and stop

## The split

Every live finding is one of two, and the label decides which step handles it:

- **Settled**: it determines one defensible change, and step 4 applies it
- **Open**: it admits more than one defensible change, or it disputes a decision the code already makes, and step 3 grills it

Label a borderline finding **open**: the interview costs a round, while a silent pick spends a decision that belongs to the user.

A finding ends in one of four states, and step 5 puts it there:

- **Fixed**: a commit addresses it
- **Answered**: a reply gives the reason it takes no change
- **Deferred**: the reviewer is right and the work sits outside this change, so a reply names the issue that now tracks it
- **Discussed**: a reply contests the claim or asks the reviewer a question, and the thread stays open for them

## Process

### 1. Read the feedback

Fetch the head the way `pr` describes checkout, and stay on your branch: step 4 checks out.

Read every live thread through `thread.list`, general and anchored. The general comment carries no anchor and is where the reviewer names what blocks the merge, so read it like any other finding and give it the whole diff as its subject. Read `blocker.list` alongside, because step 5 closes each blocker against the merge decision.

**Done when** the forge is named, and every live thread is listed with its ID, its anchor, the change it asks for, and any suggestion or blocker attached to it.

### 2. Sort every finding

Read the anchored code before labelling, because the finding is a claim about the diff and the diff is the evidence. A finding that misreads the code is still one to answer: label it settled, with no change attached and the misreading written down.

Resolve drift here. A review lands against a head that has since moved, so confirm each anchor against the current head through `pr.diff-line` before carrying its number into any later step.

**Done when** every finding carries one label from the split, a current anchor, and, when settled, the change it takes.

### 3. Grill the open findings

Carry every open finding into a single interview, the way `pr` describes the frontier. Give each question the reviewer's words, the anchored code, and your recommended answer.

An answer can also be that the reviewer is wrong, which routes the finding to **discussed**. When the interview settles a term or a decision the repo records, call the Skill tool with `domain-modeling` and write the glossary entry or ADR it earns. A finding that changes only the lines under it needs neither.

**Done when** every open finding holds an answer, from the user or from the question left for the reviewer.

### 4. Apply the fixes

Check the branch out first, so this step and step 5 have the branch they edit. A dirty tree stops the step, per `pr`: report the files and let the user settle them, rather than stashing work that is not yours. Change what the finding asks for and stop there. Apply an attached suggestion the way `pr` describes. Keep one commit per finding, so step 5 can cite a SHA apiece.

Run the repo's own checks, the way `pr` describes them.

**Done when** every settled finding has a commit that addresses it or a written reason it takes none, and the repo's checks pass locally.

### 5. Reply and close out

Re-read the remote the way `pr` describes branch drift, since a reviewer who pushed while step 4 ran is about to be overwritten. Push, so every reply cites a SHA that exists on the remote. Then write one `thread.reply` per finding the way `pr` describes writing, and put it in its end state:

- **Fixed**: name what changed and the commit that changed it, then `thread.resolve` it and lift its blocker through `blocker.resolve`
- **Answered**: give the reason it takes no change, cite the file or spec that carries the evidence, then resolve it
- **Deferred**: name the issue now tracking the work and the reason it sits outside this change, then resolve it and lift its blocker through `blocker.resolve`
- **Discussed**: ask the question or contest the claim with the evidence, and leave the thread open for the reviewer

Read `checks.read` on the pushed head, and `checks.log` for anything red, since the failing lines say which finding it belongs to. A check red for the change is step 4's work again: put its thread back through `thread.reopen` and go back. A red for a cause outside the diff takes a reply of its own on the general comment, the way `pr` describes checks.

A thread the reviewer revives is live again: take it through `thread.reopen` when the forge closed it, and work it from step 2.

**Done when**:

- every thread from step 1 carries a reply
- every fixed, answered, or deferred one reads as resolved on the forge
- the pushed head is green or carries the reply explaining why it is not
