# jazzcircuitriders.com

The band's website. Hosted free on GitHub Pages — every commit goes live in
about a minute.

**Live:** https://jazzcircuitriders.com

---

## What's in here

**The site**

```
index.html              the entire site — styles and scripts are inside it
shows.json              the only file edited routinely
404.html                shown when a URL doesn't exist
assets/audio/           MP3s
assets/img/             photos and logo
```

**Icons**

```
favicon.ico             browser tabs — Safari ignores SVG, so this one matters
favicon.svg             browser tabs everywhere else
apple-touch-icon.png    iOS home screen
manifest.webmanifest    Android home screen
```

**Search engines**

```
robots.txt              tells crawlers what to index
sitemap.xml             lists the page — update lastmod on real content changes
```

**Machinery — don't delete these**

```
CNAME                   the custom domain. Delete it and jazzcircuitriders.com stops working.
.nojekyll               stops GitHub running the site through Jekyll. Empty on purpose.
test_site.py            18 checks, run before every deploy
.github/workflows/      runs those checks automatically on every commit
README.md               this file
```

Everything except the `assets/` folders must stay at the **root**. `robots.txt`,
`404.html` and `.nojekyll` are only recognised there.

---

## Adding a show

Edit **`shows.json`**. Nothing else.

github.com → this repo → tap `shows.json` → **pencil icon** → edit →
**Commit changes**. Works from a phone.

```json
[
  {
    "date": "2026-09-14",
    "venue": "The Valiant Bar & Grill",
    "city": "Chelsea, MI",
    "time": "7:30 PM",
    "venueUrl": "https://thevaliantchelsea.com",
    "link": "https://www.facebook.com/events/123456",
    "linkText": "Details"
  }
]
```

- Required: `date`, `venue`, `city`. Optional: `time`, `link`, `linkText`.
- Keys are **lowercase**. `date` must be `YYYY-MM-DD`.
- **`link` is for whatever suits the night** — a Facebook event, the venue's
  page, a ticket seller. Most gigs won't need one.
- `linkText` is the words people click. Leave it out and it says "Details".
- `venueUrl` makes the **venue name** itself a link — use it for the venue's
  own page, and keep `link` for the Facebook event or tickets. Two links, no
  extra clutter, because the venue name is already on screen.
- The time always shows, with or without a link.
- Every entry needs a comma after it **except the last one**
- **Past dates disappear on their own.** Never delete anything.

---

## What the site does on its own

**No dates booked?** The Circuit section stays visible and says:

> We're booking now. Confirmed dates appear here. *Get yours on the calendar.*

That's deliberate. An empty calendar isn't an embarrassment — to someone
trying to hire you it reads as availability. Add a date and real listings
replace the message automatically.

**Audio doesn't load until you press play.** Track durations show a dash until
then. This is on purpose: loading five MP3s up front meant 22 MB downloaded by
every visitor, and the page took 52 seconds to finish. Now nothing is fetched
until someone asks to hear something.

**`shows.json` broken?** The site does **not** show an error — it quietly falls
back to sample dates and looks completely normal. Safe for visitors, easy for
us to miss. That's exactly why the automated check exists.

---

## The automated check

Every commit runs `test_site.py` on GitHub's servers. Look at the **Actions**
tab: green tick means fine, red X means something in that commit would break
the site, and whoever pushed it gets an email.

It checks 18 things — malformed `shows.json`, images missing alt text, links
with no styling, broken file paths, placeholder text left visible, colour
contrast, image dimensions that don't match the real files, and audio being
loaded too early.

**If you see a red X**, click into the run and read the failure. It names the
problem in plain language and, for `shows.json`, tells you exactly what's wrong
with which entry.

Run it yourself before committing: `python3 test_site.py`

**A red X does not take the site down.** Pages deploys regardless — the check
is there to tell you, not to stop you.

---

## Adding media

**Photos** → `assets/img/`
WebP, under 250KB each. Process at squoosh.app — it runs in your browser and
nothing gets uploaded anywhere. Generate at about 3× the size it'll be shown at.

**Music** → `assets/audio/`
MP3 at 192kbps, under 15MB each. Match loudness across tracks — Audacity:
Effect → Volume and Compression → Loudness Normalization → −14 LUFS.
Filenames must match the `data-src` values in `index.html`.

---

## Please don't

- Rename or move `index.html` — it must stay at the root
- Delete `CNAME` or `.nojekyll`
- Use `../` in any file path — breaks when served from a subfolder
- Add `{{` or `{%` anywhere — those can fail the build
- Upload files while inside a subfolder unless that's where you want them

---

## After any edit

**Open the live site and check.** Thirty seconds now beats a season of
wrong dates.
