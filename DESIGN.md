# Design

One idea runs through the site: **the ledger**. Accounting paper, ruled lines, and the
double rule that sits under a total. It's specific to the subject, it's quiet, and it
doesn't look like a SaaS template.

## Palette

| Token        | Hex       | Use |
|--------------|-----------|-----|
| `--paper`    | `#f3efe6` | Page background. Warm, like ledger stock. |
| `--paper-2`  | `#e9e3d6` | The occasional band (statements). |
| `--ink`      | `#1c211f` | Headings, rules, primary button. |
| `--body`     | `#2f332f` | Body copy. |
| `--mute`     | `#64615a` | Labels, secondary text (4.9:1 on paper). |
| `--rule`     | `#cdc4b2` | Hairline rules between rows. |
| `--accent`   | `#9e3a22` | Brick red, used like a red pencil: section numbers, the double underline, focus rings. Never as a fill for large areas. |
| `--deep`     | `#1f2a24` | Footer only. A dark ledger-binding green. |

No blue. No gradients. No shadows.

## Type

- **Newsreader** (variable, optical sizes) for headings, statements and the wordmark. Weight around 400–460;
  big headlines run tight (line-height ~1, negative tracking).
- **IBM Plex Sans** 400/500/600 for body, labels and the form.
- Labels are Plex 500, 12px, uppercase, letter-spaced, preceded by a brick-red section number (`01`).
- Both fonts are self-hosted from `/fonts` (SIL Open Font Licence). Latin subset only.

## Layout

- Left-aligned, asymmetric. Most sections use a 3/8 split: a sticky label in the narrow
  left column, content in the wide right column.
- Rules instead of boxes: a 1px ink rule opens a list, hairlines separate rows, and a
  **3px double rule closes a table or a section**, like the total line in a ledger.
- Corners are square (2px at most). No cards.
- Section layouts vary down a page: contents list with descriptions, a pull statement,
  comparison tables, numbered questions in the margin, a structure diagram, a three-stage
  timeline, an editorial Q&A. Each service page uses a different mix and order.
- Spacing scale: 0.5 / 1 / 1.5 / 2.5 / 4 / 6 rem. Section padding scales with viewport.

## Imagery

None by default. Two optional, config-driven slots in `build.py`: `HEADSHOT` (How it
works and home "who runs this") and nothing else until real Calgary photography exists.
No stock photos, no generated faces, no logos of firms, no reviews.

## Voice

A sharp, slightly dry professional talking to a busy physician or consultant.

- Short sentences. Concrete mechanics: salary vs dividends, retained earnings, year-end,
  passive income inside the corporation, the T2, Represent a Client.
- Say what the service is and isn't. The insurance-broker operator is disclosed plainly,
  even made into an FAQ, rather than buried.
- Banned: unlock, elevate, seamless, tailored solutions, navigate the complexities,
  empower, peace of mind, "top-rated", "vetted", savings promises.
- No specific tax rates. The only thresholds used are long-standing and well known
  ($50,000 passive income, $30,000 GST small-supplier), and they're stated as such.

## Details

- Typographic wordmark: small spaced caps "CALGARY" over "Accountant Match" in Newsreader.
- Favicon: three ledger lines with a brick double rule as the total.
- Minimal sticky header; on mobile a `<details>` menu (no JS).
- Visible focus rings, skip link, accessible labels, 48px form targets.
- Considered 404, print stylesheet, preloaded fonts with metric-matched fallbacks.

Font files are subset to the characters the site uses and pinned to opsz 36, weight 380–460
(~105 KB total). If new copy introduces unusual characters (accents, symbols), re-subset from the
original @fontsource packages or those glyphs will fall back to Georgia/Arial.
