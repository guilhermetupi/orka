import re
from pathlib import Path


class PatchError(Exception):
    pass


def extract_file_paths(diff: str):
    """Extrai arquivos de um diff estilo git."""

    files = []

    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line.replace("+++ b/", "").strip()
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
        raise PatchError("No files found in diff")

    return files


def backup_file(path: Path):
    backup_path = path.with_suffix(path.suffix + ".bak")

    if path.exists():
        backup_path.write_text(path.read_text())

    return backup_path


def apply_patch(diff: str, dry_run: bool = True):
    files = validate_diff(diff)

    print(f"Files to modify: {files}")

    if dry_run:
        print("DRY RUN: no changes applied")
        return

    for file in files:
        path = Path(file)

        if not path.exists():
            raise PatchError(f"File not found: {file}")

        backup_file(path)

        # ⚠️ simplificado (vamos melhorar depois)
        print(f"Applying changes to {file}")
