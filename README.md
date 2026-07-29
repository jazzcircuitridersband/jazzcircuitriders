# jazzcircuitriders.com

The band's website. Hosted free on GitHub Pages — every commit goes live in
about a minute.

**Live:** https://jazzcircuitridersband.github.io/jazzcircuitriders/

```
index.html                    the entire site (styles and scripts are inside it)
shows.json                    the only file edited routinely
test_site.py                  checks the site before it goes out
favicon.svg
.github/workflows/test.yml    runs the checks automatically on every commit
assets/
├── audio/                    MP3s
└── img/                      photos and logo
```

---

## Adding a show

Edit **`shows.json`**. Nothing else.

github.com → this repo → tap `shows.json` → **pencil icon** → edit →
**Commit changes**. Works from a phone.

```json
[
  {
    "date": "2026-09-14",
    "venue": "The Blue Room",
    "city": "Chelsea, MI",
    "time": "9:00 PM",
    "ticketUrl": ""
  }
]
```

- `date` must be `YYYY-MM-DD`
- Leave `ticketUrl` as `""` and the start time shows instead
- Every entry needs a comma after it **except the last one**
- **Past dates disappear on their own.** Never delete anything.

---

## What the site does on its own

**No dates booked?** The Circuit section stays visible and says:

> We're booking now. Confirmed dates appear here. *Get yours on the calendar.*

That's deliberate. An empty calendar isn't an embarrassment — to someone
trying to hire you it reads as availability. Add a date and real listings
replace the message automatically. No code change, nothing to switch on.

**Only uploaded some of the music?** The Listen section checks each MP3 and
removes any track whose file isn't there. Upload two songs, two players
appear. Add three more later and they show up on their own.

**`shows.json` broken?** This is the one to know about. The site does **not**
show an error — it quietly falls back to sample dates and looks completely
normal. Safe for visitors, easy for us to miss. Which is exactly why the
automated check exists.

---

## The automated check

Every commit runs `test_site.py` on GitHub's servers. Look at the **Actions**
tab: green tick means fine, red X means something in that commit would break
the site, and whoever pushed it gets an email.

It checks twelve things, including malformed `shows.json`, images missing
alt text, links with no styling, broken file paths, placeholder text left
visible, and colour contrast.

**If you see a red X**, click into the run and read the failure — it names
the problem in plain language. A stray comma in `shows.json` is by far the
most common cause.

To run it yourself before committing: `python3 test_site.py`

---

## Adding media

**Photos** → `assets/img/`
WebP, under 250KB each. Process at squoosh.app (runs in your browser,
nothing gets uploaded anywhere).

**Music** → `assets/audio/`
MP3 at 192kbps, under 15MB each. Match the loudness across tracks —
Audacity: Effect → Volume and Compression → Loudness Normalization → -14 LUFS.
Filenames must match the `data-src` values in `index.html`.

---

## Please don't

- Rename or move `index.html` — it must stay at the root
- Use `../` in any file path — breaks when served from a subfolder
- Add `{{` or `{%` anywhere — those fail the build and the site 404s
- Upload files while inside a subfolder unless that's where you want them

---

## After any edit

**Open the live site and check.** Thirty seconds now beats a season of
wrong dates.
