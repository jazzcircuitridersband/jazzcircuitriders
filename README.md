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
sitemap.xml             update lastmod on real content changes
```

**Machinery — don't delete these**

```
CNAME                   the custom domain. Delete it and the site stops working.
.nojekyll               stops GitHub running the site through Jekyll. Empty on purpose.
test_site.py            checks the site before it goes out
.github/workflows/      runs those checks on every commit
```

Everything except the `assets/` folders must stay at the **root**. `robots.txt`,
`404.html` and `.nojekyll` are only recognised there.

---

## Adding a show

Edit **`shows.json`**. Nothing else.

Tap the file → **pencil icon** → edit → **Commit changes**. Works from a phone.

```json
[
  {
    "date": "2026-01-15",
    "venue": "Venue Name",
    "city": "Town, ST",
    "time": "7:30 – 9:00 PM"
  }
]
```

**Required:** `date`, `venue`, `city`.
**Optional:** `time`, `cover`, `note`, `link`, `linkText`, `venueUrl`.

| Field | What it does |
|---|---|
| `time` | Free text. A start, or a range when the finish matters. |
| `cover` | Shows beside the time. `"$10 suggested"`, `"No cover"`. |
| `note` | A line under the city — a guest player, an unusual detail. |
| `link` | A Facebook event, tickets, anything. |
| `linkText` | The words people click. Defaults to "Details". |
| `venueUrl` | Makes the venue name itself a link. |

Rules that matter:

- Keys are **lowercase**. `date` must be `YYYY-MM-DD`.
- Comma after every entry **except the last one**.
- **Past dates disappear on their own.** Never delete anything.
- **Only confirmed dates go in here.** Un-announcing is worse than announcing late.

---

## Linking to a section

These work as deep links and **must never be renamed** — they're in posts and
printed material, and those links are permanent.

`#listen` · `#circuit` · `#riders` · `#booking`

Content inside a section can be rearranged freely. Only the id is a promise.
`test_site.py` fails the build if one disappears.

---

## What the site does on its own

**No dates booked?** The dates section stays visible and invites booking. That's
deliberate — an empty calendar reads as availability, not inexperience.

**Audio doesn't load until you press play.** Durations show a dash until then.
Loading it up front meant 22MB downloaded by every visitor and a page that took
52 seconds to finish.

**`shows.json` broken?** The site does **not** show an error — it quietly falls
back to sample dates and looks completely normal. Safe for visitors, easy to
miss. That's why the automated check exists.

---

## The automated check

Every commit runs `test_site.py` on GitHub's servers. Look at the **Actions**
tab: green tick means fine, red X means something in that commit would break
the site, and whoever pushed it gets an email.

**A red X does not take the site down.** Pages deploys regardless — the check
tells you, it doesn't stop you.

Click into a failed run and read the failure. It names the problem in plain
language and, for `shows.json`, says exactly what's wrong with which entry.

Run it yourself before committing: `python3 test_site.py`

---

## Adding media

**Photos** → `assets/img/`
WebP, under 250KB. Process at squoosh.app — runs in your browser, nothing gets
uploaded. Generate at about 3× the size it'll be shown at.

**Music** → `assets/audio/`
MP3 at 192kbps, under 15MB. Match loudness across tracks — Audacity: Effect →
Volume and Compression → Loudness Normalization → −14 LUFS. Filenames must
match the `data-src` values in `index.html`.

---

## Please don't

- Rename or move `index.html` — it must stay at the root
- Delete `CNAME` or `.nojekyll`
- Use `../` in any file path — breaks when served from a subfolder
- Add `{{` or `{%` anywhere — those can fail the build

---

## After any edit

**Open the live site and check.** Thirty seconds now beats a season of wrong dates.
