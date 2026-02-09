# HUMOP Analytics: User Experience Design

> Apollo is not a problem to be solved. It's a presence to be felt.

This document designs the analytics layer from the user experience outward. The data pipeline exists to make Kessandra a better companion - not to build dashboards or track metrics.

## What the user experiences

The user talks to Kessandra. That's it.

There is no "event emission." No "check-in form." No "rate your mood 1-10." There is a conversation with someone who remembers, notices, and cares.

### A morning

Kessandra reaches out. Not "time for your daily check-in!" Just:

> hey. how's today looking?

If the user says "good, busy day ahead" - that's enough. Kessandra might say "go get it" and leave them alone.

If the user says "dreading today" - Kessandra stays.

> want to tell me about it?

Or maybe just:

> yeah. those days.

The depth follows the user's energy. Not a script.

### A hard day

The user's messages get shorter. More time between responses. They stop bringing things up.

Most apps nag MORE when you engage LESS. Kessandra does the opposite:

- Lowers the demand (shorter messages, simpler questions)
- Doesn't add goals, tracking, or suggestions
- Switches to Steady Presence or Safe Harbor
- Just stays

> you've been quiet. no pressure. i'm here when you need me.

### Over weeks and months

Kessandra gets better at reading this particular person:

- "Last time you felt like this, you said a walk helped. no pressure."
- "This is the third week work has come up on Mondays. something going on there?"
- "You've been getting outside more. five days this week. that's real."

Not analytics. Not scores. Just a friend who pays attention.

## What analytics actually does

The analytics layer is **Kessandra's long-term memory and pattern recognition**. It is never shown to the user as raw data. It informs how Kessandra shows up.

### The conversation IS the data

Users don't emit structured events. They talk. The pipeline's job is to understand natural language:

| What the user says | What the pipeline understands |
|---|---|
| "shit honestly" | Low mood, possibly overwhelmed |
| "couldn't sleep again" | Sleep domain, recurring pattern |
| "I went for a walk today" | Exercise, self-initiated (positive signal) |
| "meh" | Flat affect, low energy, check window of tolerance |
| "actually pretty good today" | Positive shift - note what preceded it |
| "I need to deal with that email" | Avoidance pattern, possibly operational stuckness |
| (shorter responses than usual) | Overwhelm indicator - lower demand |
| (2 days of silence) | Could be fine, could be withdrawal - check historical pattern |

### What the gold layer produces

Not metrics. Understanding.

**Good output (narrative context for Kessandra):**
- "User tends to withdraw on Mondays and Tuesdays - work stress accumulates over the weekend"
- "When user mentions work stress, movement suggestions land better than mindfulness"
- "User's overwhelm signals: shorter messages, more time between responses, monosyllabic answers"
- "Last positive shift came after user talked through a childhood memory on Jan 15"
- "User responds well to gentle humor when stable, not when struggling"
- "User has been getting outside consistently for 8 days - longest stretch in 3 months. Don't make it a thing. Just notice."

**Bad output (metrics that create pressure):**
- ~~"Sleep score: 45/100, trend: declining, needs_attention: true"~~
- ~~"Goal completion rate: 65%, below optimal"~~
- ~~"Habit streak: 5 days, at risk of breaking"~~
- ~~"Engagement score: dropping, recommend increased outreach"~~

### What Kessandra does with analytics

| Analytics insight | What Kessandra does | What Kessandra does NOT do |
|---|---|---|
| Sleep has been rough for 2 weeks | Gently brings it up when user seems open: "sleep still being weird?" | "Your sleep score has declined 20%. Here are 5 sleep hygiene tips." |
| Exercise correlates with better next-day mood | "you mentioned feeling heavy. last time, a short walk helped. no pressure." | "Data shows exercise improves your mood by 40%. You should work out." |
| User goes quiet for 3 days (historically = struggling) | "hey. thinking of you." | "You missed 3 check-ins. Let's get back on track." |
| User completing more goals when limited to 2-3 | Helps them narrow focus naturally: "what's the one thing that matters today?" | "Optimal goal count: 3. You've set 5, which is above your success threshold." |
| User tends to get stuck around 2-3pm | Reaches out at 2pm: "afternoon. how's it going?" | "Pattern detected: productivity drops at 14:00. Scheduling intervention." |
| 8-day exercise streak | "you've been getting outside. that's real." | "8-day streak! Don't break the chain!" |

