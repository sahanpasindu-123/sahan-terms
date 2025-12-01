import os
import re
import json

REPO_PATH = "."

def gather_changed_files():
    """Get list of changed files from GitHub Actions environment."""
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        return []

    with open(event_path) as f:
        event = json.load(f)

    changed = []
    for file in event["pull_request"]["head"]["repo"].get("updated_at", []):
        changed.append(file)
    return changed


def analyze_code():
    """Very simple rule-based PR reviewer."""

    report = []
    
    for root, dirs, files in os.walk(REPO_PATH):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Rule 1: TODO detection
                if "TODO" in content:
                    report.append(f"⚠️ TODO found in `{path}` — please resolve.")

                # Rule 2: Check function size
                big_funcs = re.findall(r"def .*?:([\s\S]*?)(?=\ndef|\Z)", content)
                for func in big_funcs:
                    lines = func.count("\n")
                    if lines > 40:
                        report.append(f"⚠️ Function in `{path}` is larger than 40 lines.")

                # Rule 3: Missing docstrings
                funcs = re.findall(r"def\s+\w+\(.*?\):", content)
                for func in funcs:
                    if '"""' not in content.split(func)[1][:120]:
                        report.append(f"📘 Missing docstring for: `{func}` in `{path}`")

                # Rule 4: Debug print
                if "print(" in content:
                    report.append(f"🔧 Debug `print()` found in `{path}` — consider removing.")

    if not report:
        return "🎉 Everything looks clean! Great job."

    return "\n".join(report)


def write_output(review_text):
    """Make output available to GitHub Actions step."""
    output = f"::set-output name=review_comment::{review_text}"
    print(output)


if __name__ == "__main__":
    review = analyze_code()
    write_output(review)

