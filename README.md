# Apex ShowMojo QR stickers

6" × 6" QR stickers for the "Schedule a Showing" signs. Each code opens that unit's ShowMojo booking page (`https://showmojo.com/l/<listing id>`). The sign itself carries the compliance language, so the sticker is code only, plus a tiny gray label along the bottom edge (address and ShowMojo id) so stickers never get mixed up.

## What to print

| File | Use |
|---|---|
| `print/<YYYY-MM>.pdf` | Only the stickers added that month. Print this for the monthly batch. |
| `print/all-active.pdf` | Every unit marked `active=yes`. Reprint the full set. |
| `stickers/<address>.pdf` / `.png` | One sticker per unit, for vendors that want one upload per design. PNG is 1800 × 1800 px (300 dpi). |

Every page is exactly 6.00" × 6.00". Print at **Actual size / 100%**, never "Fit to page", and don't let the printer trim into the white border: phones need it to read the code.

## Adding next month's units

1. Add a row per new unit to `units.csv` with that month in `batch` (e.g. `2026-11`).
   - `showmojo_id` is the 10-character id in the listing's link: `showmojo.com/l/`**`46e62a80a6`**. Public list of current listings: <https://showmojo.com/f22f13606a/listings/mapsearch>
   - When a unit leases and its sign comes down, set `active` to `no` (keep the row so its history stays).
2. Run `python3 build.py` (needs `pip install qrcode reportlab pillow`).
3. Commit. `print/<YYYY-MM>.pdf` is the new batch to send to print.

## Where the units came from

Batch `2026-10` (built 21 Oct 2026): the 25 units listed on AppFolio's public listings page (theapexteam.appfolio.com/listings) that day, matched to their ShowMojo listing ids. 23 matched. No ShowMojo link was found for **1211 E 9th St Apt 1** or **1402 E Manlove St Unit 59**; add them when their ids are known.

All 23 codes were checked with two scanner engines (OpenCV and ZXing, the engine behind many phone scanners).
