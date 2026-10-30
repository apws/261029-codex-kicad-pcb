"""Check English Codex skill metadata, project discovery links and Markdown/AsciiDoc file links.
Run python3 scripts/check_skills.py after staging files. No marketplace required.
Exit 0 PASS, 1 findings, 2 execution error. Standard library, read-only.
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SCRIPT_RE = re.compile(r"`(?:[^`]*?\s)?(scripts/[\w.-]+\.(?:py|mjs|txt))")
LATIN_RE = re.compile(r"[A-Za-z]{3,}")


def frontmatter(text):
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return None
    fields = {}
    for line in lines[1:lines[1:].index("---") + 1]:
        key, sep, value = line.partition(":")
        if sep and key and not key.startswith(" "):
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] == "'":
                value = value[1:-1].replace("''", "'")
            elif len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
            fields[key.strip()] = value
    return fields


def check_skill(skill, siblings):
    problems = []
    name = skill.name
    skill_md = skill / "SKILL.md"
    if not skill_md.is_file():
        return [f"{name}: SKILL.md missing"]
    text = skill_md.read_text(encoding="utf-8")
    fm = frontmatter(text)
    if fm is None:
        return [f"{name}: SKILL.md has no frontmatter"]
    if fm.get("name") != name:
        problems.append(f"{name}: frontmatter name {fm.get('name')!r} differs from folder name")
    if not NAME_RE.match(name):
        problems.append(f"{name}: folder name must be lowercase words joined by hyphens")
    desc = fm.get("description", "")
    if not desc:
        problems.append(f"{name}: description missing")
    elif len(desc) > 1024:
        problems.append(f"{name}: description is {len(desc)} characters (max 1024)")
    if desc and not LATIN_RE.search(desc):
        problems.append(f"{name}: description needs English trigger text")
    yaml = skill / "agents" / "openai.yaml"
    if not yaml.is_file():
        problems.append(f"{name}: agents/openai.yaml missing")
    elif f"${name}" not in yaml.read_text(encoding="utf-8"):
        problems.append(f"{name}: agents/openai.yaml default_prompt does not mention ${name}")
    for ref in sorted(set(SCRIPT_RE.findall(text))):
        if not any((s / ref).is_file() for s in [skill, *siblings]):
            problems.append(f"{name}: SKILL.md names {ref}, which does not exist")
    return problems


def check_links(path, rel):
    problems = []
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"(?ms)^----\n.*?^----$", "", text)
    targets = LINK_RE.findall(text)
    targets += re.findall(r"(?:link|xref|image)::?([^\s\[]+)\[", text)
    for target in targets:
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith(("#", "<")):
            continue
        file_part = unquote(target.split("#", 1)[0])
        if file_part and not (path.parent / file_part).exists():
            problems.append(f"{rel}: broken link {target}")
    return problems


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    try:
        skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
        problems = []
        for skill in skills:
            problems += check_skill(skill, [s for s in skills if s != skill])
        for skill in skills:
            link = ROOT / ".agents" / "skills" / skill.name
            if not link.is_symlink() or link.resolve() != skill.resolve():
                problems.append(f"{skill.name}: project discovery link missing or wrong")
        out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z", "*.md", "*.adoc"],
                             capture_output=True, check=True)
        docs = [p for p in out.stdout.decode("utf-8").split("\0") if p]
        for rel in docs:
            if (ROOT / rel).is_file():
                problems += check_links(ROOT / rel, rel)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return 2
    for p in problems:
        print(p)
    print(f"skills {len(skills)}, documentation files {len(docs)}, problems {len(problems)}: "
          f"{'PASS' if not problems else 'FAIL'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
