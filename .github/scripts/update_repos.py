import json
import re
import urllib.request
from datetime import datetime

GITHUB_USERNAME = "Rashi-koiri"
README_PATH = "README.md"

ORDINALS = {
    1: "First",
    2: "Second",
    3: "Third",
    4: "Fourth",
    5: "Fifth",
    6: "Sixth",
    7: "Seventh",
    8: "Eighth",
    9: "Ninth",
    10: "Tenth"
}

def get_ordinal(n):
    if n in ORDINALS:
        return f"{n}{get_suffix(n)} ({ORDINALS[n]} Repository)"
    return f"{n}{get_suffix(n)} Repository"

def get_suffix(n):
    if 11 <= (n % 100) <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")

def fetch_repositories(username):
    url = f"https://api.github.com/users/{username}/repos?sort=created&direction=asc&per_page=100"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "GitHub-Auto-Repo-Updater"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching repositories: {e}")
        return []

def format_date(iso_str):
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso_str[:10]

def build_markdown(repos):
    if not repos:
        return "\n*No public repositories found yet.*\n"

    lines = []
    lines.append("\n<!-- Generated automatically by GitHub Action. Do not edit manually! -->\n")
    
    # Timeline list
    lines.append('<div align="left">\n')
    for idx, repo in enumerate(repos, start=1):
        name = repo.get("name", "untitled")
        url = repo.get("html_url", f"https://github.com/{GITHUB_USERNAME}/{name}")
        desc = repo.get("description") or "Exciting project in active development."
        lang = repo.get("language") or "General"
        stars = repo.get("stargazers_count", 0)
        created = format_date(repo.get("created_at"))
        ordinal_title = get_ordinal(idx)

        icon = "🛸" if idx == 1 else ("⚡" if idx == 2 else ("🌟" if idx == 3 else "📦"))

        lines.append(f"""<blockquote>
  <h4>{icon} <b>{ordinal_title}</b>: <a href="{url}"><code>{name}</code></a> <img src="https://img.shields.io/badge/Public-238636?style=flat-square&logo=github" alt="Public" /></h4>
  <p>📝 {desc}</p>
  <p>
    <img src="https://img.shields.io/badge/Language-{lang.replace(' ', '%20')}-6366f1?style=flat-square" alt="Language" />
    <img src="https://img.shields.io/badge/Stars-⭐%20{stars}-yellow?style=flat-square" alt="Stars" />
    <img src="https://img.shields.io/badge/Created-{created.replace(' ', '%20')}-blue?style=flat-square" alt="Date" />
    <a href="{url}"><img src="https://img.shields.io/badge/Explore-View%20Repository%20↗-success?style=flat-square" alt="Explore" /></a>
  </p>
</blockquote>
""")
    lines.append('</div>\n')

    # Also include a clean summary table
    lines.append("\n| Milestone | Repository | Primary Language | Created On | Quick Link |")
    lines.append("| :---: | :--- | :---: | :---: | :---: |")
    for idx, repo in enumerate(repos, start=1):
        name = repo.get("name", "untitled")
        url = repo.get("html_url", f"https://github.com/{GITHUB_USERNAME}/{name}")
        lang = repo.get("language") or "Code"
        created = format_date(repo.get("created_at"))
        ordinal_str = f"<b>{idx}{get_suffix(idx)} Repo</b>"
        lines.append(f"| {ordinal_str} | [`{name}`]({url}) | `{lang}` | {created} | [Open Repo ↗]({url}) |")

    lines.append("\n")
    return "\n".join(lines)

def update_readme():
    repos = fetch_repositories(GITHUB_USERNAME)
    if not repos:
        print("No repositories fetched. Skipping README update.")
        return

    content = build_markdown(repos)

    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    pattern = r"(<!-- REPOSITORIES_TIMELINE:START -->)(.*?)(<!-- REPOSITORIES_TIMELINE:END -->)"
    if not re.search(pattern, readme, flags=re.DOTALL):
        print("Marker tags not found in README.md")
        return

    replacement = f"\\1\n{content}\n\\3"
    updated_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_readme)

    print(f"Successfully updated {README_PATH} with {len(repos)} repositories!")

if __name__ == "__main__":
    update_readme()
