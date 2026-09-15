---
name: writing-guidelines
description: Prose written for humans, in any container - Markdown, a README, a report, a PR body, a commit message, a code comment or docstring. Use before writing such prose, and when asked to review docs, check style, or audit voice and tone. For a document an agent reads, pair with writing-for-agents.
metadata:
  version: "3.0.0"
  argument-hint: <file-or-pattern>
  source: adapted from vercel-labs/writing-guidelines
---

# Writing guidelines

The rules for prose a human reads, held in this one file. Read them before drafting and write to them from the first sentence, so the draft carries the shape of the rules rather than the shape of a first attempt.

## Writing

1. Name the reader and what they will do with the text: configure, decide, debug, merge. Every choice below serves that job.
2. Pick the document kind under “Tone by document kind” and hold its tone throughout.
3. Draft to the rules. Lead with the conclusion, then the reasons.
4. Read every sentence once at speech pace. Done when each sentence parses on the first read and every rule holds.

## Reviewing

Read the target files, or ask the user which. Run `~/.claude/scripts/check-writing.py <path>` for the mechanical rules: typography, banned words, source formatting. Then apply every remaining rule to every line by hand; voice, concision, AI tells, and structure are judgement calls the script skips.

Report each violation as `file:line - rule, fix`, grouped by file, with a bare `✓ pass` for a clean file. Sacrifice grammar for brevity. Done when every rule has met every line.

## By container

The rules target documentation pages. Every container keeps the sentence-level rules (reader first, voice, banned words, concision, AI tells, punctuation); the page-level rules (headings, structure, lists, code, links) apply as follows:

- **Code comment or docstring**: one idea, present tense, the why over the what. No headings, summaries, or links.
- **Commit message**: imperative subject line; body in paragraphs that say why the change exists and what it trades off.
- **PR body**: one opening paragraph with what changed and why, then what to review as a list.
- **README, report, or page**: every rule applies.

## Reader first

- Lead with the conclusion; reasons and detail follow. A reader who stops after the first sentence still leaves with the point.
- One idea per paragraph, 2 to 4 sentences; split anything covering two ideas.
- Concrete over abstract: an example, a number, or a name beats a category.
- Say why, not only what. The reason is the part the reader cannot infer from the artifact itself.
- Earn every detail: cut a number, name, or implementation detail when a more general phrasing leaves the reader's understanding and next action unchanged.

## Voice

- Active voice. Mental test: append “by monkeys”. If the sentence still parses, rewrite it.
- Direct address: `you`, in place of `the user` or `one can`.
- Imperative for steps: “Click **Add Project**”, in place of “You will need to click **Add Project**”.
- Sentences under 20 words as the target.
- Contractions (`you'll`, `it's`) for warmth.
- Present tense unless describing future behaviour.
- `We` only for a deliberate action by the authoring team (“we recommend”, “we deprecated”); it is never a stand-in for `you`.
- Statements, not rhetorical questions: a question the writer answers reads as marketing.
- Second-read test: read each sentence once at speech pace. If you re-read to parse it, name the subject, the action, and the consequence, and cut metaphor verbs and pronouns whose referent sits more than one sentence back.

## Banned words

- `easy`, `simple`, `quick`: pressure the reader and read as marketing. Replace with the concrete fact: “one command”, “default settings”, “most projects skip this”.
- `very`, `just`, `really`, `simply`: filler. Cut or rewrite.

## Concision

- Weasel words: replace vague qualifiers (`significantly`, `many`, `often`, `typically`, `generally`) with a specific number or claim.
- Vague quantifiers: `near-zero`, `sub-second`, `most requests` become a figure with a source (`99.37% of requests see zero cold starts`).
- Metaphor verbs: name the literal action in place of cadence (`moves through`, `lands`, `carries`, `hits` become the actual step).

## AI-generated tells

