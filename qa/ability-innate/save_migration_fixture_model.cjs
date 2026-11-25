// Offline synthetic encrypted BoxPokemon test, no real save writes.
const perm=[[0,1,2,3],[0,1,3,2],[0,2,1,3],[0,3,1,2],[0,2,3,1],[0,3,2,1],[1,0,2,3],[1,0,3,2],[2,0,1,3],[3,0,1,2],[2,0,3,1],[3,0,2,1],[1,2,0,3],[1,3,0,2],[2,1,0,3],[3,1,0,2],[2,3,0,1],[3,2,0,1],[1,2,3,0],[1,3,2,0],[2,1,3,0],[3,1,2,0],[2,3,1,0],[3,2,1,0]];
function run(migration,perm){
 const assert=(v,m)=>{if(!v)throw Error(m)}, map=new Map(migration.current_ds_custom_remap.map(a=>[a.old_ds_id,a.new_id]));
 function read16(b,i){return b[i]|b[i+1]<<8}function put16(b,i,n){b[i]=n&255;b[i+1]=(n>>>8)&255}
 function checksum(b){let n=0;for(let i=0;i<128;i+=2)n=(n+read16(b,i))&65535;return n}
 function crypt(b,seed){let c=b.slice();for(let i=0;i<c.length;i+=2){seed=(Math.imul(seed,1103515245)+24691)>>>0;put16(c,i,read16(c,i)^(seed>>>16))}return c}
 function offsets(b){const personality=(b[0]|b[1]<<8|b[2]<<16|b[3]<<24)>>>0;const p=perm[((personality&0x3e000)>>>13)%24];return [p[0]*32+13,p[0]*32+14,p[1]*32+26]}
 function decode(b){assert(b.length===136,"record length");assert((read16(b,4)&6)===0,"not clean encrypted record");let d=crypt(b.slice(8),read16(b,6));assert(checksum(d)===read16(b,6),"checksum mismatch");return d}
 function seal(b,d){let c=b.slice(),sum=checksum(d);put16(c,6,sum);c.set(crypt(d,sum),8);return c}
 function upgrade(b,format){assert(format==="ds10-staging"||format==="ds16-v3","format provenance required");const d=decode(b);const [lo,mark,hi]=offsets(b);if(format==="ds16-v3"){assert(!(d[mark]&192),"stale legacy bits");return b.slice()}assert(d[hi]===0,"legacy high-byte collision");const id=d[lo]|((d[mark]&192)<<2);assert(id<=310||map.has(id),"unknown old ID");const target=id<=310?id:map.get(id);d[lo]=target&255;d[hi]=target>>>8;d[mark]&=63;return seal(b,d)}
 function recording(b,format){const migrated=upgrade(b,format),d=decode(migrated),[lo,mark,hi]=offsets(migrated);return d[lo]|d[hi]<<8}
 let fixtures=0,recordings=0,unchanged=0,rejections=0;
 for(let shuffle=0;shuffle<32;shuffle++)for(let id=0;id<=929;id++){const b=new Uint8Array(136),pid=(shuffle<<13)|7;b[0]=pid&255;b[1]=(pid>>>8)&255;b[2]=(pid>>>16)&255;const d=Uint8Array.from({length:128},(_,i)=>(i*71+id*13+shuffle)&255),[lo,mark,hi]=offsets(b),marks=(id+shuffle)&63;d[lo]=id&255;d[hi]=0;d[mark]=marks|((id>>>8)<<6);const original=seal(b,d),next=upgrade(original,"ds10-staging"),decoded=decode(next),target=id<=310?id:map.get(id);assert(decoded[lo]|(decoded[hi]<<8) ? (decoded[lo]|decoded[hi]<<8)===target : target===0,"mapped ID");assert(decoded[mark]===marks,"marks");assert(next.length===136,"size");assert(original.every((x,i)=>i>=6||x===next[i]),"header change");for(let i=0;i<128;i++)if(![lo,mark,hi].includes(i))assert(d[i]===decoded[i],"unrelated bytes");fixtures++;unchanged++;assert(recording(original,"ds10-staging")===target,"legacy recording export");recordings++;assert(upgrade(next,"ds16-v3").every((x,i)=>x===next[i]),"idempotence");
 if(id===0){let bad=original.slice();bad[8]^=1;for(const [buf,mode] of [[bad,"ds10-staging"],[original,"unknown"]]){let rejected=false;try{upgrade(buf,mode)}catch{rejected=true}assert(rejected,"invalid fixture accepted");rejections++}}
 }
 return {encrypted_fixtures:fixtures,unrelated_byte_preservation:unchanged,recording_exports:recordings,negative_cases:rejections,shuffle_cases:32,record_bytes:136,status:"PASS_SYNTHETIC_BOX_FIXTURES_NOT_NATIVE"};
}
console.log(JSON.stringify(run(JSON.parse(require('node:fs').readFileSync(process.argv[2],'utf8')),perm),null,2));
