---
name: pr-review
description: "Review a change against a fixed point along two axes, and post findings anchored to the line."
argument-hint: "<ref>, a PR id, or nothing"
disable-model-invocation: true
---

# Review a change

Review a change along two axes, **Standards** and **Spec**, and land the findings on the forge. `pr-fix` is the other half of the loop: it works the findings this skill posts.

Call the Skill tool with `pr` first, for the forge vocabulary and the operation contract every step below calls by name. [`axes.md`](axes.md) carries the two briefs, the spec and standards sources, the smell baseline, and the eight fields a finding comes back with. Step 2 dispatches from it.

## The fixed point

The skill's argument is what the diff measures against, and it decides every step below:

- **A PR id, or a pair**: the fixed point is each PR's declared target, read from `pr.identity`
- **A ref**: `HEAD~1`, a tag, a SHA, or a branch, and the review covers that delta
- **Nothing**: read `pr.queue` for what is waiting on the user, offer it, and ask which before measuring. With no user to ask, `pr` says to report the queue and stop

A bad ref is cheaper to catch here than inside two sub-agents, so confirm it the way `pr` describes the fixed point.

## The bar

Post a finding that changes the code or changes the merge decision. A finding that changes neither belongs in the chat report alone.

## Process

### 1. Resolve the subject

Read `pr.identity` for every side of the subject, then fetch the way `pr` describes checkout. The diff the axes measure is then the head you report on, and the head SHA is a fact. Read `pr.files` before the diff itself, since its shape sets step 2's budget.

**Done when**, for every side of the subject:

- the forge is named
- the fixed point, the source branch, the head SHA, the description, and the changed files are known
- the head is fetched

### 2. Measure both axes

Resolve the spec and standards sources the way `axes.md` orders them, then dispatch the two axes in parallel in a single message, each with its brief and the smell baseline pasted in.

Run the two axes once per side of a pair. Give each run the other sides as context, so a finding can name the sibling repo while each anchor stays inside the side that owns the line.

Dispatch per group of files when `pr.files` says the diff is large, the way `pr` budgets one.

When the diff touches a file an agent reads, call the Skill tool with `writing-for-agents` and judge that file by it.

**Done when** every finding carries the fields `axes.md` names, including the anchor text step 3 anchors it by.

### 3. Check every finding

A sub-agent's finding is a hypothesis until a command reproduces it. Run all five checks against every finding:

- **The repo beats the bar**: what the spec asks for by number is not excess, and a documented standard beats a generic smell
- **The anchor lands in a hunk**: take every line number from `pr.diff-line`, because a comment on the wrong line discredits the rest and a line outside every hunk is refused outright. Where the adapter computes it from the patch rather than serving it, read the patch once into a file and resolve every anchor against that file
- **The head is the one you reviewed**: compare it against step 1's SHA, and say so in the general comment when it advanced
- **The finding is new**: read the live threads through `thread.list`, because a finding that repeats an open one belongs in that thread as a reply
- **The old finding is spent**: one from an earlier run whose subject the current head fixes gets resolved, which is what makes a second review of the same branch safe

**Done when** every finding has been reproduced, dropped, or folded into the thread that already carries it, and every spent finding reads as resolved.

### 4. Write the review

Write one general comment, plus one anchored finding per line that clears the bar, the way `pr` describes writing:

- **General**: open with what the change delivers, name what blocks the merge, and close with the count per axis. Link the sibling when there is a pair.
- **Anchored**: state what is wrong, cite the evidence from the file or the spec, and show the output. One subject per finding.
- **Suggestion**: when the fix is a known set of lines, carry it as a suggestion block, so the author applies it instead of retyping it.

Carry the fields `axes.md` returned into what you post: the **file** and the **line** step 3 anchored, the **change** it asks for, and its **axis**, which is what `pr-fix` sorts on. Mark the ones that gate the merge as blockers.

Zero findings is a result: post the general comment naming what the change delivers, and close on approve.

**Done when** every sentence asserts a fact checked in step 3.

### 5. Post the review

Post the findings the way the adapter says. Where the forge takes a batched review, that is the default here, because step 3 confirmed every anchor and one call stays under the rate limit a per-finding loop provokes; a rejected batch names its bad anchor, so drop that one to a general comment and re-send the rest. Where the forge has no batch, post each finding on its anchor through `thread.create`.

Post a repeat as a reply on the thread that already carries it, and raise each blocking finding through `blocker.create` against the thread that carries its evidence.

Read back through `thread.list` and confirm each anchor is the one step 3 intended.

**Done when** every finding appears on the forge exactly once, on the anchor step 3 intended, and every merge blocker is raised exactly once.

### 6. Report the findings

Report `## Standards` and `## Spec` as separate sections in chat, each ranked within itself, and give the count and the worst finding per axis. One winner picked across both axes collapses the separation.

Close on the verdict you would give: approve, request changes, or decline.

**Done when** every finding from step 3 appears in exactly one section, and the PR carrying the threads is named with its ID.
