@ ===== Pokemon Mercury Redux: Instant Honey Tree System =====
@ One Honey = one immediate premium encounter. No real-time wait, no tree lottery/cooldown.
@ Regional pools are intentionally rare/rewarding and can span generations.

MercuryHoneyTree_EventScript_Floaroma::
    lock
    faceplayer
    checkitem ITEM_HONEY
    goto_if_eq VAR_RESULT, FALSE, MercuryHoneyTree_EventScript_NoHoney
    msgbox MercuryHoneyTree_Text_AskSlather, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, MercuryHoneyTree_EventScript_Cancel
    removeitem ITEM_HONEY
    msgbox MercuryHoneyTree_Text_Slathered, MSGBOX_DEFAULT
    random 100
    goto_if_lt VAR_RESULT, 15, MercuryHoneyTree_EventScript_F_Aipom
    goto_if_lt VAR_RESULT, 30, MercuryHoneyTree_EventScript_F_Teddiursa
    goto_if_lt VAR_RESULT, 45, MercuryHoneyTree_EventScript_F_Cutiefly
    goto_if_lt VAR_RESULT, 60, MercuryHoneyTree_EventScript_F_Applin
    goto_if_lt VAR_RESULT, 75, MercuryHoneyTree_EventScript_F_Heracross
    goto_if_lt VAR_RESULT, 85, MercuryHoneyTree_EventScript_F_Pinsir
    goto_if_lt VAR_RESULT, 90, MercuryHoneyTree_EventScript_F_Scyther
    goto MercuryHoneyTree_EventScript_F_Munchlax

MercuryHoneyTree_EventScript_F_Aipom::
    setwildbattle SPECIES_AIPOM, 16
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_F_Teddiursa::
    setwildbattle SPECIES_TEDDIURSA, 16
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_F_Cutiefly::
    setwildbattle SPECIES_CUTIEFLY, 16
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_F_Applin::
    setwildbattle SPECIES_APPLIN, 17
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_F_Heracross::
    setwildbattle SPECIES_HERACROSS, 17
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_F_Pinsir::
    setwildbattle SPECIES_PINSIR, 17
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_F_Scyther::
    setwildbattle SPECIES_SCYTHER, 18
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_F_Munchlax::
    setwildbattle SPECIES_MUNCHLAX, 18
    goto MercuryHoneyTree_EventScript_StartBattle

@ Eterna Forest regional pool: rarer woodland species and stronger long-term catches.
MercuryHoneyTree_EventScript_Eterna::
    lock
    faceplayer
    checkitem ITEM_HONEY
    goto_if_eq VAR_RESULT, FALSE, MercuryHoneyTree_EventScript_NoHoney
    msgbox MercuryHoneyTree_Text_AskSlather, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, MercuryHoneyTree_EventScript_Cancel
    removeitem ITEM_HONEY
    msgbox MercuryHoneyTree_Text_Slathered, MSGBOX_DEFAULT
    random 100
    goto_if_lt VAR_RESULT, 15, MercuryHoneyTree_EventScript_E_Heracross
    goto_if_lt VAR_RESULT, 30, MercuryHoneyTree_EventScript_E_Scyther
    goto_if_lt VAR_RESULT, 40, MercuryHoneyTree_EventScript_E_Pinsir
    goto_if_lt VAR_RESULT, 50, MercuryHoneyTree_EventScript_E_Phantump
    goto_if_lt VAR_RESULT, 60, MercuryHoneyTree_EventScript_E_Applin
    goto_if_lt VAR_RESULT, 70, MercuryHoneyTree_EventScript_E_Teddiursa
    goto_if_lt VAR_RESULT, 80, MercuryHoneyTree_EventScript_E_Munchlax
    goto_if_lt VAR_RESULT, 90, MercuryHoneyTree_EventScript_E_Slakoth
    goto_if_lt VAR_RESULT, 95, MercuryHoneyTree_EventScript_E_Larvesta
    goto MercuryHoneyTree_EventScript_E_Cutiefly

MercuryHoneyTree_EventScript_E_Heracross::
    setwildbattle SPECIES_HERACROSS, 20
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_E_Scyther::
    setwildbattle SPECIES_SCYTHER, 20
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_E_Pinsir::
    setwildbattle SPECIES_PINSIR, 20
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_E_Phantump::
    setwildbattle SPECIES_PHANTUMP, 19
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_E_Applin::
    setwildbattle SPECIES_APPLIN, 20
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_E_Teddiursa::
    setwildbattle SPECIES_TEDDIURSA, 19
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_E_Munchlax::
    setwildbattle SPECIES_MUNCHLAX, 20
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_E_Slakoth::
    setwildbattle SPECIES_SLAKOTH, 19
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_E_Larvesta::
    setwildbattle SPECIES_LARVESTA, 20
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_E_Cutiefly::
    setwildbattle SPECIES_CUTIEFLY, 19
    goto MercuryHoneyTree_EventScript_StartBattle

