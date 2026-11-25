"""QA source-only replay from four exact Git archives; run in an offline sandbox.
Usage: python3 release11_archive_replay.py PLAN NAMESPACE INTAKE OUTPUT MERCURY.zip PLATINUM.zip HG.zip COMMUNITY.zip
No native patch application, Git history synthesis, compilation, or ROM build.
"""
import hashlib, json, os, pathlib, re, shutil, stat, subprocess, sys

PLAN = 'a68c40c72b59d64bbb370504de505150137d944a'
NAMESPACE = 'd902d6ec26a43695a716f045dc880f5c1a3bd978'
INTAKE = '6a02ab5b5b4f155a083cd30908b8b7091aca3f83'
KEYS = ('mercury','pokeplatinum','hg-engine','community-moves')
PINS = dict(zip(KEYS,('4a7560f8b6cfe7fc19ee266365428c04dbeb5f98','c248fb3f8cc9934ded800e489567c5c0eeee92eb','5157c501dc0e6f88ef1654ab121352a5cc9ed7de','4250c4bfbb2e8dddd117160cec9e1e8395dfe9f7')))

def oid(kind, data):
    return hashlib.sha1(kind.encode()+b' '+str(len(data)).encode()+b'\0'+data).hexdigest()

def pinned(path, expected):
    data = pathlib.Path(path).read_bytes()
    if oid('blob',data)!=expected: raise ValueError('pinned blob mismatch: '+str(path))
    return data

def validate(plan, ns):
    steps=plan['steps']; registry=ns['registry']
    if plan['schema']!='mercury-release9-source-replay-plan' or plan['pins']!=PINS or len(steps)!=53: raise ValueError('plan shape/pins')
    if [steps[i]['name'] for i in (0,-2,-1)]!=['Apply Mercury Platinum overlay','Rebase all runtime mechanics onto final 16-bit Ability IDs','Restore missing runtime batches R1 through R8 (shared implemented registry)']: raise ValueError('stage order')
    if any(not s['body'] or re.search(r'\b(?:sudo|git clone|make rom|curl|wget|apt-get)\b',s['body']) for s in steps): raise ValueError('source-only plan')
    if steps[-1]['body'].count('--implemented-registry mr10c-implemented-abilities.txt')!=8: raise ValueError('shared registry')
    if len(registry)!=1067 or len(set(registry))!=1067 or len(ns['keep_crosswalk'])!=75 or len(ns['historical_crosswalk'])!=125: raise ValueError('namespace coverage')

def disk_tree(root, links):
    # Independently hash extracted file bytes/modes, rather than trusting intake report.
    count=total=0; seen=set()
    def walk(directory, prefix=''):
        nonlocal count,total
        entries=[]
        for p in directory.iterdir():
            rel=prefix+p.name; name=p.name.encode('utf-8'); mode=p.lstat().st_mode
            if p.name=='.git' or rel in links: raise ValueError('unexpected path: '+rel)
            if stat.S_ISDIR(mode):
                sha=walk(p,rel+'/'); m=b'40000'; sort=name+b'/'
            elif stat.S_ISREG(mode):
                data=p.read_bytes(); count+=1; total+=len(data); sha=oid('blob',data); m=b'100755' if mode&0o111 else b'100644'; sort=name
            else: raise ValueError('unsupported file type: '+rel)
            entries.append((sort,m+b' '+name+b'\0'+bytes.fromhex(sha)))
        for rel,sha in links.items():
            if rel.startswith(prefix) and '/' not in rel[len(prefix):]:
                name=rel[len(prefix):].encode(); seen.add(rel); entries.append((name,b'160000 '+name+b'\0'+bytes.fromhex(sha)))
        return oid('tree',b''.join(value for _,value in sorted(entries)))
    sha=walk(root)
    if seen!=set(links): raise ValueError('missing gitlink parent')
    return sha,count,total

def verify_disk(root, pin):
    tree,count,size,links=pin
    if disk_tree(root,links)!=(tree,count,size): raise ValueError('extracted tree mismatch: '+str(root))

