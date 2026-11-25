// Offline model only; no live ROM or save writes.
// Run: node storage16_model.cjs <migration.json> <partition.json>
const fs=require('node:fs');
function runPrototype(migration,partition){
 const assert=(v,m)=>{if(!v)throw Error(m)};
 const oldToNew=new Map(migration.current_ds_custom_remap.map(r=>[r.old_ds_id,r.new_id]));
 const retired=new Set(partition.abilities.filter(r=>r.retired).map(r=>r.id));
 const A=0,B=32,LOW=A+13,MARK=A+14,HIGH=B+26;
 function checksum(a){let c=0;for(let i=0;i<a.length;i+=2)c=(c+a[i]+256*a[i+1])&65535;return c}
 function readLegacy(a){return a[LOW]|((a[MARK]&192)<<2)}
 function readRecovered(a){let hi=a[HIGH];if(hi===0)hi=(a[MARK]&192)>>6;return a[LOW]|(hi<<8)}
 function write(a,id){assert(Number.isInteger(id)&&id>=0&&id<=65535,"range");a[LOW]=id&255;a[HIGH]=id>>>8;a[MARK]&=63}
 function upgrade(a,format){assert(a.length===128,"record length");assert(["ds10-staging","ds16-v3"].includes(format),"explicit source format required");if(format==="ds16-v3")return a.slice();assert(a[HIGH]===0,"old high byte is not clean; hold for review");let id=readLegacy(a);assert(id<=310||oldToNew.has(id),"unknown legacy ID");let target=id<=310?id:oldToNew.get(id);let out=a.slice();write(out,target);return out}
 let a=new Uint8Array(128),roundtrips=0,legacy=0,checksums=0,preserved=0,recordings=0;
 for(let id=0;id<=65535;id++)for(let marks=0;marks<64;marks++){a[MARK]=marks|192;write(a,id);assert(readRecovered(a)===id&&(a[MARK]&63)===marks&&a[MARK]===marks,"16bit roundtrip");roundtrips++}
 for(let id=0;id<=1023;id++)for(let marks=0;marks<64;marks++){a[HIGH]=0;a[LOW]=id&255;a[MARK]=marks|((id>>>8)<<6);assert(readRecovered(a)===id&&(a[MARK]&63)===marks,"legacy fallback");legacy++}
 for(let id=0;id<=929;id++)for(let marks=0;marks<64;marks++){let a=Uint8Array.from({length:128},(_,i)=>(i*17+id*3+marks)&255);a[HIGH]=0;a[LOW]=id&255;a[MARK]=marks|((id>>>8)<<6);let oldSum=checksum(a),b=upgrade(a,"ds10-staging");let expected=id<=310?id:oldToNew.get(id);assert(readRecovered(b)===expected&&(b[MARK]&63)===marks,"semantic migration");assert(b.length===a.length,"length");for(let i=0;i<128;i++)if(![LOW,MARK,HIGH].includes(i))assert(a[i]===b[i],"unrelated byte changed");preserved++;let sum=checksum(b),delta=0;for(let i of [12,14,58])delta+=(b[i]+256*b[i+1])-(a[i]+256*a[i+1]);assert(((oldSum+delta)&65535)===sum,"checksum delta");checksums++;assert(upgrade(b,"ds16-v3").every((x,i)=>x===b[i]),"repeat migration");}
 for(let id=0;id<=65535;id++){let flags=(id*13)&7,record=(id>>>8)<<3|flags;assert(((id&255)|(((record>>>3)&255)<<8))===id&&(record&7)===flags,"battle recording model");recordings++}
 assert(oldToNew.size===619&&new Set(oldToNew.values()).size===619,"migration map not bijective");
 assert(oldToNew.get(907)===524&&oldToNew.get(690)===1004&&retired.has(524)&&retired.has(1004),"retired identities");
 let rejected=0;for(let mode of ["unknown","ds10-staging"]){let a=new Uint8Array(128);a[HIGH]=1;try{upgrade(a,mode)}catch(e){rejected++}}assert(rejected===2,"fail closed");
 let oldRecordingLoss=0;for(let id=256;id<=1023;id++){a[HIGH]=0;a[LOW]=id&255;a[MARK]=(id>>>8)<<6;let exported=a[LOW]|(a[HIGH]<<8);if(exported!==readRecovered(a))oldRecordingLoss++}
 return {roundtrips,legacy,semantic_migration_cases:preserved,checksum_cases:checksums,recording_cases:recordings,old_recording_export_loss_cases:oldRecordingLoss,rejected_invalid_examples:rejected,remap_entries:oldToNew.size,retired_ids:[...retired],status:"PASS_OFFLINE_MODEL"};
}
const [migration,partition]=process.argv.slice(2).map(p=>JSON.parse(fs.readFileSync(p,'utf8')));
console.log(JSON.stringify(runPrototype(migration,partition),null,2));
