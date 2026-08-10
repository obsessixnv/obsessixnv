#!/usr/bin/env python3
"""Render the README's Codex cards from the GitHub API.

The public github-readme-stats instances are volunteer Vercel deploys sharing a
single rate-limited token; they go down, and they answer HTTP 200 with an error
card when they do. These cards are generated here instead, so the README depends
on nothing but GitHub itself.

Usage:  GH_TOKEN=<token> python3 scripts/render_cards.py [--user LOGIN] [--out DIR]

Writes assets/{stats,langs,streak,activity}.svg. Nothing is written unless every
card renders, so a failed run can never leave a half-broken card behind.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from xml.sax.saxutils import escape

API = "https://api.github.com/graphql"

# --- Baroque chiaroscuro palette, shared with assets/header.svg ---------------
INK_BRIGHT = "#f0e4c8"   # cream, hero numbers
INK = "#bda06e"          # muted gold, labels
INK_DIM = "#8a7350"      # faint gold, axis ticks
GOLD = "#b8860b"         # titles
GOLD_HI = "#e7c469"      # gilt highlight
OXBLOOD = "#a8412a"      # accent
GROUND = "#14100a"       # card surface (opaque: identical in GitHub light+dark)
GRID = "#3a2c18"

# Sequential ramp, gold -> oxblood. Validated: monotonic lightness, every step
# >= 3:1 on GROUND. Adjacent pairs sit in the 6-8 dE band, which is legal only
# with secondary encoding -- hence the direct label + 2px gap on every segment.
RAMP = ["#f5e0a0", "#e2c076", "#d0a154", "#be833f", "#ad6538", "#9c4a33"]
RAMP_OTHER = "#6f6555"

SERIF = "Georgia, 'Times New Roman', serif"


# --- data --------------------------------------------------------------------

def gql(token: str, query: str, variables: dict) -> dict:
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "obsessixnv-readme-cards",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(f"GraphQL: {payload['errors']}")
    return payload["data"]


PROFILE_Q = """
query($login:String!) {
  user(login:$login) {
    name login createdAt
    followers { totalCount }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false,
                 orderBy:{field:STARGAZERS, direction:DESC}) {
      totalCount
      nodes {
        stargazerCount
        languages(first:10, orderBy:{field:SIZE, direction:DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""

YEAR_Q = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    contributionsCollection(from:$from, to:$to) {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch(token: str, login: str) -> dict:
    prof = gql(token, PROFILE_Q, {"login": login})["user"]
    if prof is None:
        raise RuntimeError(f"no such user: {login}")

    created = dt.datetime.strptime(prof["createdAt"], "%Y-%m-%dT%H:%M:%SZ")
    today = dt.datetime.utcnow()

    days: dict[str, int] = {}
    commits = prs = issues = 0
    # contributionsCollection covers at most one year per call
    year = created.year
    while year <= today.year:
        frm = max(created, dt.datetime(year, 1, 1))
        to = min(today, dt.datetime(year, 12, 31, 23, 59, 59))
        if frm > to:
            year += 1
            continue
        c = gql(token, YEAR_Q, {
            "login": login,
            "from": frm.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to": to.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]
        prs += c["totalPullRequestContributions"]
        issues += c["totalIssueContributions"]
        for w in c["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
        year += 1

    if not days:
        raise RuntimeError("no contribution data returned")

    langs: dict[str, int] = {}
    stars = 0
    for repo in prof["repositories"]["nodes"]:
        stars += repo["stargazerCount"]
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]

    return {
        "name": prof["name"] or prof["login"],
        "login": prof["login"],
        "followers": prof["followers"]["totalCount"],
        "repos": prof["repositories"]["totalCount"],
        "stars": stars,
        "commits": commits,
        "prs": prs,
        "issues": issues,
        "langs": langs,
        "days": days,
    }


def streaks(days: dict[str, int]) -> dict:
    """Current and longest run of consecutive contributing days."""
    ordered = sorted(days)
    best = cur = 0
    best_span = cur_span = (None, None)
    for d in ordered:
        if days[d] > 0:
            cur += 1
            cur_span = (cur_span[0] or d, d)
            if cur > best:
                best, best_span = cur, cur_span
        else:
            cur, cur_span = 0, (None, None)
    # today with no commits yet does not break a streak that ran through yesterday
    today = dt.datetime.utcnow().date().isoformat()
    if ordered and ordered[-1] == today and days[today] == 0:
        tail = ordered[:-1]
        run, span = 0, (None, None)
        for d in reversed(tail):
            if days[d] > 0:
                run += 1
                span = (d, span[1] or d)
            else:
                break
        cur, cur_span = run, span
    return {
        "total": sum(days.values()),
        "current": cur, "current_span": cur_span,
        "longest": best, "longest_span": best_span,
        "since": ordered[0],
    }


def rank(d: dict) -> tuple[str, float]:
    """github-readme-stats' published rank formula, reproduced.

    Returns (grade, percentile). Lower percentile is better, so the ring is
    drawn from (100 - percentile) -- it encodes the value rather than a
    hardcoded arc.
    """
    def exp_cdf(x): return 1 - 2 ** -x
    def log_cdf(x): return x / (1 + x)
    weights = [
        (2, exp_cdf, d["commits"] / 1000),
        (1, exp_cdf, d["issues"] / 25),
        (4, log_cdf, d["stars"] / 50),
        (3, log_cdf, d["prs"] / 50),
        (1, log_cdf, d["followers"] / 10),
    ]
    total = sum(w for w, _, _ in weights)
    pct = (1 - sum(w * f(x) for w, f, x in weights) / total) * 100
    for threshold, level in zip(
        [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100],
        ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"],
    ):
        if pct <= threshold:
            return level, pct
    return "C", pct


def human(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}m".replace(".0m", "m")
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


# --- drawing -----------------------------------------------------------------

def frame(w: int, h: int, title: str, body: str, uid: str) -> str:
    """A card on its own opaque ground, so it reads the same in either GitHub theme."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">
  <title>{escape(title)}</title>
  <defs>
    <radialGradient id="g{uid}" cx="28%" cy="22%" r="92%">
      <stop offset="0%" stop-color="#2a1e11"/><stop offset="60%" stop-color="{GROUND}"/>
      <stop offset="100%" stop-color="#0b0807"/>
    </radialGradient>
    <linearGradient id="b{uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{GOLD_HI}"/><stop offset="55%" stop-color="#8a6a1e"/>
      <stop offset="100%" stop-color="#3d2b09"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" rx="7" fill="url(#g{uid})"/>
  <rect x="1.1" y="1.1" width="{w-2.2}" height="{h-2.2}" rx="6" fill="none"
        stroke="url(#b{uid})" stroke-width="2.2"/>
  <text x="20" y="31" font-family="{SERIF}" font-size="15" font-weight="700"
        letter-spacing="2.6" fill="{GOLD}">{escape(title.upper())}</text>
  <path d="M20 40 H {w-20}" stroke="{GOLD}" stroke-width="1" stroke-dasharray="1.5 5" opacity="0.55"/>
{body}
</svg>
"""


def card_stats(d: dict) -> str:
    rows = [
        ("Total Stars", human(d["stars"])),
        ("Total Commits", human(d["commits"])),
        ("Total PRs", human(d["prs"])),
        ("Total Issues", human(d["issues"])),
        ("Repositories", human(d["repos"])),
    ]
    out = []
    y = 68
    for label, value in rows:
        out.append(
            f'  <text x="24" y="{y}" font-family="{SERIF}" font-size="13.5" fill="{INK}">{escape(label)}</text>'
            f'<text x="215" y="{y}" font-family="{SERIF}" font-size="13.5" font-weight="700"'
            f' text-anchor="end" fill="{INK_BRIGHT}">{escape(value)}</text>'
        )
        y += 25
    grade, pct = rank(d)
    circumference = 2 * 3.141592653589793 * 43
    filled = circumference * max(0.0, min(1.0, (100 - pct) / 100))
    out.append(f"""  <circle cx="345" cy="118" r="43" fill="none" stroke="{GOLD}" stroke-width="5" opacity="0.22"/>
  <circle cx="345" cy="118" r="43" fill="none" stroke="{GOLD_HI}" stroke-width="5"
          stroke-linecap="round" stroke-dasharray="{filled:.1f} {circumference:.1f}"
          transform="rotate(-90 345 118)"/>
  <text x="345" y="127" font-family="{SERIF}" font-size="30" font-weight="700"
        text-anchor="middle" fill="{INK_BRIGHT}">{grade}</text>""")
    return frame(430, 200, f"{d['name']} · the codex", "\n".join(out), "s")


def card_langs(d: dict) -> str:
    total = sum(d["langs"].values()) or 1
    top = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:6]
    shown = sum(v for _, v in top)
    items = [(k, v / total * 100) for k, v in top]
    if total - shown > 0:
        items.append(("Other", (total - shown) / total * 100))

    out = []
    # stacked share bar; 2px surface gaps keep adjacent ramp steps apart
    x, bar_y, bar_w = 24, 58, 332
    for i, (_, pct) in enumerate(items):
        seg = max(pct / 100 * bar_w - 2, 1.5)
        colour = RAMP[i] if i < len(RAMP) else RAMP_OTHER
        out.append(f'  <rect x="{x:.1f}" y="{bar_y}" width="{seg:.1f}" height="11" rx="2.5" fill="{colour}"/>')
        x += seg + 2

    # every segment is direct-labelled: identity never rests on colour alone
    ly = 92
    for i, (name, pct) in enumerate(items):
        col = 24 if i % 2 == 0 else 196
        colour = RAMP[i] if i < len(RAMP) else RAMP_OTHER
        out.append(
            f'  <circle cx="{col+5}" cy="{ly-4}" r="4.6" fill="{colour}"/>'
            f'<text x="{col+17}" y="{ly}" font-family="{SERIF}" font-size="12.5" fill="{INK}">'
            f'{escape(name)} <tspan fill="{INK_BRIGHT}" font-weight="700">{pct:.1f}%</tspan></text>'
        )
        if i % 2 == 1:
            ly += 22
    return frame(380, 200, "most used languages", "\n".join(out), "l")


def card_streak(s: dict) -> str:
    def pretty(iso: str | None) -> str:
        if not iso:
            return ""
        return dt.datetime.strptime(iso, "%Y-%m-%d").strftime("%b %-d, %Y")

    cur_lo, cur_hi = s["current_span"]
    lon_lo, lon_hi = s["longest_span"]
    cells = [
        (140, human(s["total"]), "Total Contributions", f'{pretty(s["since"])} — Present'),
        (430, str(s["current"]), "Current Streak",
         f'{pretty(cur_lo)} — {pretty(cur_hi)}' if cur_lo else "—"),
        (720, str(s["longest"]), "Longest Streak",
         f'{pretty(lon_lo)} — {pretty(lon_hi)}' if lon_lo else "—"),
    ]
    out = []
    for i, (cx, big, label, sub) in enumerate(cells):
        if i == 1:
            # decorative ring: a complete circle, so it never implies a value it isn't carrying
            out.append(f'  <circle cx="{cx}" cy="98" r="46" fill="none" stroke="{GOLD}" stroke-width="4" opacity="0.25"/>')
            out.append(f'  <circle cx="{cx}" cy="98" r="46" fill="none" stroke="{GOLD_HI}" stroke-width="4" opacity="0.85"/>')
        out.append(f'  <text x="{cx}" y="{106 if i==1 else 102}" font-family="{SERIF}" font-size="{34 if i==1 else 40}"'
                   f' font-weight="700" text-anchor="middle" fill="{INK_BRIGHT}">{escape(big)}</text>')
        out.append(f'  <text x="{cx}" y="{158 if i==1 else 132}" font-family="{SERIF}" font-size="13"'
                   f' letter-spacing="1.6" text-anchor="middle" fill="{GOLD}">{escape(label)}</text>')
        out.append(f'  <text x="{cx}" y="{176 if i==1 else 152}" font-family="{SERIF}" font-size="11"'
                   f' text-anchor="middle" fill="{INK_DIM}">{escape(sub)}</text>')
    for x in (285, 575):
        out.append(f'  <path d="M{x} 62 V 152" stroke="{GOLD}" stroke-width="1" opacity="0.3"/>')
    return frame(860, 200, "the reckoning", "\n".join(out), "k")


def card_activity(days: dict[str, int], n: int = 30) -> str:
    ordered = sorted(days)[-n:]
    vals = [days[d] for d in ordered]
    peak = max(vals) if vals else 0
    scale_top = max(peak, 1)

    x0, x1, y0, y1 = 56, 866, 74, 214
    def px(i): return x0 + (x1 - x0) * (i / max(len(vals) - 1, 1))
    def py(v): return y1 - (y1 - y0) * (v / scale_top)

    out = []
    # recessive gridlines + y ticks
    for f in (0, 0.5, 1):
        v = scale_top * f
        y = py(v)
        out.append(f'  <path d="M{x0} {y:.1f} H {x1}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'  <text x="{x0-9}" y="{y+4:.1f}" font-family="{SERIF}" font-size="10.5"'
                   f' text-anchor="end" fill="{INK_DIM}">{int(round(v))}</text>')

    pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(vals))
    out.append(f'  <polygon points="{x0},{y1} {pts} {x1},{y1}" fill="{GOLD_HI}" opacity="0.13"/>')
    out.append(f'  <polyline points="{pts}" fill="none" stroke="{GOLD_HI}" stroke-width="2"'
               f' stroke-linejoin="round" stroke-linecap="round"/>')

    # selective direct label: the peak day only, never a number on every point
    if peak > 0:
        pi = vals.index(peak)
        out.append(f'  <circle cx="{px(pi):.1f}" cy="{py(peak):.1f}" r="4" fill="{OXBLOOD}"'
                   f' stroke="{GROUND}" stroke-width="2"/>')
        anchor = "end" if pi > len(vals) * 0.85 else ("start" if pi < len(vals) * 0.15 else "middle")
        out.append(f'  <text x="{px(pi):.1f}" y="{py(peak)-11:.1f}" font-family="{SERIF}" font-size="11.5"'
                   f' font-weight="700" text-anchor="{anchor}" fill="{INK_BRIGHT}">{peak}</text>')

    step = max(len(ordered) // 6, 1)
    for i in range(0, len(ordered), step):
        label = dt.datetime.strptime(ordered[i], "%Y-%m-%d").strftime("%-d %b")
        out.append(f'  <text x="{px(i):.1f}" y="{y1+18:.1f}" font-family="{SERIF}" font-size="10.5"'
                   f' text-anchor="middle" fill="{INK_DIM}">{label}</text>')

    out.append(f'  <text x="{(x0+x1)/2:.0f}" y="56" font-family="{SERIF}" font-size="12.5"'
               f' font-style="italic" text-anchor="middle" fill="{INK}">'
               f'Nulla dies sine linea — contributions, last {len(vals)} days</text>')
    return frame(900, 250, "the daily line", "\n".join(out), "a")


# --- entry -------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="obsessixnv")
    ap.add_argument("--out", default="assets")
    args = ap.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("error: set GH_TOKEN (or GITHUB_TOKEN)", file=sys.stderr)
        return 2

    try:
        data = fetch(token, args.user)
    except (urllib.error.URLError, RuntimeError, KeyError, TimeoutError) as e:
        print(f"error: could not fetch GitHub data: {e}", file=sys.stderr)
        return 1

    s = streaks(data["days"])
    # render everything before writing anything: a partial failure must not
    # leave one fresh card beside three stale ones
    cards = {
        "stats.svg": card_stats(data),
        "langs.svg": card_langs(data),
        "streak.svg": card_streak(s),
        "activity.svg": card_activity(data["days"]),
    }
    os.makedirs(args.out, exist_ok=True)
    for name, svg in cards.items():
        with open(os.path.join(args.out, name), "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"wrote {args.out}/{name}")

    print(f"  stars={data['stars']} commits={data['commits']} prs={data['prs']} "
          f"issues={data['issues']} rank={rank(data)[0]} "
          f"streak={s['current']} longest={s['longest']} total={s['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
