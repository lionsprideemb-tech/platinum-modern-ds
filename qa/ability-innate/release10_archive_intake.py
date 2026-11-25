"""Offline exact-tree ZIP intake, QA only. No checkout/ROM/build/network.
Usage: python3 release10_archive_intake.py OUTPUT mercury.zip platinum.zip hg.zip community.zip
On success, OUTPUT contains raw verified Git-archive trees; use only for QA replay.
"""
import hashlib, json, pathlib, stat, sys, tempfile, zipfile
PINS = {
 'mercury': ('2aa5c71abc978e832d90fee94a2b13f7bf40caa7',658,57190256,{}),
 'pokeplatinum': ('1fc0c552ddab856ba026a0132a3eb39de8d91b9c',27669,138280413,{}),
 'hg-engine': ('ee31c262b8a9f30ca799c598076019ec0ae43adf',32437,128126630,{'tools/source/nitrogfx':'a8fd94a3e582ded71eda5b9f5f0c69258544bb22'}),
 'community-moves': ('0a182c33f6c01e25b90ee14ae13c278c7637e9ef',1493,6907829,{})}
def oid(kind, data):
 return hashlib.sha1(kind.encode()+b' '+str(len(data)).encode()+b'\0'+data).hexdigest()
def add(root, parts, entry):
 for part in parts[:-1]:
  root=root.setdefault(part,{})
  if not isinstance(root,dict): raise ValueError('path collision')
 if parts[-1] in root: raise ValueError('duplicate path')
 root[parts[-1]]=entry
def tree_oid(root):
 entries=[]
 for name,v in root.items():
  n=name.encode('utf-8'); mode,sha=('40000',tree_oid(v)) if isinstance(v,dict) else v
  entries.append((n+(b'/' if mode=='40000' else b''),mode.encode()+b' '+n+b'\0'+bytes.fromhex(sha)))
 return oid('tree',b''.join(v for _,v in sorted(entries)))
def verify_zip(zpath, dest, pin):
 expected,count,byte_count,links=pin
 root={}; names=set(); total=0; files=0; prefix=None
 with zipfile.ZipFile(zpath) as z:
  infos=z.infolist()
  if len(infos)>count*3+100: raise ValueError('excess entries')
  for i in infos:
   raw=i.filename; parts=raw.rstrip('/').split('/')
   if not all(parts) or any(p in ('.','..','.git') or '\\' in p or '\x00' in p or ':' in p for p in parts): raise ValueError('unsafe path')
   if raw in names: raise ValueError('duplicate ZIP member')
   names.add(raw)
   if prefix is None: prefix=parts[0]
   if prefix!=parts[0]: raise ValueError('multiple archive roots')
   if i.is_dir(): continue
   if len(parts)<2 or i.flag_bits&1: raise ValueError('invalid archive member')
   rel=parts[1:]; path='/'.join(rel)
   if any(path==l or path.startswith(l+'/') for l in links): raise ValueError('unexpected submodule bytes')
   unix=(i.external_attr>>16)&0xffff
   # git archive ZIP uses DOS creator/zero attributes for ordinary files.
   if i.create_system==0 and i.external_attr==0: mode='100644'
   elif i.create_system==3 and stat.S_IFMT(unix)==stat.S_IFREG: mode='100755' if unix&0o111 else '100644'
   else: raise ValueError('unsupported archive mode')
   files+=1; total+=i.file_size
   if files>count or total>byte_count: raise ValueError('excess archive bytes')
   data=z.read(i)
   if len(data)!=i.file_size: raise ValueError('size mismatch')
   add(root,rel,(mode,oid('blob',data)))
   target=dest.joinpath(*rel); target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb') as f: f.write(data)
   target.chmod(0o755 if mode=='100755' else 0o644)
  for path,sha in links.items(): add(root,path.split('/'),('160000',sha))
  if (files,total,tree_oid(root))!=(count,byte_count,expected): raise ValueError('exact tree mismatch')
 return {'tree':expected,'files':files,'bytes':total,'gitlinks':links}
def main():
 if len(sys.argv)!=6: raise SystemExit(__doc__)
 out=pathlib.Path(sys.argv[1]).absolute()
 if out.exists(): raise ValueError('fresh output required')
 out.parent.resolve(strict=True)
 # Stage into a private sibling; no partial input is promoted.
 with tempfile.TemporaryDirectory(dir=out.parent,prefix='.mr10-intake-') as t:
  staging=pathlib.Path(t)/'verified'; staging.mkdir(); report={}
  for (key,pin),zpath in zip(PINS.items(),sys.argv[2:]):
   dest=staging/key; dest.mkdir(); report[key]=verify_zip(zpath,dest,pin)
  (staging/'INTAKE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
  if out.exists(): raise ValueError('output appeared')
  staging.rename(out)
 print('EXACT_SOURCE_TREE_INTAKE_PASS; no replay or native certification')
if __name__=='__main__': main()
