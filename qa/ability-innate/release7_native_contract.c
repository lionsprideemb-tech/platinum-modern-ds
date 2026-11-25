/* QA-only portable C99 contract. No DS enum, save schema or ROM allocation. */
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef uint16_t Ability;
typedef struct { Ability primary[3], innate[3]; } Package;
typedef struct { Ability slots[4]; unsigned count; } Active;
typedef bool (*Eligible)(Ability, bool);
typedef bool (*Suppressed)(Ability, unsigned);
static bool resolve(const Package *p, unsigned pick, bool enabled,
                    const Package *override, bool authorized, Eligible eligible,
                    Suppressed suppressed, Active *out) {
    Active temp={{0},0};
    if (!p || !out || !eligible || !suppressed || pick>=3 || (override && !authorized)) return false;
    if (override) p=override;
    for(unsigned i=0;i<(enabled?4u:1u);++i) {
        Ability id=i?p->innate[i-1]:p->primary[pick];
        if (!id || !eligible(id,i!=0)) return false;
        if (!suppressed(id,i)) temp.slots[temp.count++]=id;
    }
    *out=temp; return true;
}
/* policy: -1 unresolved, 0 once, 1 per effective slot. */
static int dispatch(const Active *a, Ability id, int policy) {
    unsigned n=0; for(unsigned i=0;i<a->count;++i) n+=a->slots[i]==id;
    if(n>1 && policy!=0 && policy!=1) return -1;
    return n>1 && policy==0 ? 1 : (int)n;
}
/* Caller supplies dynamic effective move classification and ability membership. */
static uint32_t predator_power(uint16_t power, bool damaging, bool biting, bool slicing, bool active) {
    return active && damaging && (biting || slicing) ? (uint32_t)power*130u/100u : power;
}
/* Abstract status enum; NOT a native status bit assignment. */
typedef enum { CLEAR, OTHER, NERVE } Status;
static Status nerve_apply(Status s, bool active, bool damage, bool poison, bool contact, unsigned roll) {
    return s==CLEAR && active && damage && poison && contact && roll<30 ? NERVE : s;
}
typedef struct { bool major, poison_tick, paralysis_speed, paralysis_failure, native_poison, native_paralysis; } StatusView;
static StatusView nerve_view(Status s) {
    return (StatusView){s!=CLEAR,s==NERVE,s==NERVE,s==NERVE,false,false};
}
static Status generic_cure(Status s, bool cure) { return cure?CLEAR:s; }
/* Explicit slot supplied by caller; no implicit Knock Off priority approved. */
typedef struct { uint16_t item[2]; } Items;
static bool valid_items(Items p) { return !p.item[0] || !p.item[1] || p.item[0]!=p.item[1]; }
static bool swap_items(Items *a,unsigned i,Items *b,unsigned j) {
    if(!a||!b||a==b||i>1||j>1||!valid_items(*a)||!valid_items(*b)) return false;
    Items x=*a,y=*b;uint16_t t=x.item[i];x.item[i]=y.item[j];y.item[j]=t;
    if(!valid_items(x)||!valid_items(y)) return false;
    *a=x;*b=y;return true;
}
static bool remove_item(Items *a,unsigned i) {if(!a||i>1||!valid_items(*a)||!a->item[i])return false;a->item[i]=0;return true;}
static bool has_item(Items a) {return a.item[0]||a.item[1];}
/* Version is trusted external fixture metadata, never inferred from bytes. */
typedef bool (*Remap)(Ability,Ability *);
static bool recording_decode(uint8_t low,uint8_t high,unsigned version,Remap remap,Ability *out) {
    if(!out)return false;
    Ability a=(Ability)(low|((uint16_t)high<<8));
    if(version==10){if(high>3||!remap)return false;return remap(a,out);}
    if(version==16){*out=a;return true;}return false;
}
static bool eligible(Ability a,bool innate){return a!=99 && !(innate&&a==77);}
static bool suppressed(Ability a,unsigned slot){(void)slot;return a==12;}
static bool fixture_map(Ability a,Ability *out){if(a>929)return false;*out=(Ability)(a+1000);return true;}
int main(void) {
    unsigned pred=0,nerve=0,item=0,rec=0,routing=0;
    for(unsigned power=0;power<=65535;power++)for(unsigned mask=0;mask<16;mask++){
        bool d=mask&1,b=mask&2,s=mask&4,a=mask&8;
        uint32_t expected=(a&&d&&(b||s))?power+power*3/10:power;
        assert(predator_power((uint16_t)power,d,b,s,a)==expected);pred++;
    }
    for(unsigned st=0;st<3;st++)for(unsigned mask=0;mask<16;mask++)for(unsigned roll=0;roll<100;roll++){
        Status n=nerve_apply((Status)st,mask&1,mask&2,mask&4,mask&8,roll);
        assert(n==((st==CLEAR&&mask==15&&roll<30)?NERVE:(Status)st));
        StatusView v=nerve_view(n);assert(v.major==(n!=CLEAR));
        assert(v.poison_tick==(n==NERVE)&&v.paralysis_speed==(n==NERVE)&&v.paralysis_failure==(n==NERVE));
        assert(!v.native_poison&&!v.native_paralysis&&generic_cure(n,true)==CLEAR&&generic_cure(n,false)==n);nerve++;
    }
    for(unsigned a=0;a<4;a++)for(unsigned b=0;b<4;b++)for(unsigned c=0;c<4;c++)for(unsigned d=0;d<4;d++)for(unsigned i=0;i<2;i++)for(unsigned j=0;j<2;j++){
        Items x={{a,b}},y={{c,d}},origx=x,origy=y;
        Items expectedx=x,expectedy=y;expectedx.item[i]=y.item[j];expectedy.item[j]=x.item[i];
        bool ok=valid_items(x)&&valid_items(y)&&valid_items(expectedx)&&valid_items(expectedy);
        assert(swap_items(&x,i,&y,j)==ok);
        assert(!memcmp(&x,ok?&expectedx:&origx,sizeof x)&&!memcmp(&y,ok?&expectedy:&origy,sizeof y));item++;
    }
    Items bag={{1,2}};assert(remove_item(&bag,0)&&has_item(bag)&&bag.item[1]==2);assert(remove_item(&bag,1)&&!has_item(bag));item+=2;
    for(unsigned id=0;id<=65535;id++){Ability out=0;assert(recording_decode(id&255,id>>8,16,NULL,&out)&&out==id);rec++;if(id<1024){assert(recording_decode(id&255,id>>8,10,fixture_map,&out)==(id<=929));if(id<=929)assert(out==id+1000);rec++;}}
    Ability out=0;assert(!recording_decode(0,4,10,fixture_map,&out)&&!recording_decode(0,0,0,fixture_map,&out));rec+=2;
    Package p={{11,12,13},{11,14,15}},o={{21,22,23},{24,25,26}};Active x;
    for(unsigned k=0;k<3;k++)for(unsigned on=0;on<2;on++){assert(resolve(&p,k,on,NULL,false,eligible,suppressed,&x));assert(x.count==(on?4u:1u)-(k==1));routing++;}
    assert(resolve(&p,0,true,NULL,false,eligible,suppressed,&x)&&dispatch(&x,11,-1)==-1&&dispatch(&x,11,0)==1&&dispatch(&x,11,1)==2);routing++;
    assert(!resolve(&p,0,true,&o,false,eligible,suppressed,&x));routing++;
    assert(resolve(&p,0,true,&o,true,eligible,suppressed,&x)&&x.slots[0]==21&&x.slots[3]==26);routing++;
    p.innate[0]=77;assert(!resolve(&p,0,true,NULL,false,eligible,suppressed,&x)&&resolve(&p,0,false,NULL,false,eligible,suppressed,&x));routing++;
    printf("predator=%u nerve=%u item=%u recording=%u routing=%u\n",pred,nerve,item,rec,routing);return 0;
}
