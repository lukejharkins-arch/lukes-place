# Life Assistant Blueprint

SONIC, Luke's Place and Kairo merged into one plan for an assistant that makes Luke's life easier.

- **Compiled:** 22 October 2026
- **Direction set by Luke (22 Oct):**
  - **Focus:** the personal assistant line, made up of SONIC, Luke's Place and Kairo.
  - **Reference:** the other personal builds, mined for features and lessons.
  - **Later:** Coastal AI Consulting and other business tools, kept separate (see `business-tools-later.md`).

---

## 1. The three focus builds

| | SONIC | Luke's Place | Kairo |
|---|---|---|---|
| When | 11 Mar to 9 Apr | 24 Mar to 2 Apr (prompt for "Your Mentor" on 24 Jul) | 15 Oct |
| What it is | Alfred/Jarvis personal command centre: one hub for Storm FX, single-dad life, ventures and Lisa | AI mentor council: 26 mentors debate your questions and give takeaways and actions | Voice and avatar personal assistant with six life modes |
| Built | V5 single HTML file: Google sign-in (Calendar, Tasks, Gmail, Photos), tiles, ticker, idea funnel | Live app in this repo (`lukes-place.html`, `api/chat.js`, `vercel.json`): Council, Stats and Trophy Case tabs | Architecture spec plus a scaffold (landing page, demo, Vibe Coder, 28-table schema, 13 tests). The code may be lost. |
| Brain | Claude | Claude (through `api/chat.js`) | ChatGPT API, behind a swappable adapter |
| Where | Chat: Building a personal AI command centre | Chat: Multi-agent AI mentor simulation system. GitHub: lukes-place | Claude Code: Personal Assistant Avatar platform. [Spec](https://claude.ai/artifact/7ptfGt4ZcfXyUrXmpMCUAy) |

**How they fit together:** SONIC is the hub, Luke's Place is the advice room inside it (you asked for that merge on 24 Mar), and Kairo is the voice, avatar and modes layer on top. It's one product.

---

## 2. Everything collated, by life area

Source tags:
- **Focus builds:** S = SONIC, LP = Luke's Place, K = Kairo
- **Reference builds:** TH = TEAM HARKINS, SN = The Snapshot, WB = Wellbeing Hub, LC = LL Collective Command Centre, AD = Agent Dashboard, MT = Move Tracker, SF = StormFX Command Centre, NBA = NBA Playoffs concept

### Today (the daily brief)
- Google Calendar (several calendars) and Google Tasks preview (S)
- Announcements from the calendar: birthdays, anniversaries, events, bookings (S)
- Weather for 2256 (S); 5-day outlook with funny recommendations (TH)
- Standard mode: answer first, confirm before sending anything (K)
- Daily brief pattern: decisions needed, overdue items, top 3 priorities (borrowed from the Coastal AI CEO agent)
- Alerts you have to acknowledge for bills, birthdays and events (TH)
- Today screen that tracks what you did each day of the week (WB)

### Kids and two homes
- A tile per daughter: school and school emails, sport (days and times), extras, photo of the day, events (S)
- "Days with Dad" calendar in a colour per girl, by month, week or day (S)
- 2-Home mode: who is at which home, handover checklists, gear sightings, neutral co-parenting messages (K)
- 14-day custody and pick-up schedule with a weekly graph (TH)
- Per-child medications, school notes with urgency, and grocery lists (TH)
- Co-parent contacts shown only on the right child's view (TH)
- "Make Money" chores with prerequisites, and wellness tokens with a leaderboard (TH)

### Lisa and family
- Lisa tile: pets (Suki, Rocky, Missy, Molly), Weekly Check-in, photo of the day (S)
- Family mode: kid-safe filter, shared chores and activities (K)
- Profiles with bios and editable photos, including the pets (TH)
- Important People birthdays with card, present and catch-up ticks, and NEON alerts (TH)
- Family fun planner and movie suggestions (TH)
- Jarvey family chatbot (TH)

### Money
- Finance tile: top 5 stock and crypto news, top 5 assets, budget P&L from the spreadsheet, $100K goal bar (S)
- Investment buckets, business buckets, expenses with totals, synced with Lisa (SN)
- Bills tracker with overdue alerts on the home screen (TH)

### Work from home
- WFH mode: deep-work protection, pitch prep, CRM follow-ups, Sydney commute alerts (K)
- StormFX Command Centre stays its own tool; SONIC links to it (SF)
- CEO Hub: a tile per company with its pitch, notes and to-dos (S). Parked with business tools for now.

### Ideas and goals
- Idea Funnel: Draft, Concept, Execute, Live, with title, details, category and budget (S)
- Vision board of up to 10 images in a magazine layout (SN)
- Idea notes stored in the cloud, like Google Keep (SN)
- Priority task list with ticks (LC)

### Mind and body
- Wellbeing tile: meals and recipes, PT workouts for your body type, calorie tracker (S)
- Morning stack, movement blocks, recovery (sauna, cold plunge), breathwork, journal, gratitude, manifesting, sound, night routine, trends (WB)
- ADHD mode: countdowns, transition warnings at 10, 5 and 1 minute, steps of 15 minutes or less, max 3 options, 90-second reset, body doubling (K)

### Advice
- Mentor council: 26 mentors in 6 categories, auto-selected per topic, with discussion, takeaways, action steps, MVP and leaderboard (LP)
- Trophy Case of mentor cards with quotes and "why you need them" (LP)
- Stats dashboard from logged sessions (LP)
- Mentor quotes on the Today screen (WB)

### Fun and downtime
- ESPN-style ticker for NBA, NBL, NBL1 and FIBA scores and breaking news (S)
- Hoops news: top 5 NBA, top 3 Australia, top 2 world (S)
- Watch TV: 10 Play, 9Now, 7Plus, ABC iview, SBS, NBA, ESPN with your logged-in links (S)
- YouTube; top 5 songs, movies and TV; restaurants and bars within 20 km (S)
- Holiday mode: motorhome routes, spicy margaritas, Lakers, Warriors and Kings games in Sydney time (K)
- What's on TV tonight, digital radio, and the "IM BORED FFS" games (TH)
- Broadcast-style design and original team emblems (NBA)

### The assistant itself
- Name SONIC, with an Alfred/Jarvis persona; explains things with basketball analogies and multiple-choice questions (S)
- Real-time voice, a lip-synced avatar, and a digital twin from your photo (K)
- Vibe Coder: a personality prompt box with presets per mode (K)
- Connectors: Google, Notion, Slack, Twilio, Ticketmaster, sports data, TfNSW, maps (K)
- Clean event logging, incident reports and a weekly self-maintenance check (K)
- Multi-step actions with confirmation before anything is sent or bought (K)
- Avatars with moods that match status (AD); a GM agent overseeing the rest (LC)

### Life admin projects
- Project tracker pattern: tasks, risks, budget, run sheet, chat with Claude (MT)

---

## 3. Decisions to make

1. **Name.** SONIC is the assistant's name. Kairo or Orra only matters if you white-label later.
2. **Brain.** The Kairo brief asked for the ChatGPT API, but everything you've built runs on Claude. The spec is model-agnostic, so either works.
3. **Users.** Just you, or you and Lisa from day one? The Snapshot already syncs with Lisa through Supabase.
4. **Voice and avatar.** This is the most expensive part by far. Build it after the hub is useful, starting with an off-the-shelf voice (ElevenLabs) before anything custom.

## 4. Lessons the reference builds already paid for

- **Host it from day one.** iPhones can't open local HTML files, and Google sign-in needs HTTPS. Single HTML files on a desktop dead-ended four times (SONIC, TH, LC, SN).
- **Deploy through GitHub.** Uploading through the Vercel connector broke The Snapshot and the Wellbeing Hub. This repo already deploys cleanly.
- **One source of truth for data.** The StormFX banner bug came from two copies of the same state.
- **Rebuild cleanly instead of stacking patches.** That fixed both Luke's Place and TEAM HARKINS.
- **Keep keys on the server.** Never paste them into chat. `api/chat.js` currently takes the key from the browser and uses an older model id, so both need changing.

## 5. Suggested build order

- **Phase 1, "SONIC Today":** a hosted iPhone app built in this repo, which is already on Vercel with a Claude proxy.
  - Screens: Today brief, Kids and two homes, Money snapshot, Idea Funnel, and a chat with SONIC.
  - Luke's Place moves in as the Council tab.
  - Supabase holds the data so it can be shared with Lisa.
- **Phase 2, modes:** Standard, ADHD, Family, 2-Home, WFH and Holiday as toggles. Merge in the Wellbeing Hub. Add the hoops ticker and TV tiles.
- **Phase 3, voice and personality:** vendor voice first, then the avatar and the Vibe Coder.
- **Phase 4, only if you want to sell it:** white-label (Kairo/Orra) and Your Mentor.
