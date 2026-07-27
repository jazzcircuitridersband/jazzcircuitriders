# jazzcircuitriders.com

The band's website. Two files matter:

    index.html    the entire site — styles and scripts are inside it
    shows.json    the only file edited routinely

Hosted free on GitHub Pages. Every commit goes live in about a minute.

## Adding a show

Edit `shows.json`. Nothing else.

```json
{
  "date": "2026-09-14",
  "venue": "The Blue Room",
  "city": "Springfield, IL",
  "time": "9:00 PM",
  "ticketUrl": ""
}
```

- `date` must be `YYYY-MM-DD`
- Leave `ticketUrl` as `""` and the show time displays instead
- Every block needs a comma after it EXCEPT the last one
- Past dates disappear automatically — never delete anything

**Check the live site after editing.** A broken comma makes the site show
backup dates rather than an error. Safe for visitors, easy for us to miss.