@ Route 215 regional pool: premium rain-road / martial grove encounters.
@ Platinum Route 215 has a Honey Tree; Mercury keeps it instant and worthwhile.
MercuryHoneyTree_EventScript_Route215::
    lock
    faceplayer
    checkitem ITEM_HONEY
    goto_if_eq VAR_RESULT, FALSE, MercuryHoneyTree_EventScript_NoHoney
    msgbox MercuryHoneyTree_Text_AskSlather, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, MercuryHoneyTree_EventScript_Cancel
    removeitem ITEM_HONEY
    msgbox MercuryHoneyTree_Text_Slathered, MSGBOX_DEFAULT
    random 100
    goto_if_lt VAR_RESULT, 15, MercuryHoneyTree_EventScript_215_Oranguru
    goto_if_lt VAR_RESULT, 30, MercuryHoneyTree_EventScript_215_Passimian
    goto_if_lt VAR_RESULT, 45, MercuryHoneyTree_EventScript_215_Heracross
    goto_if_lt VAR_RESULT, 55, MercuryHoneyTree_EventScript_215_FarfetchdGalar
    goto_if_lt VAR_RESULT, 65, MercuryHoneyTree_EventScript_215_Munchlax
    goto_if_lt VAR_RESULT, 75, MercuryHoneyTree_EventScript_215_Zangoose
    goto_if_lt VAR_RESULT, 85, MercuryHoneyTree_EventScript_215_Seviper
    goto_if_lt VAR_RESULT, 90, MercuryHoneyTree_EventScript_215_Scyther
    goto_if_lt VAR_RESULT, 95, MercuryHoneyTree_EventScript_215_Larvesta
    goto MercuryHoneyTree_EventScript_215_Slakoth

MercuryHoneyTree_EventScript_215_Oranguru::
    setwildbattle SPECIES_ORANGURU, 31
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_215_Passimian::
    setwildbattle SPECIES_PASSIMIAN, 31
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_215_Heracross::
    setwildbattle SPECIES_HERACROSS, 31
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_215_FarfetchdGalar::
    setwildbattle SPECIES_FARFETCHD_GALAR, 31
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_215_Munchlax::
    setwildbattle SPECIES_MUNCHLAX, 31
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_215_Zangoose::
    setwildbattle SPECIES_ZANGOOSE, 32
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_215_Seviper::
    setwildbattle SPECIES_SEVIPER, 32
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_215_Scyther::
    setwildbattle SPECIES_SCYTHER, 32
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_215_Larvesta::
    setwildbattle SPECIES_LARVESTA, 32
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_215_Slakoth::
    setwildbattle SPECIES_SLAKOTH, 32
    goto MercuryHoneyTree_EventScript_StartBattle

@ Route 214 regional pool: premium rocky-scrub Honey encounters.
@ Platinum Route 214 has a Honey Tree; Mercury keeps it instant and route-specific.
MercuryHoneyTree_EventScript_Route214::
    lock
    faceplayer
    checkitem ITEM_HONEY
    goto_if_eq VAR_RESULT, FALSE, MercuryHoneyTree_EventScript_NoHoney
    msgbox MercuryHoneyTree_Text_AskSlather, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, MercuryHoneyTree_EventScript_Cancel
    removeitem ITEM_HONEY
    msgbox MercuryHoneyTree_Text_Slathered, MSGBOX_DEFAULT
    random 100
    goto_if_lt VAR_RESULT, 15, MercuryHoneyTree_EventScript_214_Teddiursa
    goto_if_lt VAR_RESULT, 30, MercuryHoneyTree_EventScript_214_Shuckle
    goto_if_lt VAR_RESULT, 45, MercuryHoneyTree_EventScript_214_Heracross
    goto_if_lt VAR_RESULT, 55, MercuryHoneyTree_EventScript_214_Pinsir
    goto_if_lt VAR_RESULT, 65, MercuryHoneyTree_EventScript_214_Kecleon
    goto_if_lt VAR_RESULT, 75, MercuryHoneyTree_EventScript_214_Pancham
    goto_if_lt VAR_RESULT, 85, MercuryHoneyTree_EventScript_214_Munchlax
    goto_if_lt VAR_RESULT, 90, MercuryHoneyTree_EventScript_214_Joltik
    goto_if_lt VAR_RESULT, 95, MercuryHoneyTree_EventScript_214_Larvesta
    goto MercuryHoneyTree_EventScript_214_Sewaddle

