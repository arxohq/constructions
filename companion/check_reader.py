#!/usr/bin/env python3
"""Check the Water route and four truth states using the reviewed public CLI."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--law', type=Path, help='CLI executable; defaults to law on PATH')
    parser.add_argument('--bundle', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    binary = str(args.law.resolve()) if args.law else shutil.which('law')
    assert binary, 'Install @arxo/cli and put law on PATH.'
    bundle = args.bundle.resolve()
    report = json.loads((bundle / 'execution.json').read_text())
    version = json.loads(subprocess.run([binary, 'version', '--json'], capture_output=True, text=True, check=True).stdout)
    assert version['tool'] == report['binary']['tool'], 'Use the CLI version reviewed for this companion.'
    assert version['semantics'] == report['binary']['semantics'], 'The supported semantic line changed.'
    for key, item in report['compiled'].items():
        assert sha(bundle / item['program']) == item['sha256'], key
        if 'test_world' in item:
            assert sha(bundle / item['test_world']) == item['world_sha256'], key
    out = args.out.resolve() if args.out else Path(tempfile.mkdtemp(prefix='constructions-reader-'))
    out.mkdir(parents=True, exist_ok=True)
    def call(arguments):
        result = subprocess.run([str(binary), *map(str, arguments)], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    water = bundle / report.get('water_package', 'voda')
    query = 'evaluate truth(openstax.chemistry_acids::amphiprotic(entity_ref("urn:case:kniga:h2o")));'
    answer = call(['ask', water, '--case', 'Voda', '--query', query, '--query-id', 'amphi', '--out', out / 'water', '--format', 'json'])
    assert answer['results'][0]['truthStatus'] == 'TRUE_ONLY'
    assert answer['results'][0]['evaluationStatus'] == 'COMPUTED'
    replay = call(['eval', out / 'water'])
    assert replay['resultHash'] == answer['resultHash'], 'Saved answer replay changed.'
    assert replay['proofGraph']['proofHash'] == answer['proofGraph']['proofHash'], 'Saved proof replay changed.'
    original = (water / 'cases/voda.lawcase').read_text()
    prefix = original[:original.index('    assert')]
    positive = '    assert openstax.chemistry_acids::donates_proton(entity_ref("urn:case:kniga:h2o")) { id "reader-positive"; origin case_input; }\n'
    negative = '    assert not openstax.chemistry_acids::donates_proton(entity_ref("urn:case:kniga:h2o")) { id "reader-negative"; origin case_input; }\n'
    states = {'TRUE_ONLY': positive, 'FALSE_ONLY': negative, 'BOTH': positive + negative, 'NEITHER': ''}
    observations = []
    for expected, facts in states.items():
        case = out / 'cases' / expected
        assert not case.exists(), 'Choose a new output directory; reader evidence is preserved.'
        shutil.copytree(water, case)
        (case / 'cases/voda.lawcase').write_text(prefix + facts + '}\n')
        response = call(['ask', case, '--case', 'Voda',
                         '--query', 'evaluate truth(openstax.chemistry_acids::donates_proton(entity_ref("urn:case:kniga:h2o")));',
                         '--query-id', 'donates', '--out', out / 'answers' / expected, '--format', 'json'])
        actual = response['results'][0]
        assert actual['evaluationStatus'] == 'COMPUTED', actual
        assert actual['truthStatus'] == expected, (expected, actual)
        observations.append({'expected': expected, 'actual': actual['truthStatus'], 'resultHash': response['resultHash']})
    outcome = {'water': 'accepted', 'replay': 'same resultHash and proofHash',
               'four_states': observations, 'binary_sha256': version['binaryHash'].removeprefix('sha256:'),
               'tool': version['tool'], 'independent_human_pilot': 'not_performed'}
    (out / 'reader-check.json').write_text(json.dumps(outcome, indent=2) + '\n')
    print(json.dumps(outcome, indent=2))

if __name__ == '__main__':
    main()
