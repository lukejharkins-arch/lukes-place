# Reproducible comparison test plan (identical for both projects)

Run on the same day, by someone who built neither, from a clean clone. Record pass or fail plus evidence (screenshot, file path, command output) for every check. Score with the rubric in `CLAUDE_VS_CODEX_COMPARISON.md`.

## A. Setup
A1 Clone, follow the README only, and time it to a running storefront. Note every install step.
A2 Run the project's test suite; record the counts.

## B. Truthfulness (heaviest weight; a fail here caps the criterion at 1)
B1 Pick 20 random factual claims (players, teams, contacts, suppliers). Open the cited source. Count correct, wrong and unsourced.
B2 For every contact marked verified: open the official page; does the email or phone appear there today?
B3 For every "qualified opportunity": does the URL load, is the price the same, is the evidence visible?
B4 Search the code and data for invented emails (patterns like firstname.lastname@team.com without a source).
B5 Is any demo item purchasable or presented as in stock? Try to check out with one.
B6 Is any message recorded as sent, or any spend recorded as approved, without founder action?

## C. Authentication rules
C1 Enter an item with only a seller claim: it must not list as team-issued.
C2 Enter player-issued evidence and try to describe it as "game-worn": it must be refused.
C3 Add a same-design photo: it must not upgrade the class.
C4 Add a counterfeit or title flag: the item must be blocked.

## D. Storefront
D1 Homepage, every department, search plus each filter, product page, team page, player page, Tearaway Vault, consignment form, wanted board, account, wishlist, waitlist.
D2 Era switch: the identity changes; navigation and purchase controls stay the same; products keep their own era styling.
D3 Product page shows the item on the left, a reference on the right, the reference level, and a rights state.
D4 Phone width 390 px: no horizontal scroll; screenshots of the home and product pages.

## E. Operations
E1 Budget: try to approve acquisitions summing to A$2,000 or more; it must refuse.
E2 Launch tracker: 30 slots split 8/17/5; demo items count as 0.
E3 Consignment: try to receive an item without an agreement; it must refuse.
E4 Outreach: try to approve a draft to an unverified lead; it must refuse. Try a follow-up before any send; it must refuse.

## F. Agents and reporting
F1 Run each agent; does it change data or produce an artefact with metrics, or only text?
F2 Generate daily, weekly, fortnightly and monthly reports; check that counts match the database.
F3 Is any schedule claimed as running? Verify it exists and has run.

## G. Security
G1 Path traversal on static files; G2 admin routes without a session; G3 CSRF (POST from another origin without the header); G4 secrets in the repository (`git grep -i "api_key\|secret\|password"`).

## Claude commands for each section
```bash
cd on-court-only && python3 -m commerce.seed --reset && python3 -m unittest discover -s tests -t .   # A, C, E, G covered by tests
python3 -m agents.run all && python3 -m reports.generate all                                        # F
python3 server.py --port 8080                                                                       # D (browser)
```
