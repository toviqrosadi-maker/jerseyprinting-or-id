"""Run all existing padel QA scripts sequentially and retain exit codes/logs.

python scripts/run_padel_qa.py --output <evidence-directory>
Use the interpreter with Playwright installed. Asset converters are not QA tests.
"""
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
out=args.output.resolve()
out.mkdir(parents=True,exist_ok=True)
names=['qa_padel.py','qa_padel_browser.py','qa_padel_images.py','qa_padel_pillar_assets.py']
results=[]
for name in names:
    command=[sys.executable,str(ROOT/'scripts'/name)]
    if name!='qa_padel.py':
        command+=['--output',str(out/Path(name).stem)]
    result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=out/(Path(name).stem+'.log')
    log.write_bytes(result.stdout)
    results.append({'script':name,'exitCode':result.returncode,'log':log.name})
    (out/'suite-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(name,'PASS' if result.returncode==0 else 'FAIL',flush=True)
raise SystemExit(any(r['exitCode'] for r in results))
