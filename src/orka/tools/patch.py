import re
from pathlib import Path
from unidiff import PatchSet


class PatchError(Exception):
    pass


def extract_file_paths(diff: str):
    """Extrai arquivos de um diff estilo git."""

    files = []

    for line in diff.splitlines():
        if line.startswith("+++"):
            path = line.replace("+++ b/", "").replace("+++", "").strip()
            files.append(path)

    return files


def validate_diff(diff: str):
    """Valida se um diff é válido."""

    if not diff.strip():
        raise PatchError("Empty diff")

    if "+++" not in diff or "---" not in diff:
        raise PatchError("Invalid diff format")

    files = extract_file_paths(diff)

    if not files:
        print("⚠️ Could not parse files from diff")
        print(diff)
        return

    return files


def extract_diff(text: str) -> str:
    match = re.search(r"(---[\s\S]+?)(?:\n\n|\Z)", text)
    if match:
        return match.group(1).strip()
    return text


def normalize_diff(diff: str) -> str:
    diff = diff.replace("---a/", "--- a/")
    diff = diff.replace("+++b/", "+++ b/")

    diff = diff.replace("++++", "\n+++ ")

    return diff


def backup_file(path: Path):
    backup_path = path.with_suffix(path.suffix + ".bak")

    if path.exists():
        backup_path.write_text(path.read_text())

    return backup_path


def apply_patch(diff: str, dry_run: bool = True):
    patch = PatchSet(diff)

    if not patch:
        raise PatchError("Invalid or empty patch")

    for patched_file in patch:
        file_path = Path(patched_file.path)

        print(f"\nProcessing: {file_path}")

        if not file_path.exists():
            raise PatchError(f"File not found: {file_path}")

        original_lines = file_path.read_text().splitlines(keepends=True)
        new_lines = original_lines.copy()

        offset = 0

        for hunk in patched_file:
            start = hunk.source_start - 1 + offset

            # remove linhas antigas
            for line in hunk:
                if line.is_removed:
                    if start < len(new_lines):
                        new_lines.pop(start)
                        offset -= 1

                elif line.is_added:
                    new_lines.insert(start, line.value)
                    start += 1
                    offset += 1

                else:
                    start += 1

        if dry_run:
            print("DRY RUN - no changes applied")
        else:
            backup_file(file_path)
            file_path.write_text("".join(new_lines))
            print(f"Applied changes to {file_path}")