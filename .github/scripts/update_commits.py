#!/usr/bin/env python3
"""
Script to automatically fetch the latest public commits of Loriek-cyber
and update the commit history section in README.md.
"""

import os
import re
import urllib.request
import json

USERNAME = "Loriek-cyber"
README_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")
START_MARKER = "<!-- RECENT_COMMITS_START -->"
END_MARKER = "<!-- RECENT_COMMITS_END -->"
MAX_COMMITS = 8

def fetch_recent_commits():
    url = f"https://api.github.com/search/commits?q=author:{USERNAME}+is:public&sort=author-date&order=desc"
    headers = {
        "User-Agent": f"{USERNAME}-Profile-Updater",
        "Accept": "application/vnd.github+json"
    }
    
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching commits from GitHub API: {e}")
        return None

    items = data.get("items", [])[:MAX_COMMITS]
    if not items:
        return "- *Nessun commit pubblico recente trovato.*"

    lines = []
    for item in items:
        sha = item.get("sha", "")[:7]
        url = item.get("html_url", "#")
        commit_info = item.get("commit", {})
        date_str = commit_info.get("author", {}).get("date", "")[:10]
        repo_name = item.get("repository", {}).get("full_name", "")
        raw_msg = commit_info.get("message", "").split("\n")[0].strip()
        
        # Clean message
        if len(raw_msg) > 75:
            raw_msg = raw_msg[:72] + "..."
        clean_msg = raw_msg.replace("<", "&lt;").replace(">", "&gt;")
        repo_url = f"https://github.com/{repo_name}"
        lines.append(f"- 🚀 `{date_str}` — [`{sha}`]({url}) in **[{repo_name}]({repo_url})**: {clean_msg}")

    return "\n".join(lines)

def update_readme():
    readme_path = os.path.abspath(README_PATH)
    if not os.path.exists(readme_path):
        print(f"README file not found at {readme_path}")
        return False

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        rf"({re.escape(START_MARKER)})(.*?)({re.escape(END_MARKER)})",
        re.DOTALL
    )

    if not pattern.search(content):
        print("Markers not found in README.md")
        return False

    commits_text = fetch_recent_commits()
    if commits_text is None:
        print("Skipping README update due to fetch error.")
        return False

    new_block = f"{START_MARKER}\n{commits_text}\n{END_MARKER}"
    updated_content = pattern.sub(new_block, content)

    if updated_content != content:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("README.md successfully updated with latest commits!")
    else:
        print("README.md is already up to date.")
    return True

if __name__ == "__main__":
    update_readme()
