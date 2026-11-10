#!/usr/bin/env python3
"""Validate the Binder lesson. --execute runs all 45 code cells in a fresh kernel."""

import argparse
import hashlib
import json
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--source-checkout", type=Path)
    parser.add_argument("--executed-output", type=Path)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "BINDER_SOURCE.json").read_text())
    path = ROOT / manifest["binder_notebook"]
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == manifest["binder_notebook_sha256"]
    notebook = nbformat.reads(data.decode(), as_version=4)
    nbformat.validate(notebook)
    assert len(notebook.cells) == manifest["cell_count"] == 94
    code_cells = [c for c in notebook.cells if c.cell_type == "code"]
    assert len(code_cells) == manifest["code_cell_count"] == 45
    assert notebook.metadata.kernelspec.name == "python3"
    for cell in code_cells:
        assert cell.execution_count is None and cell.outputs == []
        compile(cell.source, "lesson-cell", "exec")
        assert "piplite" not in cell.source and "duty_u16" not in cell.source
    for name, expected in manifest["assets_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected

    if args.source_checkout:
        source_data = (args.source_checkout / manifest["source_notebook_path"]).read_bytes()
        assert hashlib.sha256(source_data).hexdigest() == manifest["source_notebook_sha256"]
        source = nbformat.reads(source_data.decode(), as_version=4)
        changed = []
        for index, (a, b) in enumerate(zip(source.cells, notebook.cells)):
            assert a.cell_type == b.cell_type
            if a.source != b.source:
                changed.append(index)
        assert changed == manifest["adapted_cell_indexes_zero_based"], changed
        print(f"PASS: source parity; only the {len(changed)} documented environment adaptations differ.")
    print("PASS: schema, all 45 code cells compile, native kernel, assets, and checksums.")

    if args.execute:
        from nbclient import NotebookClient

        # Assertions execute in the same kernel as the lesson, without altering the saved lesson.
        checks = nbformat.v4.new_code_cell('''
from rdkit import Chem, rdBase
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
assert rdBase.rdkitVersion == "2026.03.6", rdBase.rdkitVersion
assert rdMolDescriptors.CalcMolFormula(mol) == "C12H22O11"
assert abs(Descriptors.MolWt(mol) - 342.297) < 0.001
assert "<svg" in str(svg)
assert mol_3d.GetNumConformers() == 1
assert status == 0 and result == 0
assert "createViewer" in view_mol._make_html()
assert "createViewer" in view_enz._make_html()
assert pdb_path.is_file()
for example, formula in [("CCO", "C2H6O"), ("O", "H2O")]:
    molecule = Chem.MolFromSmiles(example)
    assert rdMolDescriptors.CalcMolFormula(molecule) == formula
    molecule = Chem.AddHs(molecule)
    assert AllChem.EmbedMolecule(molecule, randomSeed=42) == 0
    assert AllChem.UFFOptimizeMolecule(molecule, maxIters=1000) == 0
print("PASS: maltose formula/mass/SVG/3D, enzyme viewer, ethanol, and water.")
''')
        notebook.cells.append(checks)
        NotebookClient(
            notebook, timeout=180, kernel_name="python3", allow_errors=False,
            resources={"metadata": {"path": str(ROOT)}}
        ).execute()
        for cell in notebook.cells:
            for output in cell.get("outputs", []):
                assert output.output_type != "error"
        output_types = [key for cell in notebook.cells for output in cell.get("outputs", [])
                        for key in output.get("data", {})]
        assert "image/svg+xml" in output_types
        assert output_types.count("text/html") >= 2
        assert "image/png" in output_types
        notebook.cells.pop()
        if args.executed_output:
            nbformat.write(notebook, args.executed_output)
        print("PASS: all 45 lesson cells and molecular assertions executed in a fresh Python kernel.")
        print("NOTE: HTML viewer generation is checked; a browser is needed to verify WebGL rendering.")


if __name__ == "__main__":
    main()
