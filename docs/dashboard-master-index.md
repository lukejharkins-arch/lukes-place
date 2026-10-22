# Dashboard Master Index

Single source of truth for every dashboard, command centre and dashboard business idea in Luke's Claude history.

- **Compiled:** 22 October 2026
- **Sources searched:** claude.ai export (75 chats, 20 projects, all memory files, artifact data), 8 published artifacts, 6 Claude Code sessions, the `lukes-place` repo
- **Not searched:** ChatGPT (excluded by request); Notion, Google Drive and Gmail (not Claude sources; available on request)
- **Status:** DRAFT. Nothing gets filed or archived until Luke confirms this list is complete.

> **Direction (22 Oct):**
> - **Focus:** C1 SONIC, C2 Luke's Place and P3 Kairo, merged in `life-assistant-blueprint.md`.
> - **Reference:** C3 to C9, M2, M3 and M5.
> - **Later:** P1, P2, P4, P6, P7, M1 and M4, kept separate in `business-tools-later.md`. This replaces the scoring in section 4 for now.

---

## 0. Security first

Four live credentials were pasted into chats. Treat them as exposed and revoke them, even if they no longer work:

| Credential | Chat | Date |
|---|---|---|
| Anthropic API key | Multi-agent AI mentor simulation system | 1 Apr 2026 |
| Anthropic API key | Storm Dashboard Creator - Command Centre - RETIRED | 24 Jun 2026 |
| GitHub personal access token | Storm Dashboard Creator - Command Centre - RETIRED | 8 Jul 2026 |
| Vercel token | All-in-one wellbeing journey platform | 25 Jul 2026 |

Revoke at console.anthropic.com (API keys), github.com/settings/tokens and vercel.com/account/tokens. The values are not repeated here.

---

## 1. The register

21 items in three groups. Status key: **Idea** (talked about), **Spec** (written plan), **Built** (working file or app), **Live** (in use), **Stuck** (built but broken or blocked).

### A. Products to sell (dashboard business ideas)