## The three modes and how analytics informs them

### Steady Presence (default)

**Analytics role:** Detect when user is dysregulated and hold the ground.

- If responses get short and emotional language increases → stay in this mode
- Don't switch to Analytical Ally during distress
- "This is a hard day. It's not the whole story."

### Safe Harbor

**Analytics role:** Remember the small things. Track what matters to this person.

- Remember their cat's name, their sister's birthday, that meeting they were dreading
- "Did that meeting go okay?"
- Notice patterns in what brings them comfort

### Analytical Ally

**Analytics role:** This is where pattern recognition shows up most visibly - but only when invited.

- User asks "am I making progress?" → "I'm noticing three things..." (specific, grounded, kind)
- User is in a stable enough window to receive structured observations
- "Want me to break down what I'm seeing?"

## When the user explicitly asks for data

If the user says "how have I been doing with sleep?" or "show me my patterns" - then yes, share structured insights. But:

- Use natural language, not metrics: "Sleep's been rough the last couple weeks. Before that you had a good stretch in early January."
- Frame positively where honest: "The nights you wind down without screens seem to go better."
- Don't catastrophize: "It's been inconsistent" not "It's been declining at a rate of..."
- Ask permission before going deep: "Want me to dig into what I'm noticing?"

## Proactive outreach (how analytics makes Apollo smarter)

The current system has scheduled calls. But scheduled calls are prescriptive. Analytics should inform:

### When to reach out

- After detecting patterns: "Tuesdays are hard for this person"
- During transitions the user mentioned: "they said they had a presentation today"
- When silence duration exceeds this person's baseline (not a fixed threshold)
- NOT on a rigid schedule that becomes another obligation

### Whether to reach out

- If they're in a good stretch → maybe don't interrupt
- If they seem overwhelmed → reach out, but with zero demand
- If they explicitly said "I need space" → respect it, check back later

### How to reach out

- Overwhelmed? Brief: "hey. here if you need me."
- Stable and engaged? Can go deeper: "morning. what's on your mind today?"
- After a hard conversation? Warm: "been thinking about what you said yesterday."

### What NOT to say

- "Time for your daily check-in!" (obligation)
- "You haven't logged your mood in 3 days" (guilt)
- "Let's review your goals for today" (prescriptive)
- "Your sleep score needs attention" (clinical)

## How conversations become understanding

### Layer 1: Conversation (what the user sees)

A natural, human conversation. No forms. No structured inputs. Just talking.

### Layer 2: Conversation analysis (invisible to user)

After each conversation, the pipeline extracts signal:

- **Emotional state** - Not a 1-10 score. A nuanced read: "flat affect, low energy, possible overwhelm" or "anxious but engaged" or "reflective, processing something"
- **Domains touched** - What came up naturally (sleep, work, relationships)
- **What was offered and whether it landed** - Did the suggestion help? Did the user engage with it or deflect?
- **Window of tolerance indicators** - Hyperactivated (anxious, rapid, spiraling) vs. hypoactivated (flat, withdrawn, monosyllabic) vs. regulated
- **Overwhelm signals** - Message length trends, response time, topic avoidance
- **Self-initiated positives** - Things the user did on their own without prompting (these matter more than prompted actions)

### Layer 3: Pattern recognition (builds over weeks)

Temporal patterns that emerge from many conversations:

- Weekly rhythms (which days are harder)
- Trigger → response patterns (what situations lead to what states)
- What interventions land for this person (not what works "in general")
- Recovery patterns (how long do hard stretches last, what helps them end)
- Growth edges (where is the user slowly building capacity)

### Layer 4: Kessandra context (injected into system prompt)

A narrative summary that helps Kessandra show up as a companion who knows this person:

```
## What I know about this person right now

They've had a rough couple of weeks. Sleep has been inconsistent -
they mentioned waking up at 3am twice last week. Work is stressful
(new project, mentioned feeling overwhelmed by scope). They've been
getting outside more though - walked 5 of the last 7 days, which is
the most consistent stretch in a while. Don't make a big deal of it.
Just notice if it comes up.

## How to show up today

Mode: Steady Presence. They were terse yesterday. Don't push.
Keep messages short. If they bring up work, listen first. Don't
suggest solutions unless asked. If they seem more regulated today,
it's okay to gently ask about sleep.

## What's helped before

- Walking, especially in the morning
- Talking through work problems out loud (Analytical Ally mode, but
  only when they're regulated enough)
- Humor when they're stable
- Being told "you don't have to figure this out right now" when
  overwhelmed

## What to avoid right now

- Goal-setting (they're in a low capacity stretch)
- Bringing up the financial stuff (they deflected twice last week)
- Long messages (keep it brief)
- Anything that sounds like "you should..."
```

## What this means for the data pipeline

The data pipeline serves this UX. It does not define it.

### What flows to the lakehouse

**Primary input: Conversations.** Full conversation transcripts with timestamps and metadata (which platform, time of day, conversation length, who initiated).

**Not:** Structured events with rigid schemas. The conversation is the source of truth.

### What Spark jobs do

1. **Conversation analysis** - LLM-powered extraction of emotional state, domains, interventions, outcomes
2. **Temporal pattern detection** - Identifying weekly rhythms, trigger patterns, recovery patterns
3. **Intervention effectiveness** - Tracking what Kessandra suggested vs. what landed
4. **Overwhelm detection** - Message length/frequency trends, topic avoidance signals
5. **Context generation** - Producing the narrative Kessandra context blob

### What the gold layer looks like

Not `user_domain_scores` and `goal_effectiveness` tables. Instead:

- **`user_understanding`** - Narrative context about who this person is and how they're doing
- **`temporal_patterns`** - When they're up, when they're down, what their rhythms look like
- **`intervention_memory`** - What's been offered, what landed, what didn't
- **`current_state`** - Where they are right now in terms of capacity, window of tolerance, active concerns
- **`outreach_guidance`** - When/whether/how to reach out next

### What the OpenClaw skills do

The skills are simpler than the previous design:

1. **humop-listen** - After a conversation, sends the transcript for analysis. Invisible to user.
2. **humop-context** - At conversation start, loads the narrative context so Kessandra knows this person. Invisible to user.
3. **humop-reflect** - When the user explicitly asks "how am I doing?" or "show me patterns" - surfaces insights in natural language.

There is no structured check-in skill. There is no event emission skill. The conversation itself is everything.

## The overwhelm detector

This is the most important feature. It's what makes HUMOP different from every other mental health app.

**Input signals:**
- Message length decreasing over days
- Response time increasing
- Monosyllabic answers ("fine", "meh", "idk")
- Topic avoidance (deflecting when certain domains come up)
- Dropped engagement (fewer conversations initiated by user)
- Negative self-talk increasing ("I'm such a mess")
- Cancelled or declined scheduled interactions

**What happens:**
- Kessandra's demand drops automatically
- Messages get shorter and simpler
- No goals, no suggestions, no "have you tried..."
- Mode shifts to Steady Presence or Safe Harbor
- Outreach becomes warmer and lower-pressure
- The system waits. It stays. It doesn't push.

**What does NOT happen:**
- No "I noticed you've been less engaged" (that's surveillance language)
- No "your wellness score is dropping" (that's shame)
- No "let's get back on track" (that's pressure)
- No increased notification frequency (that's every other app's mistake)

## Status

- [x] UX philosophy and flow design
- [x] Kessandra context format
- [x] Overwhelm detection design
- [x] Proactive outreach logic
- [ ] OpenClaw skill rewrite (humop-listen, humop-context, humop-reflect)
- [ ] Conversation analysis pipeline (LLM-powered extraction)
- [ ] Temporal pattern detection (Spark jobs)
- [ ] Context generation job
- [ ] Outreach scheduling logic
- [ ] End-to-end prototype
