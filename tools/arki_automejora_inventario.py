#!/usr/bin/env python3
"""Read-only ARKI self-inspection. No network, database writes, or code edits."""
import json, subprocess, pathlib, datetime, hashlib, sys
root = pathlib.Path(__file__).resolve().parents[1]
def git(*args):
    p=subprocess.run(['git',*args],cwd=root,text=True,capture_output=True,timeout=15)
    return p.stdout.strip() if p.returncode == 0 else None
tracked=(git('ls-files') or '').splitlines()
py=[p for p in tracked if p.endswith('.py')]
tests=[p for p in py if p.startswith('tests/') and pathlib.Path(p).name.startswith('test_')]
contracts=[p for p in tracked if 'contract' in p.lower() or 'frozen' in p.lower()]
risks=[]
if git('status','--porcelain'): risks.append({'type':'WORKTREE_DIRTY','status':'REVIEW_REQUIRED'})
if not tests: risks.append({'type':'TESTS_NOT_DISCOVERED','status':'UNKNOWN'})
if not any('ace88' in p.lower() for p in tests): risks.append({'type':'ACE88_TESTS_NOT_DISCOVERED','status':'UNKNOWN'})
report={'schema':'ARKI_SELF_INSPECTION_V0','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'repo':str(root),'branch':git('branch','--show-current'),'head':git('rev-parse','HEAD'),
        'tracked_python_modules':len(py),'tracked_test_files':len(tests),'contract_candidates':contracts[:100],
        'risks':risks,'canonical_mutations':0,'normative_validation':'NOT_EXECUTED',
        'architectural_autocorrection':'NOT_IMPLEMENTED','status':'OBSERVATIONAL_ONLY'}
print(json.dumps(report,indent=2,ensure_ascii=False))