- Summary-style transitions: a paragraph that opens by recapping the last one (`With this setup complete…`, `Now that we've explored…`). Pivot straight to the next point (`In practice…`, `The catch is…`).
- Stop-start sentences: one dependent idea split into choppy fragments (`Previously this was manual. Now it's automatic. This saves time.` becomes one sentence). Short sentences for emphasis stay.
- Spec-sheet voice: sentences that read like a system reciting a datasheet (`provides`, `is configurable`, `is explicitly labeled`).
- Cold-open paragraphs: a body paragraph whose first sentence works as a standalone heading has no antecedent. Carry the prior subject forward (`Because…`, `Once…`).
- Personified artifacts: machines performing human-physical actions (`hand the browser a URL` becomes `the browser fetches the URL`; `the token holds…` becomes `the token is stored…`).
- Reused framing: the angle comes from this document, not a template (`The question most teams face is whether…`).

## Tone by document kind

- **Tutorial**: warm, encouraging, predictable structure, no traps.
- **How-to**: terse and direct; the reader is mid-task.
- **Reference**: neutral, exhaustive, quotable.
- **Conceptual**: explain it so the reader could teach it back; examples and analogies welcome.
- **Troubleshooting**: empathetic without apologising; acknowledge, then fix.
- A document does one job: tutorial or how-to or reference, one at a time.

## Headings

- Sentence case at every level: “Configure environment variables”.
- The title is user-shaped (the reader's question), not feature-shaped (the engineer's name).
- Subheadings descriptive, never a single generic word: “Caveats when self-hosting on Cloudflare”, in place of “Caveats”, “Overview”, or “Notes”.
- The reader can guess a section's content from its heading alone.

## Structure

- The document opens with a one-paragraph summary of what it covers.
- Every major section opens with a summary sentence.
- Acronyms spelled out on first use: “Content Security Policy (CSP) blocks inline scripts”.
- Every term defined the first time it appears, with a link to its conceptual page where one exists.
- Reference material organised by surface; educational material organised by reader task.

## Lists

- Three or more list-shaped items in a paragraph become a list.
- Bulleted for unordered; numbered for ordered (lifecycles, sequential steps).
- A colon introduces every list.
- Periods at the end of list items only when the items are full sentences.
- Term lists use `- **Term**: description`.

## Code

- Every code block carries a language tag.
- Highlight load-bearing lines where the renderer supports it: `` ```typescript {8-12,23-37} ``.
- At most 80 columns per line and 25 lines per snippet; longer blocks split with prose between them.
- Omit defaults and repeated variable definitions.
- Prose explains what each code block does; comments inside the block stay minimal.
- The document is the deliverable: inline the code rather than pointing at a full example file elsewhere.

## Placeholders

- Text placeholders in descriptive `snake_case`: `your_access_token_here`, so the reader can double-click to select it before pasting.
- Number placeholders count up: `1234567890123`, recognisable as fake and predictable.
- `<TOKEN>`, `xxx`, `your-token`, and generic ALL_CAPS are banned.

## Units

- Space, then an uppercase unit: `64 KB`, `5 KB`, `200 ms`. Seconds stay bare: `30s`.
- Consistent across the corpus so readers develop scanning habits.

## Emphasis

- **Bold** marks a UI element or a critical fact. Reaching for bold to add tone means the sentence is weak; rewrite it.
- `Inline code` for paths, file extensions, identifiers, and short snippets: `/api`, `.tsx`, `body`, `req`. If it would look odd outside a monospace font, monospace it.

## Punctuation

- Colons, commas, and periods carry the rhythm; the em dash (`—`) and the hyphen used as one are banned. Rephrase when a colon or comma feels forced.
- Curly quotes (`“ ”`, `‘ ’`) in prose; straight quotes stay in code.
- The ellipsis character (`…`) in place of three dots; loading states end with it: `Loading…`.
- `&` in place of “and” only where space is constrained: nav labels and buttons.

## Source formatting

- One paragraph is one source line; the editor wraps it.
- One blank line before a heading; one before and after a code block.
- Headings separate sections; horizontal rules (`---`) are banned.
- Blank lines only where a paragraph breaks.

## Links

- Anchor text names the destination; bare URLs and `here` or `link` are banned.
- Link the canonical page for a product or concept rather than restating it.