MercuryHoneyTree_EventScript_214_Teddiursa::
    setwildbattle SPECIES_TEDDIURSA, 33
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_214_Shuckle::
    setwildbattle SPECIES_SHUCKLE, 33
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_214_Heracross::
    setwildbattle SPECIES_HERACROSS, 33
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_214_Pinsir::
    setwildbattle SPECIES_PINSIR, 33
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_214_Kecleon::
    setwildbattle SPECIES_KECLEON, 34
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_214_Pancham::
    setwildbattle SPECIES_PANCHAM, 34
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_214_Munchlax::
    setwildbattle SPECIES_MUNCHLAX, 34
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_214_Joltik::
    setwildbattle SPECIES_JOLTIK, 34
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_214_Larvesta::
    setwildbattle SPECIES_LARVESTA, 35
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_214_Sewaddle::
    setwildbattle SPECIES_SEWADDLE, 34
    goto MercuryHoneyTree_EventScript_StartBattle

@ Route 213 regional pool: premium coastal resort-grove encounters.
@ Platinum Route 213 has a Honey Tree. Mercury keeps the instant-Honey rule,
@ but deliberately uses a fresh cross-generation pool instead of repeating
@ the earlier Floaroma/Eterna/214/215 rewards.
@ Physical placement is deferred to the final Platinum-based Route 213 map.
MercuryHoneyTree_EventScript_Route213::
    lock
    faceplayer
    checkitem ITEM_HONEY
    goto_if_eq VAR_RESULT, FALSE, MercuryHoneyTree_EventScript_NoHoney
    msgbox MercuryHoneyTree_Text_AskSlather, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, MercuryHoneyTree_EventScript_Cancel
    removeitem ITEM_HONEY
    msgbox MercuryHoneyTree_Text_Slathered, MSGBOX_DEFAULT
    random 100
    goto_if_lt VAR_RESULT, 15, MercuryHoneyTree_EventScript_213_Pikachu
    goto_if_lt VAR_RESULT, 30, MercuryHoneyTree_EventScript_213_Pachirisu
    goto_if_lt VAR_RESULT, 40, MercuryHoneyTree_EventScript_213_Emolga
    goto_if_lt VAR_RESULT, 50, MercuryHoneyTree_EventScript_213_Dedenne
    goto_if_lt VAR_RESULT, 60, MercuryHoneyTree_EventScript_213_Togedemaru
    goto_if_lt VAR_RESULT, 70, MercuryHoneyTree_EventScript_213_Morpeko
    goto_if_lt VAR_RESULT, 80, MercuryHoneyTree_EventScript_213_Karrablast
    goto_if_lt VAR_RESULT, 90, MercuryHoneyTree_EventScript_213_Shelmet
    goto_if_lt VAR_RESULT, 95, MercuryHoneyTree_EventScript_213_Charjabug
    goto MercuryHoneyTree_EventScript_213_Tropius

MercuryHoneyTree_EventScript_213_Pikachu::
    setwildbattle SPECIES_PIKACHU, 36
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_213_Pachirisu::
    setwildbattle SPECIES_PACHIRISU, 36
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_213_Emolga::
    setwildbattle SPECIES_EMOLGA, 36
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_213_Dedenne::
    setwildbattle SPECIES_DEDENNE, 36
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_213_Togedemaru::
    setwildbattle SPECIES_TOGEDEMARU, 37
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_213_Morpeko::
    setwildbattle SPECIES_MORPEKO, 37
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_213_Karrablast::
    setwildbattle SPECIES_KARRABLAST, 37
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_213_Shelmet::
    setwildbattle SPECIES_SHELMET, 37
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_213_Charjabug::
    setwildbattle SPECIES_CHARJABUG, 38
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_213_Tropius::
    setwildbattle SPECIES_TROPIUS, 38
    goto MercuryHoneyTree_EventScript_StartBattle


