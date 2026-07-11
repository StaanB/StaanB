#!/usr/bin/env python3
"""Generates assets/terminal.svg: a terminal-window styled card with
static specs plus live GitHub stats, matching the portfolio's palette.

Run with GITHUB_TOKEN and USERNAME env vars set (as in the workflow).
"""
import html
import json
import os
import urllib.request

USERNAME = os.environ.get("USERNAME", "StaanB")
TOKEN = os.environ["GITHUB_TOKEN"]

BG = "#0A0908"
TITLEBAR = "#1C1712"
INK = "#F2ECE3"
MUTED = "#5A5347"
ACCENT = "#FF6B1A"
BORDER = "#2A241C"

SPECS = [
    ("Role", "Full Stack Dev (AI-first)"),
    ("Coding since", "2021"),
    ("Host", "Prolog App"),
    ("IDE", "VSCode"),
    ("Lang.Prog", "JavaScript, TypeScript, Ruby, Java"),
    ("Lang.Frame", "React, Next.js, Node.js, NestJS, Rails, Flutter"),
    ("Lang.Real", "Português (nativo), Inglês, Japonês (básico)"),
    ("Hobbies", "Animes, jogos, futebol"),
    ("Portfolio", "portfolio-stanley-delta.vercel.app"),
    ("Contact", "LinkedIn · GitHub · Gmail"),
]


def fetch_stats():
    query = """
    query($login: String!) {
      user(login: $login) {
        followers { totalCount }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes { stargazerCount }
        }
        contributionsCollection {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          restrictedContributionsCount
        }
      }
    }
    """
    body = json.dumps({"query": query, "variables": {"login": USERNAME}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    user = data["data"]["user"]
    stars = sum(r["stargazerCount"] for r in user["repositories"]["nodes"])
    contrib = user["contributionsCollection"]
    return {
        "repos": user["repositories"]["totalCount"],
        "stars": stars,
        "followers": user["followers"]["totalCount"],
        "commits": contrib["totalCommitContributions"],
        "private": contrib["restrictedContributionsCount"],
        "prs": contrib["totalPullRequestContributions"],
        "issues": contrib["totalIssueContributions"],
    }


def esc(s):
    return html.escape(str(s))


def kv_line(x, y, label, dots, value, font_size=15):
    return (
        f'<text x="{x}" y="{y}" font-size="{font_size}">'
        f'<tspan fill="{ACCENT}" font-weight="600">{esc(label)}</tspan>'
        f'<tspan fill="{MUTED}">{esc(dots)}: </tspan>'
        f'<tspan fill="{INK}">{esc(value)}</tspan>'
        f"</text>"
    )


def build_svg(stats):
    pad_x = 28
    label_w = 14
    font_size = 15
    line_h = 26
    titlebar_h = 42
    top_pad = 20
    bottom_pad = 22
    content_w = 700

    stats_rows = [
        ("Repos", str(stats["repos"])),
        ("Stars", str(stats["stars"])),
        ("Commits (1y)", f'{stats["commits"]} (+{stats["private"]} private)'),
        ("Followers", str(stats["followers"])),
        ("PRs / Issues", f'{stats["prs"]} / {stats["issues"]}'),
    ]

    # header + rule + specs, blank, header + rule + stats
    n_lines = (2 + len(SPECS)) + 1 + (2 + len(stats_rows))
    total_h = titlebar_h + top_pad + n_lines * line_h + bottom_pad
    total_w = content_w

    svg = []
    svg.append(
        f'<svg width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    )
    svg.append(
        f'<defs><clipPath id="round"><rect width="{total_w}" height="{total_h}" rx="10"/></clipPath></defs>'
    )
    svg.append('<g clip-path="url(#round)">')
    svg.append(f'<rect width="{total_w}" height="{total_h}" fill="{BG}"/>')
    svg.append(f'<rect width="{total_w}" height="{titlebar_h}" fill="{TITLEBAR}"/>')
    svg.append(f'<circle cx="24" cy="{titlebar_h/2}" r="6" fill="#FF5F56"/>')
    svg.append(f'<circle cx="46" cy="{titlebar_h/2}" r="6" fill="#FFBD2E"/>')
    svg.append(f'<circle cx="68" cy="{titlebar_h/2}" r="6" fill="#27C93F"/>')
    svg.append(
        f'<text x="{total_w/2}" y="{titlebar_h/2+5}" font-size="13" fill="{MUTED}" '
        f'text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        f"stanley@dev — zsh</text>"
    )
    svg.append(f'<rect x="0" y="{titlebar_h}" width="{total_w}" height="1" fill="{BORDER}"/>')
    svg.append(
        "<style>text{font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;}</style>"
    )

    y = titlebar_h + top_pad + font_size
    svg.append(
        f'<text x="{pad_x}" y="{y}" font-size="{font_size+2}" font-weight="700" fill="{INK}">'
        f"visitor@stanley:~$ whoami</text>"
    )
    y += line_h
    svg.append(f'<text x="{pad_x}" y="{y}" font-size="{font_size}" fill="{ACCENT}">{"-"*11}</text>')
    y += line_h
    for label, value in SPECS:
        dots = "." * max(1, label_w - len(label))
        svg.append(kv_line(pad_x, y, label, dots, value, font_size))
        y += line_h

    y += line_h  # blank spacer

    svg.append(
        f'<text x="{pad_x}" y="{y}" font-size="{font_size+2}" font-weight="700" fill="{INK}">'
        f"visitor@stanley:~$ github-stats</text>"
    )
    y += line_h
    svg.append(f'<text x="{pad_x}" y="{y}" font-size="{font_size}" fill="{ACCENT}">{"-"*13}</text>')
    y += line_h
    stats_label_w = 14
    for label, value in stats_rows:
        dots = "." * max(1, stats_label_w - len(label))
        svg.append(kv_line(pad_x, y, label, dots, value, font_size))
        y += line_h

    svg.append("</g>")
    svg.append("</svg>")
    return "\n".join(svg)


def main():
    stats = fetch_stats()
    svg_content = build_svg(stats)
    out_path = os.path.join(os.path.dirname(__file__), "..", "assets", "terminal.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("wrote", out_path)
    print(stats)


if __name__ == "__main__":
    main()
