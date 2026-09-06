# alu-regex-data-extraction_aubin-karaha

# Regex Onboarding Hackathon

## What's here

A script that reads raw text from a support ticket and pulls out emails,
card numbers, phone numbers, and links after checking whether everything is right.

```
alu-regex-data-extraction_aubin-karaha/
├── input/
│   └── raw-text.txt        (the messy sample text)
├── src/
│   └── main.py               (everything happens here)
├── output/
│   └── sample-output.json    (what you get after running it)
└── README.md

```
 

## Running it

Python 3, nothing else needed (`re` and `json`, are both built in).

Run it from the top folder, or it won't find `input/raw-text.txt`.

## What it pulls out

Emails and card numbers were required. I added phone numbers and links
too, since we were requested at least two extras. Emails from the three
ALU domains (`@alueducation.com`, `@alumni.alueducation.com`,
`@si.alueducation.com`) get tagged as such.

## Regex, briefly

- **email** — just `local@domain.tld`. Anything with
  `@@` or `..` gets rejected afterward.
- **card** — matches 16-digit cards (4-4-4-4) and Amex's 15-digit ones
  (4-6-5), spaces or dashes or nothing between groups.
- **phone** — country code and area code are optional, then three
  chunks of digits. Skips anything under 9 digits. One catch: cards get pulled
  out first, since a long card number can look like a phone number if
  you're not careful.
- **link** — grabs `http(s)://` up to the next space or stray
  quote/bracket.

## Why regex alone isn't enough

Regex only checks if something's shaped right it has no clue if a
card is real. So every match also has to pass a **Luhn checksum**
(same math card issuers use); if it fails, it's left out. Same deal
for emails as broken ones get dropped before they ever reach the output.

## Handling the not-safe stuff

Script tags and SQL injection attempts get caught
by a separate check. They're never saved anywhere.

Cards and emails get masked (only the last 4 digits or first couple
characters show) before anything's printed or saved.

## Known limitations

- Phone matching only really works for the formats in the sample text.