| ID | Name | What it is | Status | Where it lives |
|---|---|---|---|---|
| P1 | **SME Agent Command Center** | Dashboard where local small businesses switch on ready-made AI agents for booking, social media and customer routing. Verticals: plumber, hair salon, real estate, retail. Spec v1.2: 10 sections, Phase 1 (38 tickets, 171 points) and Phase 2 (24 tickets, 115 points). Clickable prototype with 11 screens and 4 example businesses. Written for the US market (ZIP codes, 911, A2P 10DLC, Fair Housing), so it needs Australian localisation. | Spec + prototype | Claude Code session "SME Agent Command Center architecture" (15 Oct, archived). Artifacts: [Spec](https://claude.ai/artifact/Bd4SR3jc6B4VQ67NATAaFJ), [Prototype](https://claude.ai/artifact/28Ncbx9LUAm13DQqgJ7rnM) |
| P2 | **CoastBase** | Coastal AI's white-label GoHighLevel platform: CRM, pipelines, automations, bookings, reviews and a reporting dashboard. "One login, one dashboard, one monthly fee." From $297/month plus setup. Started as the 29 Apr request for "a white label tool to manage this business and other people's businesses"; named 6 Jul. Rule: never name GoHighLevel publicly. | Spec (priced, account not set up) | Chats: Launching AI Strategy Audits business in 20 days; Central Coast SME AI consultant business plan. Projects: Coastal AI Consulting Folder, CEO - COASTAL AI CONSULTING |
| P3 | **Kairo** (working name) | White-label personal assistant with real-time voice, a lip-synced avatar and six modes: Standard, ADHD, Family, 2-Home, WFH, Holiday. The grown-up version of SONIC. Names explored: Kairo, Twinly, Wingmate, then Tandem, Ferry, Orra (Orra recommended). Scaffold built (landing, demo, Vibe Coder, 28-table Postgres schema, paywall, 13 tests) but "committed locally" in a session with no GitHub repo, so the code may be gone. | Spec + partial build (at risk) | Claude Code session "Personal Assistant Avatar platform" (15 Oct). Artifact: [Kairo Platform Architecture](https://claude.ai/artifact/7ptfGt4ZcfXyUrXmpMCUAy) |
| P4 | **Your Room / Your Mentor** | White-label version of Luke's Place. Anyone picks from the top 500 influencers per category, sport-first (NRL, NBA, NFL, cricket). Freemium plus premium, revenue-share licensing, aimed at consumers and creators. Needs an admin command centre: add, remove and update influencer profiles, manage white-label client accounts, analytics across every Room, push content updates. Renamed "Your Mentor" on 24 Jul. Risk: real people's names and likeness as AI personas need permission. | Idea (scoped) | Chat: Multi-agent AI mentor simulation system (24 Mar, 24 Jul) |
| P5 | **White-label Personal Dashboard** | "Personal Dashboard to manage your busy universe", listed in the Pacific Adrenalin product line-up on 11 Mar, with a note to write a separate prompt for a white-label copy of SONIC. Now covered by P3. | Idea (merged into P3) | Chat: Building a personal AI command centre |
| P6 | **Client reporting dashboard (Evolute)** | Monthly automated client report showing content published and search visibility (Looker Studio with Search Console and GA4), plus "investigate Go High Level white label to offer clients their own dashboard". | Idea (in roadmap) | Chat: Strategic direction and go-to-market roadmap (9 Apr). Project: Evolute Technology |
| P7 | **"AI dashboards" as a later Coastal AI product** | The business plan clean-up lists subscription products and AI-powered dashboards as long-term growth, with an explicit "Do not build that yet". This conflicts with building P1 now and needs a decision. | Parked on purpose | Chat: Business plan cleanup and strategic direction (27 May) |

### B. Your own command centres (built for you, Lisa, family or work)

| ID | Name | What it is | Status | Where it lives |
|---|---|---|---|---|
| C1 | **SONIC Personal AI Command Centre** | Alfred/Jarvis-style personal dashboard, V5 single HTML file. Google sign-in for Calendar, Tasks, Gmail and Photos; 7 TV channel tiles with editable links; hoops news; idea funnel; NBA broadcast styling; local info for 2256. | Built (V5), never confirmed live. Google sign-in needs it hosted on Vercel. | Chat: Building a personal AI command centre (11 Mar to 9 Apr) |
| C2 | **Luke's Place** | AI mentor council: 26 mentors, Council, Dashboard and Trophy Case tabs, auto-selection, leaderboard, Simpsons-style portraits. You also asked for a version merged into SONIC. | Built, deployed from this repo (`lukes-place.html`, `api/chat.js`, `vercel.json`) | Chat: Multi-agent AI mentor simulation system. GitHub: lukejharkins-arch/lukes-place |
| C3 | **StormFX Command Centre** | Work renewals dashboard, 17 script blocks: renewal tracker with 31-day and 6-week alerts, open quotes, win-back list, past renewals, GP and revenue charts, vendor pricing (Autodesk June CPQ 137 products, Chaos, McNeel, Twinmotion, Pico and Meta stock), time zone and currency converters, margin calculator, Buddy AI assistant, GitHub Gist save and restore, renewal email templates. | Live (daily work tool). Last worked on 17 Jul. | Chats: Storm Dashboard Creator - Command Centre - RETIRED; StormFX Command Centre development. Projects: STORM FX - Command Centre ("Dex"), Storm FX |
| C4 | **TEAM HARKINS Family Command Centre** | Family dashboard v3: profiles (including the four pets), 14-day custody and pick-up schedule, birthdays with NEON alerts, bills, groceries, "Make Money" chores, games, wellness tokens, Jarvey chatbot, weather, local news. | Built (v3, 5 Jun). No hosting noted. | Chat: Team Harkins Command Centre. Project: Family |
| C5 | **LL Collective Command Centre** (June build) | Umbrella view of 10 ventures: El Capitan GM agent tile plus 9 agent tiles, Mango Lagoon revenue tile with a pokies slot machine and fireworks, priority tasks with ticks. Beach and tequila styling. | Built (last change 4 Jul) | Chat: LL COLLECTIVE DASHBOARD (21 Jun to 14 Jul). Project: LL Collective |
| C6 | **LL Collective Dashboard "The Snapshot"** (July build) | iPhone app for you and Lisa: investment buckets, business buckets, expenses, vision board, idea notes, Supabase sync, ADHD-friendly animations, "Baller Life" splash. | Stuck. Deployed to ll-collective-dashboard.vercel.app, which returned 404 on 27 Jul. A later chat used llcollective.vercel.app, also 404. | Chats: Investment portfolio allocation framework; App deployment in portfolio allocation. Project: Investment Dashboard - LL Collective |
| C7 | **Agent Dashboard** | Monitor your AI agents: status, progress, cost and tokens, logs, task queue. v3 has 12 industry avatar costumes, an edit form and a link button per agent. | Built (v3). Missing: saving and an add-agent button. | Chat: Agent progress tracking dashboard. Project: Agent Dashboard |
| C8 | **NBA Playoffs Dashboard** (concept) | React concept with a broadcast and editorial look, 16 original SVG team emblems, live scoreboard hero and score ticker. Built to connect to live data later. Also listed in the Basketball register. | Built (concept) | Chat: Basketball - Building a visual concept from scratch NBA Dashboard. Project: Dashboard Prompt Work |
| C9 | **Luke's Wellbeing Hub** (borderline) | Personal wellness app with 13 sections including Today and Trends. Next.js and Supabase. More a tracker app than a command centre. | Stuck (main page file never uploaded) | Chats: All-in-one wellbeing journey platform and 2 deployment chats. Project: Wellness App |

### C. Modules and planned add-ons

| ID | Name | What it is | Status | Where it lives |
|---|---|---|---|---|
| M1 | **Chaos Renewal Agent** | NetSuite renewal agent planned as a new StormFX Command Centre section. Architecture choice still open; a guided playbook first was recommended. | Spec (decision pending) | Chat: Chaos renewal agent for NetSuite automation (6 May) |
| M2 | **Email generator** | AI email writer using the Storm FX template library, added to the Command Centre. | Built, merged into C3 | Chat: Email writing tool - COMMUNICATION (9 Apr) |
| M3 | **Move Tracker** | Tasks, risks, budget, move-day run sheet and a Claude chat panel, meant to drop into The Snapshot. | Stuck (waiting on C6's real URL) | Chat: Luke & Lisa's move to Ettalong. Project: Moving House |
| M4 | **Coastal AI agent command centre** | The CEO agent (Beacon, competing with Jasper) acting as a command centre: daily brief (decisions, overdue, leads, delivery, finance, top 3), departments tracked Green, Amber or Red. "No persistent task tracking tool selected" is an open blocker. | Process only, no dashboard built | Chat: CEO - Coastal AI Consulting (Silus) and the agent chats. Project: CEO - COASTAL AI CONSULTING |
| M5 | **Notion life and business command centre** | Set as a priority with Lisa on 8 Apr. Memory says Notion is your "central life/business command centre, in progress". The TeqDreams Kanban board also lives there. | Unknown from Claude data | Chats: Luke's personal information; Using Claude on mobile without installation. Lives in Notion. |

---

## 2. Where ideas overlap

1. **The personal assistant line:** SONIC (Mar) became Luke's Place (merge request), then the White-label Personal Dashboard (P5), then Kairo (Oct). One idea under four names.
2. **The LL Collective line:** Notion TeqDreams, then the June Command Centre (C5), then The Snapshot (C6), then the Move Tracker (M3). There are two separate builds both called "LL Collective Dashboard", two URLs, and both are broken.
3. **The agent line:** Agent Dashboard (C7), El Capitan tiles (C5), Coastal AI departments (M4) and SME Agent Command Center (P1) all use the same pattern: agents, status, tasks, handoffs.
4. **The small-business product line:** a white-label management tool (Apr), then CoastBase (Jul), then the Evolute client dashboard (P6), then SME Agent Command Center (Oct). This is the buy-it (GoHighLevel) versus build-it decision.

## 3. Loose ends and risks

- Kairo code may only exist in a container that has since been reclaimed. Only the spec artifact is safe.
- The SME Agent Command Center spec assumes the US market. The first Coastal AI test clients are a local hair salon and Concrete Jungle Strength Co., not a plumber.
- The Snapshot is broken at both URLs, and the Move Tracker is waiting on it.
- The Agent Dashboard has no saving.
- The Wellbeing Hub deployment is unfinished.
- The Coastal AI audit price is still not locked ($395 is the only confirmed figure), which blocks selling CoastBase.
- The 27 May plan said not to build dashboards yet. Either confirm that still stands, or replace it.
- An empty "Dashboard" artifact was created on 22 Oct ([link](https://claude.ai/artifact/JVeB4M8dPRSnCTkwBwKbLz)). It can be deleted once you confirm.

## 4. First read on the best option (to work through together)

Scored 1 to 5 against your known goals: revenue within 90 days, solo build with AI, recurring income, fit with Coastal AI as the lead business, and low risk.

| Option | Speed to revenue | Build effort (5 = light) | Recurring | Fit with Coastal AI | Low risk | Total |
|---|---|---|---|---|---|---|
| P2 CoastBase | 5 | 5 | 4 | 5 | 4 | **23** |
| P6 Client reporting dashboard | 4 | 4 | 3 | 3 | 4 | 18 |
| P1 SME Agent Command Center | 2 | 2 | 5 | 5 | 3 | 17 |
| P3 Kairo / Orra | 1 | 1 | 4 | 2 | 2 | 10 |
| P4 Your Mentor | 2 | 2 | 3 | 1 | 1 | 9 |

**Suggested path:** sell CoastBase to the first 3 to 5 audit clients now. Then build SME Agent Command Center Phase 1 on top of what those clients actually use, starting with hair salons (your real test client) rather than plumbing, and localised for Australia. Park Kairo and Your Mentor. Stop starting new personal dashboards: keep StormFX running and merge the LL Collective builds into one.

## 5. Filing plan (only after sign-off)

1. Luke confirms this index is complete.
2. Create one Claude Project: **Dashboards & Command Centres**. Upload this file as project knowledge. Set instructions: Australian English, no long dashes, this index is the source of truth.
3. Move these 12 core chats into it:
   - Building a personal AI command centre (11 Mar)
   - Multi-agent AI mentor simulation system (24 Mar)
   - Storm Dashboard Creator - Command Centre - RETIRED (2 Apr)
   - Email writing tool - COMMUNICATION (9 Apr)
   - Basketball - Building a visual concept from scratch NBA Dashboard (27 Apr)
   - Chaos renewal agent for NetSuite automation (6 May)
   - Team Harkins Command Centre (27 May)
   - LL COLLECTIVE DASHBOARD (21 Jun)
   - StormFX Command Centre development (9 Jul)
   - Agent progress tracking dashboard (21 Jul)
   - Investment portfolio allocation framework (23 Jul)
   - App deployment in portfolio allocation (23 Jul)
4. Your call: Luke & Lisa's move to Ettalong (M3), and the 3 Wellbeing Hub chats (C9).
5. Leave in place. These only mention dashboards, and the key points are captured above: Luke's personal information, Organizing Google folder structure, Using Claude on mobile without installation, Launching AI Strategy Audits business in 20 days, Building a road trip game for iPhone, Presentations, Central Coast SME AI consultant business plan, Gmail Work, Strategic direction and go-to-market roadmap, Business plan cleanup and strategic direction, CEO - Coastal AI Consulting (Silus).
6. Fold these dashboard-only projects in, then delete them once empty: Dashboard Prompt Work, Agent Dashboard, Investment Dashboard - LL Collective, Family. STORM FX - Command Centre is a decision for Luke (see questions).
7. Claude Code sessions and artifacts can't go into a claude.ai Project. They stay linked from this index.