@ Route 212 South regional pool: premium rain-marsh tree encounters.
@ Platinum Route 212 South has a Honey Tree. Mercury keeps the instant-Honey rule
@ and gives this tree a distinct damp-woodland / marsh-insect rare pool.
@ Physical placement is deferred to the final Platinum-based Route 212 South map.
MercuryHoneyTree_EventScript_Route212South::
    lock
    faceplayer
    checkitem ITEM_HONEY
    goto_if_eq VAR_RESULT, FALSE, MercuryHoneyTree_EventScript_NoHoney
    msgbox MercuryHoneyTree_Text_AskSlather, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, MercuryHoneyTree_EventScript_Cancel
    removeitem ITEM_HONEY
    msgbox MercuryHoneyTree_Text_Slathered, MSGBOX_DEFAULT
    random 100
    goto_if_lt VAR_RESULT, 15, MercuryHoneyTree_EventScript_212S_Nincada
    goto_if_lt VAR_RESULT, 30, MercuryHoneyTree_EventScript_212S_Spinarak
    goto_if_lt VAR_RESULT, 45, MercuryHoneyTree_EventScript_212S_Grubbin
    goto_if_lt VAR_RESULT, 55, MercuryHoneyTree_EventScript_212S_Dewpider
    goto_if_lt VAR_RESULT, 65, MercuryHoneyTree_EventScript_212S_Dwebble
    goto_if_lt VAR_RESULT, 75, MercuryHoneyTree_EventScript_212S_Venipede
    goto_if_lt VAR_RESULT, 85, MercuryHoneyTree_EventScript_212S_Scyther
    goto_if_lt VAR_RESULT, 90, MercuryHoneyTree_EventScript_212S_Heracross
    goto_if_lt VAR_RESULT, 95, MercuryHoneyTree_EventScript_212S_Snom
    goto MercuryHoneyTree_EventScript_212S_Larvesta

MercuryHoneyTree_EventScript_212S_Nincada::
    setwildbattle SPECIES_NINCADA, 37
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212S_Spinarak::
    setwildbattle SPECIES_SPINARAK, 37
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212S_Grubbin::
    setwildbattle SPECIES_GRUBBIN, 37
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212S_Dewpider::
    setwildbattle SPECIES_DEWPIDER, 38
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212S_Dwebble::
    setwildbattle SPECIES_DWEBBLE, 38
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212S_Venipede::
    setwildbattle SPECIES_VENIPEDE, 38
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212S_Scyther::
    setwildbattle SPECIES_SCYTHER, 39
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212S_Heracross::
    setwildbattle SPECIES_HERACROSS, 39
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212S_Snom::
    setwildbattle SPECIES_SNOM, 39
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212S_Larvesta::
    setwildbattle SPECIES_LARVESTA, 40
    goto MercuryHoneyTree_EventScript_StartBattle

@ Route 212 North regional pool: premium mansion-estate tree encounters.
@ Platinum Route 212 North has a Honey Tree near the Pokemon Mansion. Mercury uses
@ a distinct companion / fairy / estate rarity pool with immediate encounters.
@ Physical placement is deferred to the final Platinum-based Route 212 North map.
MercuryHoneyTree_EventScript_Route212North::
    lock
    faceplayer
    checkitem ITEM_HONEY
    goto_if_eq VAR_RESULT, FALSE, MercuryHoneyTree_EventScript_NoHoney
    msgbox MercuryHoneyTree_Text_AskSlather, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, MercuryHoneyTree_EventScript_Cancel
    removeitem ITEM_HONEY
    msgbox MercuryHoneyTree_Text_Slathered, MSGBOX_DEFAULT
    random 100
    goto_if_lt VAR_RESULT, 15, MercuryHoneyTree_EventScript_212N_Togepi
    goto_if_lt VAR_RESULT, 30, MercuryHoneyTree_EventScript_212N_Happiny
    goto_if_lt VAR_RESULT, 40, MercuryHoneyTree_EventScript_212N_Porygon
    goto_if_lt VAR_RESULT, 50, MercuryHoneyTree_EventScript_212N_Hatenna
    goto_if_lt VAR_RESULT, 60, MercuryHoneyTree_EventScript_212N_Milcery
    goto_if_lt VAR_RESULT, 70, MercuryHoneyTree_EventScript_212N_Eevee
    goto_if_lt VAR_RESULT, 80, MercuryHoneyTree_EventScript_212N_Skitty
    goto_if_lt VAR_RESULT, 85, MercuryHoneyTree_EventScript_212N_Minccino
    goto_if_lt VAR_RESULT, 90, MercuryHoneyTree_EventScript_212N_Chansey
    goto MercuryHoneyTree_EventScript_212N_Indeedee

MercuryHoneyTree_EventScript_212N_Togepi::
    setwildbattle SPECIES_TOGEPI, 38
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212N_Happiny::
    setwildbattle SPECIES_HAPPINY, 38
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212N_Porygon::
    setwildbattle SPECIES_PORYGON, 39
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212N_Hatenna::
    setwildbattle SPECIES_HATENNA, 39
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212N_Milcery::
    setwildbattle SPECIES_MILCERY, 39
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212N_Eevee::
    setwildbattle SPECIES_EEVEE, 39
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212N_Skitty::
    setwildbattle SPECIES_SKITTY, 39
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212N_Minccino::
    setwildbattle SPECIES_MINCCINO, 39
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212N_Chansey::
    setwildbattle SPECIES_CHANSEY, 40
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_212N_Indeedee::
    setwildbattle SPECIES_INDEEDEE, 40
    goto MercuryHoneyTree_EventScript_StartBattle

