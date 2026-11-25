import pathlib, tempfile, subprocess, sys, json
import release11_archive_replay as m
import release10_archive_intake as intake

def reject(fn):
    try: fn()
    except (ValueError,RuntimeError,subprocess.CalledProcessError): return
    raise AssertionError('unexpected acceptance')
with tempfile.TemporaryDirectory() as temp:
    root=pathlib.Path(temp); r=root/'repo'; r.mkdir()
    def git(*args): return subprocess.check_output(['git','-C',str(r),*args]).decode().strip()
    git('init','-q'); git('config','user.email','qa@example.invalid'); git('config','user.name','QA')
    (r/'nested').mkdir(); (r/'nested'/'run').write_bytes(b'#!/bin/sh\n'); (r/'nested'/'run').chmod(0o755); (r/'data').write_bytes(b'\x00\xff')
    git('add','.'); git('commit','-qm','fixture'); link=git('rev-parse','HEAD'); git('update-index','--add','--cacheinfo','160000,'+link+',nested/link'); git('commit','-qm','link')
    z=root/'source.zip'; git('archive','--format=zip','--prefix=src/','--output='+str(z),'HEAD'); d=root/'extracted'; d.mkdir(); pin=(git('rev-parse','HEAD^{tree}'),2,12,{'nested/link':link})
    intake.verify_zip(z,d,pin); m.verify_disk(d,pin)
    (d/'data').write_bytes(b'\x00\xfe'); reject(lambda:m.verify_disk(d,pin)); (d/'data').write_bytes(b'\x00\xff')
    (d/'nested'/'run').chmod(0o644); reject(lambda:m.verify_disk(d,pin)); (d/'nested'/'run').chmod(0o755)
    (d/'extra').symlink_to('data'); reject(lambda:m.verify_disk(d,pin)); (d/'extra').unlink(); m.verify_disk(d,pin)
    reject(lambda:m.pinned(z,'0'*40)); assert m.pinned(z,m.oid('blob',z.read_bytes()))==z.read_bytes()
    logs=root/'logs'; logs.mkdir(); s={'completed':[],'failed':None}; snapshots=[]
    steps=[{'name':'one','body':'printf ok > result'},{'name':'two','body':'printf failure; exit 9'},{'name':'three','body':'touch forbidden'}]
    reject(lambda:m.run_steps(steps,d,logs,s,lambda:snapshots.append(json.loads(json.dumps(s)))))
    assert s=={'completed':['one'],'failed':'two'} and not (d/'forbidden').exists() and (logs/'02.log').read_text()=='failure'
    (d/'vendor/pokeplatinum/generated').mkdir(parents=True); (d/'vendor/pokeplatinum/generated/abilities.txt').write_text('A\nB\n'); (d/'mr10c-implemented-abilities.txt').write_text('B\n'); ns={'registry':['A','B'],'keep_crosswalk':[{'token':'B'}],'historical_crosswalk':[]}; assert m.registry_check(d,ns)=={'namespace':2,'implemented':1,'required':1}
    (d/'mr10c-implemented-abilities.txt').write_text('A\n'); reject(lambda:m.registry_check(d,ns))
    (d/'mr10c-implemented-abilities.txt').write_text('B\nB\n'); reject(lambda:m.registry_check(d,ns))
    if {p.name for p in pathlib.Path('/sys/class/net').iterdir()}!={'lo'}: reject(m.offline_check); print('non-isolated environment correctly rejected')
print('PASS: exact tree rehash, pinned bytes, tamper/mode/symlink rejection, first-stage failure stop, registry coverage/duplicate rejection')
