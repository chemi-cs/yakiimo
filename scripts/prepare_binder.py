#!/usr/bin/env python3
"""Copy a verified JupyterLite checkout into a native-Python Binder notebook.

Usage: python scripts/prepare_binder.py ../yakiimo-lite
Review the resulting diff and run validate_notebook.py --execute before publishing.
This script does not fetch, commit, or push any files.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = "yakiimo_python_junior.ipynb"
SOURCE_REPOSITORY = "https://github.com/chemi-cs/yakiimo-lite"


def text(cell):
    source = cell["source"]
    return "".join(source) if isinstance(source, list) else source


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    source_root = Path(sys.argv[1]).resolve()
    status = subprocess.check_output(
        ["git", "-C", str(source_root), "status", "--porcelain"], text=True
    )
    if status.strip():
        raise SystemExit("Source checkout must be clean so its commit identifies the content.")
    commit = subprocess.check_output(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"], text=True
    ).strip()
    source_path = source_root / "content" / NOTEBOOK
    source_bytes = source_path.read_bytes()
    notebook = json.loads(source_bytes)
    cells = notebook["cells"]
    if len(cells) != 94 or sum(c["cell_type"] == "code" for c in cells) != 45:
        raise SystemExit("Source lesson structure changed. Review the conversion before continuing.")

    old_note = (
        "> 講師向け：このNotebookは、同梱の設定で作ったJupyterLiteサイト用です。\n"
        "> Python 3.13（Pyodide 0.29.4）に合わせたRDKitの実験ビルドを使用します。\n"
        "> 一般のJupyterLiteサイトへNotebookだけを移しても、同じ環境にはなりません。"
    )
    new_note = (
        "> 講師向け：これは、公開済みJupyterLite教材のBinder用バックアップです。\n"
        "> サーバー上のPython 3.12と通常のRDKitを使用します。必要なライブラリは起動時に用意されています。\n"
        "> 授業内容・演習・分子表示は元の教材と同じです。編集内容は終了前にダウンロードしてください。"
    )
    if old_note not in text(cells[86]) or "await piplite.install" not in text(cells[87]):
        raise SystemExit("Source environment instructions changed. Review the conversion first.")
    cells[86]["source"] = text(cells[86]).replace(old_note, new_note).splitlines(keepends=True)
    prep = text(cells[87])
    imports = prep[prep.index("from rdkit import Chem, rdBase"):]
    cells[87]["source"] = (
        "# 最初に1回だけ実行する準備セル\n"
        "# Binderでは必要なライブラリをあらかじめインストールしています。\n" + imports
    ).splitlines(keepends=True)
    hardware_note = "**JupyterLiteでは実行しません。**"
    if hardware_note not in text(cells[91]):
        raise SystemExit("Source hardware warning changed. Review the conversion first.")
    cells[91]["source"] = text(cells[91]).replace(
        hardware_note, "**Binder・JupyterLiteでは実行しません。**"
    ).splitlines(keepends=True)

    for cell in cells:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        cell["metadata"].pop("execution", None)
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"
    }
    notebook["metadata"]["language_info"] = {"name": "python", "version": "3.12"}
    notebook["metadata"]["yakiimo_environment"] = {
        "platform": "Binder / native CPython", "python": "3.12", "rdkit": "2026.3.6",
        "py3dmol": "2.5.2"
    }
    notebook["metadata"]["binder_source"] = {
        "repository": SOURCE_REPOSITORY, "commit": commit, "path": f"content/{NOTEBOOK}"
    }
    output = (json.dumps(notebook, ensure_ascii=False, indent=1) + "\n").encode()
    (ROOT / NOTEBOOK).write_bytes(output)
    assets = {}
    for name in ("1.2.png", "5wqs.pdb"):
        data = (source_root / "content" / name).read_bytes()
        if (ROOT / name).read_bytes() != data:
            raise SystemExit(f"Existing asset {name} differs. Review instead of overwriting it.")
        assets[name] = hashlib.sha256(data).hexdigest()
    manifest = {
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": commit,
        "source_notebook_path": f"content/{NOTEBOOK}",
        "source_notebook_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "binder_notebook": NOTEBOOK,
        "binder_notebook_sha256": hashlib.sha256(output).hexdigest(),
        "cell_count": len(cells),
        "code_cell_count": 45,
        "adapted_cell_indexes_zero_based": [86, 87, 91],
        "adaptations": [
            "Replace the JupyterLite-only environment note with Binder instructions.",
            "Remove the WebAssembly installer; import preinstalled native packages.",
            "Keep the Pico hardware code as read-only teaching material in both environments.",
            "Use the python3 kernelspec, native environment metadata, and cleared outputs."
        ],
        "assets_sha256": assets
    }
    (ROOT / "BINDER_SOURCE.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Prepared {NOTEBOOK} from {commit}. Review and test before publishing.")


if __name__ == "__main__":
    main()