@ Route 218 regional pool: premium canal-side / maritime approach encounters.
@ Platinum Route 218 has a Honey Tree. Mercury keeps the instant-Honey rule.
@ Physical placement is deferred until the final Platinum-derived Route 218 map exists.
MercuryHoneyTree_EventScript_Route218::
    lock
    faceplayer
    checkitem ITEM_HONEY
    goto_if_eq VAR_RESULT, FALSE, MercuryHoneyTree_EventScript_NoHoney
    msgbox MercuryHoneyTree_Text_AskSlather, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, MercuryHoneyTree_EventScript_Cancel
    removeitem ITEM_HONEY
    msgbox MercuryHoneyTree_Text_Slathered, MSGBOX_DEFAULT
    random 100
    goto_if_lt VAR_RESULT, 15, MercuryHoneyTree_EventScript_218_Elekid
    goto_if_lt VAR_RESULT, 30, MercuryHoneyTree_EventScript_218_Pawmi
    goto_if_lt VAR_RESULT, 40, MercuryHoneyTree_EventScript_218_MeowthGalar
    goto_if_lt VAR_RESULT, 50, MercuryHoneyTree_EventScript_218_Munchlax
    goto_if_lt VAR_RESULT, 60, MercuryHoneyTree_EventScript_218_Scyther
    goto_if_lt VAR_RESULT, 70, MercuryHoneyTree_EventScript_218_Klefki
    goto_if_lt VAR_RESULT, 80, MercuryHoneyTree_EventScript_218_Duraludon
    goto_if_lt VAR_RESULT, 90, MercuryHoneyTree_EventScript_218_Rotom
    goto_if_lt VAR_RESULT, 95, MercuryHoneyTree_EventScript_218_Porygon
    goto MercuryHoneyTree_EventScript_218_VoltorbHisui

MercuryHoneyTree_EventScript_218_Elekid::
    setwildbattle SPECIES_ELEKID, 42
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_218_Pawmi::
    setwildbattle SPECIES_PAWMI, 42
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_218_MeowthGalar::
    setwildbattle SPECIES_MEOWTH_GALAR, 42
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_218_Munchlax::
    setwildbattle SPECIES_MUNCHLAX, 43
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_218_Scyther::
    setwildbattle SPECIES_SCYTHER, 43
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_218_Klefki::
    setwildbattle SPECIES_KLEFKI, 43
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_218_Duraludon::
    setwildbattle SPECIES_DURALUDON, 44
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_218_Rotom::
    setwildbattle SPECIES_ROTOM, 44
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_218_Porygon::
    setwildbattle SPECIES_PORYGON, 44
    goto MercuryHoneyTree_EventScript_StartBattle
MercuryHoneyTree_EventScript_218_VoltorbHisui::
    setwildbattle SPECIES_VOLTORB_HISUI, 44
    goto MercuryHoneyTree_EventScript_StartBattle

MercuryHoneyTree_EventScript_StartBattle::
    msgbox MercuryHoneyTree_Text_PokemonCameImmediately, MSGBOX_DEFAULT
    dowildbattle
    release
    end

MercuryHoneyTree_EventScript_NoHoney::
    msgbox MercuryHoneyTree_Text_NoHoney, MSGBOX_DEFAULT
    release
    end

MercuryHoneyTree_EventScript_Cancel::
    msgbox MercuryHoneyTree_Text_Cancel, MSGBOX_DEFAULT
    release
    end

MercuryHoneyTree_Text_AskSlather:
    .string "The bark gives off a sweet scent.\p"
    .string "Slather HONEY on this tree?$"

MercuryHoneyTree_Text_Slathered:
    .string "{PLAYER} slathered HONEY on the tree.\p"
    .string "The scent spreads through the branches at once...$"

MercuryHoneyTree_Text_PokemonCameImmediately:
    .string "The branches rustle-\n"
    .string "a rare Pokemon came for the HONEY!$"

MercuryHoneyTree_Text_NoHoney:
    .string "This sweet-smelling tree could attract unusual\n"
    .string "Pokemon, but you don't have any HONEY.$"

MercuryHoneyTree_Text_Cancel:
    .string "The tree remains quiet.$"
