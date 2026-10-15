#!/usr/bin/env python3
"""Run the four receipt scenes through the public CLI, without Cargo/lawref."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import shutil
import tempfile

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--law', type=Path)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    binary = str(args.law.resolve()) if args.law else shutil.which('law')
    assert binary, 'Install @arxo/cli and put law on PATH.'
    base = bundle / 'packs/demo/expense-evidence'
    directory = Path(tempfile.mkdtemp(prefix='constructions-expense-'))
    def call(arguments):
        result = subprocess.run([str(binary), *map(str, arguments)], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    original = call(['engine', 'lower-case', base / 'scenes/base.lawcase'])
    program = json.loads((base / 'clir/expense-evidence.lawir.json').read_text())
    query = {'queryId': 'urn:query:demo:reimbursable', 'kind': 'truth',
             'literal': {'kind': 'literal', 'polarity': 'positive',
                'predicate': 'urn:demo:expense-evidence#reimbursable',
                'args': [{'kind': 'entity_ref', 'id': 'urn:demo:purchase:42'},
                         {'kind': 'entity_ref', 'id': 'urn:demo:employee:7'}]}}
    observations = []
    for index, (excluded, expected) in enumerate(((['B92', 'B93'], 'NEITHER'),
            (['B93'], 'TRUE_ONLY'), (['B92', 'B93'], 'NEITHER'), (['B92'], 'TRUE_ONLY')), 1):
        project = directory / str(index)
        project.mkdir()
        case = copy.deepcopy(original)
        removed = {'urn:demo:expense-evidence#doc-' + name for name in excluded}
        case['evidence'] = [e for e in case['evidence'] if e['id'] not in removed]
        case['supportEdges'] = [s for s in case['supportEdges'] if s['from'] not in removed]
        case['verifications'] = [v for v in case.get('verifications', []) if v['evidence'] not in removed]
        request = {'schemaVersion': 'law.core.evaluation-request/0.2',
                   'semanticVersion': program['semanticVersion'], 'ir': program, 'case': case, 'query': query}
        (project / 'request.json').write_text(json.dumps(request))
        result = call(['engine', 'eval', project])
        (project / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        actual = result['results'][0]
        assert actual['truthStatus'] == expected and actual['evaluationStatus'] == 'COMPUTED', (index, actual)
        observations.append({'scene': index, 'excluded': excluded, 'expected': expected,
                             'truthStatus': actual['truthStatus'], 'document': result})
    if args.json:
        print(json.dumps(observations, ensure_ascii=False, indent=2))
    else:
        for row in observations:
            print(f"Scene {row['scene']}: {row['truthStatus']} (excluded {', '.join(row['excluded'])})")
            report = row['document'].get('evidenceAcceptance', {})
            for decision in report.get('decisions', []):
                print(' ', decision['evidence'], decision['decision'], ', '.join(decision.get('reasons', [])))
        print('Four scene expectations verified. Evidence:', directory)

if __name__ == '__main__':
    main()
