import tempfile,subprocess,pathlib,zipfile
import release10_archive_intake as m
with tempfile.TemporaryDirectory() as t:
 r=pathlib.Path(t)/'repo';r.mkdir();g=lambda *a: subprocess.check_output(['git','-C',str(r),*a]).decode().strip();g('init','-q');g('config','user.email','qa@example.invalid');g('config','user.name','QA');(r/'x').write_bytes(b'abc\x00');(r/'nested').mkdir();(r/'nested'/'run').write_text('#!/bin/sh\n');(r/'nested'/'run').chmod(0o755);g('add','.');g('commit','-qm','test');tree=g('rev-parse','HEAD^{tree}');z=pathlib.Path(t)/'source.zip';g('archive','--format=zip','--prefix=src/','--output='+str(z),'HEAD');d=pathlib.Path(t)/'verified';d.mkdir();size=sum((r/p).stat().st_size for p in ['x','nested/run']);pin=(tree,2,size,{});print(m.verify_zip(z,d,pin));assert (d/'x').read_bytes()==b'abc\x00';assert (d/'nested/run').stat().st_mode&0o111
 for i,bad in enumerate([(tree,1,size,{}),('0'*40,2,size,{}),(tree,2,size-1,{})]):
  d=pathlib.Path(t)/f'bad{i}';d.mkdir()
  try:m.verify_zip(z,d,bad);raise AssertionError('accepted wrong pin')
  except ValueError as e:print('rejected:',e)
 z2=pathlib.Path(t)/'unsafe.zip'
 with zipfile.ZipFile(z2,'w') as f:f.writestr('src/../escape','bad')
 d=pathlib.Path(t)/'unsafe';d.mkdir()
 try:m.verify_zip(z2,d,pin);raise AssertionError('accepted traversal')
 except ValueError as e:print('rejected:',e)
 g('update-index','--add','--cacheinfo','160000,'+g('rev-parse','HEAD')+',submodule');link=g('rev-parse','HEAD');g('commit','-qm','link');z3=pathlib.Path(t)/'link.zip';g('archive','--format=zip','--prefix=src/','--output='+str(z3),'HEAD');d=pathlib.Path(t)/'link';d.mkdir();print(m.verify_zip(z3,d,(g('rev-parse','HEAD^{tree}'),2,size,{'submodule':link})))
 print('PASS: 2 exact Git archive acceptance cases; 4 negative cases')
