#!/usr/bin/env python3
"""Prepare one typed scenario for the public CLI's vector explain commands."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('test', type=Path)
    parser.add_argument('--law', help='CLI executable; defaults to law on PATH')
    parser.add_argument('--program', type=Path, required=True)
    parser.add_argument('--imports', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    binary = str(Path(args.law).resolve()) if args.law else shutil.which('law')
    assert binary, 'Install @arxo/cli and put law on PATH.'
    cmd = [binary, 'engine', 'lower-test', str(args.test), '--program', str(args.program)]
    if args.imports:
        cmd.extend(['--imports', str(args.imports)])
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    tests = json.loads(result.stdout)['tests']
    assert len(tests) == 1, 'Keep one question in the scenario copy.'
    scenario = tests[0]
    assert 'case' in scenario and 'query' in scenario
    args.out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.program, args.out / 'ir.json')
    for key in ('case', 'query', 'expectations'):
        (args.out / (key + '.json')).write_text(json.dumps(scenario[key], ensure_ascii=False, indent=2) + '\n')
    version = json.loads(subprocess.run([binary, 'version', '--json'], capture_output=True, text=True, check=True).stdout)
    provenance = {'compiler': version['binaryHash'], 'tool': version['tool'],
                  'source': hashlib.sha256(args.test.read_bytes()).hexdigest(),
                  'program': hashlib.sha256(args.program.read_bytes()).hexdigest(),
                  'semantic_decisions': 'none; compiler-lowered case and query copied verbatim'}
    (args.out / 'source-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')

if __name__ == '__main__':
    main()
