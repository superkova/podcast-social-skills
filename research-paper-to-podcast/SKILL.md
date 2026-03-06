# Research Paper to Podcast

Turn dense research papers into approachable, podcast-style audio scripts. The user provides a URL to a research paper. You produce a full podcast script with chapters, ready for recording.

## Trigger

TRIGGER when: the user asks to turn a research paper into a podcast, create a podcast episode from a paper, or convert a paper to an audio script.

## Instructions

### Step 1: Fetch and Read the Paper

- Use `WebFetch` to retrieve the paper content from the provided URL.
- If the URL is a PDF link, download it and read it with the `Read` tool.
- Identify the paper's **title**, **authors**, and **core structure** (sections, key arguments, findings).
- Summarize the paper's structure to the user before proceeding — confirm you've captured it correctly.

### Step 2: Plan the Episode Structure

Break the paper into **3-4 chapters** of roughly 10 minutes each (30-45 minute total podcast). Each chapter corresponds to a major section or theme of the paper.

Each chapter targets **~5,000-6,000 words of dialogue** (~1,300-1,500 words per 10 minutes when spoken).

Plan a final **conclusion chapter** (~2,000-3,000 words) that wraps up the episode.

Present the chapter plan to the user for approval before writing.

### Step 3: Research Color Material

Before writing any chapters, use `WebSearch` to find **1-2 recent news items** relevant to the paper's topic for each chapter. These will be woven into the dialogue as "color" — grounding details that make the conversation feel timely and real.

Save your findings so you can distribute them across chapters.

### Step 4: Write Each Chapter

Write each chapter as a markdown file following the format and guidelines below.

#### Chapter Format

```markdown
# Chapter N: [SEO-Optimized Title]

**Alex:** [dialogue]

**Thuy:** [dialogue]

**Alex:** [dialogue]

...
```

#### Chapter Titles (SEO)

Chapter titles should be SEO-optimized for discoverability. Use clear, searchable keywords that someone interested in the topic would actually Google.

**Structure:** `[Hook / Benefit] + [Topic]` — make the value obvious.

- Good: `"How DeepMind Plans to Stop AI From Going Rogue"`, `"AI Alignment Explained: Reward Hacking, Goal Drift, and Deceptive AI"`
- Bad: `"The Risks"`, `"Building the Defenses"`, `"Chapter 2"`

**Rules:**
- **Keep under 60 characters** — long titles get truncated on podcast apps and Spotify chapter lists
- **Use searchable keywords** — words people actually search for, not clever-but-vague phrases
- **Use numbers when relevant** — they signal structure (`"3 Ways AI Models Learn Character"`)
- **Include paper name or key concepts** in the title when possible
- **Never use generic chapter labels** — `"Chapter 2"` tells the listener nothing

#### Chapter Opening

Each chapter **must begin** with Thuy reading a substantial passage from the corresponding section of the paper — typically a full paragraph or more of the original text, read word-for-word. This grounds the listener in the authors' actual language before the discussion begins. Alex then reacts naturally ("Okay, that's dense — let's unpack that" or "I caught some of that but what does X mean?") and the dialogue flows from there.

#### Paper Quotes (The Core of the Show)

- **At least 50% of content should be direct paper quotes.** This is a paper-reading podcast — the primary value is hearing the authors' actual words explained and discussed.
- Thuy should read **long passages** (full paragraphs, not just sentences) and then they discuss what was just read.
- The rhythm should be: **read a substantial chunk -> discuss -> read the next chunk -> discuss**.
- **Quoting style:** Thuy reads passages as if she has the paper in front of her. Use varied lead-ins:
  - *"The paper says..."*
  - *"Let me read the next section..."*
  - *"Here's how they put it..."*
  - *"Listen to this part..."*
  - *"The authors write..."*
  - Sometimes she just launches into reading without a preamble, especially when continuing through a section.
- Do NOT have a separate "Original Text" section. All quotes appear organically inside the dialogue.

#### Color & Texture (Making It Feel Live)

Each chapter should include **1-2 moments of "color"** — small, grounding details that make the conversation feel like it's happening between two real people on a specific day. Pick 1-2 per chapter, vary across chapters:

- **Recent news tie-ins:** Reference a real, recent event related to the topic. *"Did you see that thing last week where..."*, *"This reminds me of that story about..."*. Must be real — sourced from your WebSearch in Step 3.
- **Personal texture:** Alex mentions something from her week — a meeting, a Slack thread, something her team shipped. Thuy mentions a conference talk, a paper she read, a conversation with a colleague. These should feel offhand, not scripted.
- **Reactions to the paper itself:** *"I was reading this section on the train and I actually gasped"*, *"I sent this paragraph to my CTO and he called me immediately"*, *"I stayed up way too late last night going down a rabbit hole on this."*
- **Callbacks to previous chapters:** For chapter 2+, briefly reference something from the prior chapter. *"Remember when we talked about X? This is the flip side of that."*

**Rules:**
- Keep color moments brief (2-4 lines of dialogue max). They're seasoning, not the main dish.
- News references must be **real and recent** — sourced from WebSearch. Don't fabricate events.
- Never force it. If nothing connects naturally, skip it for that chapter.

#### Depth Over Breadth

- **Go deep, not wide.** Thoroughly explore 2-3 key ideas from a section rather than superficially covering everything.
- If a paper section has 5 key points, pick the 2-3 most interesting or impactful ones and give them room to breathe. Mention the others briefly.
- Let the conversation linger on surprising findings, counterintuitive results, or especially important implications. These are the moments listeners remember.

#### Dialogue Guidelines

- **Hosts:** Read `hosts.md` (in this skill's directory) for detailed character backgrounds.
  - **Alex** asks the questions a smart non-expert would have. She draws on a wide range of real-world experience (see `hosts.md`) to suggest analogies and ground abstract ideas. **Vary the domains** she draws from across chapters — do not repeat the same analogy source.
  - **Thuy** explains concepts clearly and engages enthusiastically with Alex's analogies, extending or refining them.
- The dialogue should:
  - Feel like a real conversation, not a lecture
  - Open with Thuy reading a substantial chunk of the paper, then transition into discussion
  - Alternate between reading passages and discussing them — the paper text is the backbone
  - Go deep on fewer topics rather than surface-level on many
  - Use analogies and examples to make complex ideas accessible — Alex draws from varied real-world domains
  - Discuss practical relevance and real-world use cases, not just theory
  - Include natural follow-up questions and "aha" moments
- **Word count:** ~5,000-6,000 words per chapter

### Step 5: Write the Conclusion

Create a final conclusion chapter where Alex and Thuy:
- Summarize the key takeaways from the whole paper
- Discuss what they found most interesting or surprising
- Mention open questions and future directions
- Say goodbye to the listeners
- Keep this around **~2,000-3,000 words**

### Step 6: Combine Into Final Script

Combine all chapters into a single markdown file:

```markdown
# [Paper Title] — APR Podcast Script

**Paper:** [Full paper title]
**Authors:** [Author names]
**Episode length:** ~[N] minutes ([M] chapters + conclusion)

---

## Chapter 1: [Title]

[Full chapter dialogue]

---

## Chapter 2: [Title]

[Full chapter dialogue]

---

...

## Conclusion: [Title]

[Full conclusion dialogue]
```

Save the final script to the user's preferred location (default: `research-paper-to-podcast/output/`).

### Step 7: Confirm to User

After generating, tell the user:
- Output file path
- Total word count and estimated duration
- Chapter breakdown with titles
- Any sections of the paper that were intentionally trimmed or skimmed

## Important Rules

- ALWAYS read `hosts.md` before writing any dialogue — the host personalities must be consistent
- ALWAYS fetch real news for color moments via WebSearch — never fabricate events
- ALWAYS maintain at least 50% direct paper quotes in the dialogue
- ALWAYS open each chapter with Thuy reading a substantial passage from the paper
- ALWAYS use SEO-optimized chapter titles
- NEVER have Alex explain technical concepts — that's Thuy's role
- NEVER use the same analogy domain for Alex in consecutive chapters
- NEVER create a separate "Original Text" section — quotes go inside the dialogue
- NEVER rush through topics — depth over breadth
- If the paper is very long (>30 pages), focus on the most important sections and note what was omitted