def registry_check(work, ns):
    def lines(p): return [s.strip() for s in (work/p).read_text().splitlines() if s.strip()]
    actual=lines('vendor/pokeplatinum/generated/abilities.txt'); implemented=lines('mr10c-implemented-abilities.txt'); tokens=set(implemented)
    required={x['token'] for k in ('keep_crosswalk','historical_crosswalk') for x in ns[k]}
    if actual!=ns['registry'] or len(tokens)!=len(implemented) or not tokens<=set(actual) or not required<=tokens: raise ValueError('final registry mismatch')
    return {'namespace':len(actual),'implemented':len(tokens),'required':len(required)}

def run_steps(steps, work, logs, summary, report):
    for i,step in enumerate(steps,1):
        summary['failed']=step['name']; report()
        with (logs/f'{i:02}.log').open('wb') as log:
            subprocess.run(['bash','-e','-u','-o','pipefail','-c',step['body']],cwd=work,stdin=subprocess.DEVNULL,stdout=log,stderr=log,check=True,env={**os.environ,'GIT_TERMINAL_PROMPT':'0','PYTHONDONTWRITEBYTECODE':'1','BASH_ENV':'','ENV':''})
        summary['completed'].append(step['name']); summary['failed']=None; report()

def offline_check():
    # Refuse environments with any non-loopback network interface; this is a
    # conservative Linux preflight, not a substitute for sandbox isolation.
    interfaces={p.name for p in pathlib.Path('/sys/class/net').iterdir()}
    if interfaces!={'lo'}: raise RuntimeError('offline network namespace required')

def main():
    if len(sys.argv)!=9: raise SystemExit(__doc__)
    planfile,nsfile,intakefile,outfile,*archives=sys.argv[1:]
    plan=json.loads(pinned(planfile,PLAN)); ns=json.loads(pinned(nsfile,NAMESPACE)); code=pinned(intakefile,INTAKE); validate(plan,ns)
    intake={'__name__':'verified_intake'}; exec(compile(code,'verified_intake','exec'),intake)
    offline_check()
    out=pathlib.Path(outfile).absolute(); parent=out.parent.resolve(strict=True)
    if parent!=out.parent or out.exists() or out.is_symlink(): raise ValueError('fresh resolved output required')
    archives=[pathlib.Path(a).resolve(strict=True) for a in archives]
    if len(set(archives))!=4 or any(not p.is_file() for p in archives): raise ValueError('four distinct regular archives required')
    out.mkdir(mode=0o700); staging=out/'verified'; staging.mkdir(); logs=out/'logs'; logs.mkdir(); work=out/'work'
    summary={'status':'VERIFYING_ARCHIVES','completed':[],'failed':None,'sourceOnly':True,'nativeCertified':False,'sourcePins':PINS,'verifiedTrees':{}}
    def report():
        tmp=out/'report.tmp'; tmp.write_text(json.dumps(summary,indent=2)+'\n'); tmp.replace(out/'REPLAY_REPORT.json')
    try:
        report()
        for key,archive in zip(KEYS,archives):
            summary['failed']='archive:'+key; report(); dest=staging/key; dest.mkdir()
            pin=intake['PINS'][key]; proof=intake['verify_zip'](archive,dest,pin); verify_disk(dest,pin)
            summary['verifiedTrees'][key]=proof; report()
        summary['failed']='assemble verified trees'; report()
        (staging/'mercury').rename(work); vendor=work/'vendor'; vendor.mkdir(exist_ok=True)
        for key in KEYS[1:]:
            target=vendor/key
            if target.exists() or target.is_symlink(): raise ValueError('vendor path already exists: '+key)
            (staging/key).rename(target)
        staging.rmdir(); summary['failed']=None; summary['status']='IN_PROGRESS'; report()
        run_steps(plan['steps'],work,logs,summary,report)
        summary['failed']='final registry'; report(); summary['registry']=registry_check(work,ns)
        summary['failed']=None; summary['status']='SOURCE_REPLAY_PASS_NATIVE_UNTESTED'; report()
    except BaseException as e:
        summary['status']='BLOCKED'; summary['error']=str(e); report(); raise
if __name__=='__main__': main()
