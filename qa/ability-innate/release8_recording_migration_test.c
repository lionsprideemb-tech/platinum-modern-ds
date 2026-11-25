#include <assert.h>
#include <stdio.h>
#include "release8_recording_migration.h"
int main(void) {
    unsigned rec=0,box=0,modern=0,round=0,negative=0;
    for(unsigned id=0;id<1024;id++) {
        uint16_t out=65535;
        bool ok=MercuryQA_DecodeRecordingAbility(id&255,id>>8,MERCURY_QA_DS10_STAGING,&out);
        assert(ok==(id<=929));
        if(ok) assert(out==(id<=310?id:mercuryQAOldCustomToNew[id-311])); else assert(out==65535);
        rec++;
        for(unsigned marks=0;marks<64;marks++) {
            out=65535;
            bool b=MercuryQA_DecodeBoxAbility(id&255,marks|((id>>8)<<6),0,MERCURY_QA_DS10_STAGING,&out);
            assert(b==ok);
            if(b) {
                uint8_t l=0,m=marks|192,h=0;uint16_t v=65535;
                assert(MercuryQA_EncodeMigratedAbility(out,&l,&m,&h)&&m==marks);
                assert(MercuryQA_DecodeBoxAbility(l,m,h,MERCURY_QA_DS16_V3,&v)&&v==out);round++;
            }
            box++;
        }
    }
    for(unsigned id=0;id<65536;id++) {
        uint16_t out=65535;
        bool ok=MercuryQA_DecodeRecordingAbility(id&255,id>>8,MERCURY_QA_DS16_V3,&out);
        assert(ok==(id<=1066));if(ok)assert(out==id);else assert(out==65535);modern++;
    }
    uint16_t x=0;assert(!MercuryQA_DecodeRecordingAbility(1,4,MERCURY_QA_DS10_STAGING,&x));negative++;
    assert(!MercuryQA_DecodeBoxAbility(1,0,1,MERCURY_QA_DS10_STAGING,&x));negative++;
    assert(!MercuryQA_DecodeBoxAbility(1,64,0,MERCURY_QA_DS16_V3,&x));negative++;
    assert(!MercuryQA_DecodeRecordingAbility(1,0,(enum MercuryQARegistryVersion)0,&x));negative++;
    printf("legacy_recording=%u legacy_box=%u modern_recording=%u marking_roundtrip=%u negative=%u\n",rec,box,modern,round,negative);
    return 0;
}
