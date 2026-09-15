"""Execute the full notebook, export figures and run thickness holdout diagnostics."""
from pathlib import Path
import base64
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import time
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'notebooks/neutron_transport.ipynb'
notebook = nbformat.read(path, as_version=4)
for cell in notebook.cells:
    if cell.cell_type == 'code':
        cell.outputs = []
        cell.execution_count = None
source_hash = hashlib.sha256('\n'.join(c.source for c in notebook.cells).encode()).hexdigest()
manager = KernelManager(kernel_name='python3')
manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
started = time.perf_counter()
NotebookClient(notebook, km=manager, timeout=600, resources={'metadata': {'path': str(path.parent)}}).execute()
nbformat.validate(notebook)
nbformat.write(notebook, path)
names = {38: 'outcome_fractions', 43: 'thickness_scan', 56: 'layered_transport', 61: 'surrogate_random_split'}
for index, name in names.items():
    for output in notebook.cells[index].get('outputs', []):
        png = output.get('data', {}).get('image/png')
        if png:
            (ROOT / f'figures/{name}.png').write_bytes(base64.b64decode(png))
subprocess.run([sys.executable, str(ROOT / 'scripts/evaluate_thickness.py')], check=True)
record = {'status': 'passed', 'seed': 20260915, 'source_sha256': source_hash,
          'elapsed_seconds': round(time.perf_counter()-started, 2),
          'python': sys.version.split()[0], 'code_cells': sum(c.cell_type == 'code' for c in notebook.cells),
          'versions': {p: importlib.metadata.version(p) for p in ['numpy','pandas','matplotlib','scikit-learn','nbclient','nbformat','ipykernel']}}
(ROOT / 'results/reproduction.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps(record, indent=2))
