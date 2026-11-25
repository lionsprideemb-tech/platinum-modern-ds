/* QA-only native-compatible migration helper. No storage or ID allocation.
 * Explicit trusted outer schema required; do not infer format from high bits.
 * Source migration blob: 504ef92d5f40334b2f53272cbf9a782dea5bb6b6
 * Caller validates full record checksum, flags, and registry eligibility.
 * Retired mappings are retained as tombstones, never silently reassigned.
 */
#ifndef MERCURY_QA_RECORDING_MIGRATION_H
#define MERCURY_QA_RECORDING_MIGRATION_H
#include <stdint.h>
#include <stdbool.h>
enum MercuryQARegistryVersion { MERCURY_QA_DS10_STAGING = 10, MERCURY_QA_DS16_V3 = 16 };
static const uint16_t mercuryQAOldCustomToNew[619] = {
    1043, 1044, 1045, 1046, 1047, 972, 1048, 1049, 1050, 1051, 1052, 467, 498, 591, 593, 376,
    338, 1053, 1054, 1055, 1056, 521, 1057, 1058, 1059, 952, 953, 954, 955, 956, 957, 958,
    959, 960, 961, 1060, 1061, 1062, 384, 1063, 632, 633, 634, 635, 636, 637, 638, 639,
    640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655,
    656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671,
    962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 922, 923, 924, 925, 926, 927,
    928, 929, 930, 931, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984,
    985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000,
    1001, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708,
    709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 899, 900, 901, 902, 903, 904,
    905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920,
    921, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733,
    734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749,
    750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765,
    766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781,
    782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797,
    798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813,
    814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829,
    830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845,
    846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861,
    862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877,
    878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893,
    894, 895, 896, 897, 898, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942,
    943, 944, 945, 946, 947, 948, 949, 950, 951, 1002, 1003, 1004, 1005, 1009, 1011, 1012,
    1016, 1021, 1022, 1023, 1024, 1025, 626, 627, 628, 629, 630, 631, 672, 673, 674, 675,
    676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691,
    692, 693, 1026, 1027, 1028, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1064,
    320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 333, 334, 335, 346, 350,
    352, 356, 359, 360, 361, 363, 366, 367, 369, 370, 373, 374, 375, 381, 386, 389,
    393, 394, 396, 397, 399, 403, 404, 409, 412, 418, 426, 428, 431, 436, 440, 441,
    445, 451, 452, 454, 457, 458, 461, 463, 471, 474, 476, 477, 485, 487, 488, 490,
    491, 492, 493, 513, 517, 518, 549, 552, 555, 559, 563, 564, 568, 575, 577, 579,
    582, 595, 597, 620, 621, 539, 472, 528, 562, 607, 462, 415, 442, 507, 520, 443,
    466, 481, 401, 478, 505, 532, 545, 470, 567, 516, 576, 347, 446, 574, 417, 534,
    514, 611, 425, 617, 578, 500, 456, 437, 501, 343, 337, 459, 600, 495, 583, 434,
    548, 480, 527, 468, 557, 497, 479, 581, 473, 541, 602, 388, 392, 531, 345, 449,
    556, 427, 533, 592, 411, 614, 465, 398, 405, 336, 542, 469, 416, 414, 484, 435,
    506, 438, 455, 486, 524, 613, 482, 540, 368, 1006, 1015, 1042, 331, 332, 339, 340,
    341, 342, 344, 348, 351, 354, 355, 357, 377, 383, 390,
};
static inline bool MercuryQA_MigrateAbility(uint16_t old, enum MercuryQARegistryVersion version, uint16_t *out)
{
    if (!out) return false;
    if (version == MERCURY_QA_DS16_V3) {
        if (old > 1066) return false;
        *out = old;
        return true;
    }
    if (version != MERCURY_QA_DS10_STAGING || old > 929) return false;
    *out = old <= 310 ? old : mercuryQAOldCustomToNew[old - 311];
    return true;
}
static inline bool MercuryQA_DecodeRecordingAbility(uint8_t low, uint8_t high,
    enum MercuryQARegistryVersion version, uint16_t *out)
{
    if (version == MERCURY_QA_DS10_STAGING && high > 3) return false;
    return MercuryQA_MigrateAbility((uint16_t)(low | ((uint16_t)high << 8)), version, out);
}
static inline bool MercuryQA_DecodeBoxAbility(uint8_t low, uint8_t marks, uint8_t high,
    enum MercuryQARegistryVersion version, uint16_t *out)
{
    if (version == MERCURY_QA_DS10_STAGING) {
        if (high != 0) return false;
        return MercuryQA_DecodeRecordingAbility(low, marks >> 6, version, out);
    }
    if (version != MERCURY_QA_DS16_V3 || (marks & 0xC0) != 0) return false;
    return MercuryQA_DecodeRecordingAbility(low, high, version, out);
}
static inline bool MercuryQA_EncodeMigratedAbility(uint16_t id, uint8_t *low,
    uint8_t *marks, uint8_t *high)
{
    if (!low || !marks || !high || id > 1066) return false;
    *low = (uint8_t)id;
    *marks &= 0x3F;
    *high = (uint8_t)(id >> 8);
    return true;
}
#endif
