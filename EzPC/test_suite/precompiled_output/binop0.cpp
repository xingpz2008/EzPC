#include<vector>
#include<math.h>
#include<cstdlib>
#include<iostream>
#include<fstream>

using namespace std;

uint32_t public_lrshift(uint32_t x, uint32_t y){
return (x >> y);
}

int32_t public_lrshift(int32_t x, uint32_t y){
return ((int32_t)(((uint32_t)x) >> y));
}

uint64_t public_lrshift(uint64_t x, uint64_t y){
return (x >> y);
}

int64_t public_lrshift(int64_t x, uint64_t y){
return ((int64_t)(((uint64_t)x) >> y));
}

template<typename T>
vector<T> make_vector(size_t size) {
return std::vector<T>(size);
}

template <typename T, typename... Args>
auto make_vector(size_t first, Args... sizes)
{
auto inner = make_vector<T>(sizes...);
return vector<decltype(inner)>(first, inner);
}

template<typename T>
ostream& operator<< (ostream &os, const vector<T> &v)
{
for(auto it = v.begin (); it != v.end (); ++it) {
os << *it << endl;
}
return os;
}


#include "ezpc.h"
ABYParty *party;
Circuit* ycirc;
Circuit* acirc;
Circuit* bcirc;
uint32_t bitlen = 32;
output_queue out_q;

share* signedgtbl(share* x, share* y){

share* ux = x;

share* uy = y;
/* Temporary variable for sub-expression on source location: (5,28-5,33) */
int32_t __tac_var1 = ( (int32_t)1 <<  (int32_t)31);
/* Temporary variable for sub-expression on source location: (5,28-5,33) */
share* __tac_var2 = put_cons32_gate(ycirc, __tac_var1);

share* signBitX = ycirc->PutANDGate(x, __tac_var2);
/* Temporary variable for sub-expression on source location: (6,28-6,33) */
int32_t __tac_var3 = __tac_var1;
/* Temporary variable for sub-expression on source location: (6,28-6,33) */
share* __tac_var4 = __tac_var2;

share* signBitY = ycirc->PutANDGate(y, __tac_var2);
/* Temporary variable for sub-expression on source location: (7,10-7,29) */
share* __tac_var5 = ycirc->PutXORGate(signBitX, signBitY);
/* Temporary variable for sub-expression on source location: (7,33-7,35) */
share* __tac_var6 = put_cons32_gate(ycirc,  (uint32_t)0);
/* Temporary variable for sub-expression on source location: (7,9-7,35) */
share* __tac_var7 = ycirc->PutGTGate(__tac_var5, __tac_var6);
/* Temporary variable for sub-expression on source location: (7,52-7,54) */
share* __tac_var8 = __tac_var6;
/* Temporary variable for sub-expression on source location: (7,41-7,54) */
share* __tac_var9 = ycirc->PutGTGate(signBitX, __tac_var6);
/* Temporary variable for sub-expression on source location: (7,58-7,63) */
share* __tac_var10 = put_cons1_gate(ycirc, 0);
/* Temporary variable for sub-expression on source location: (7,66-7,70) */
share* __tac_var11 = put_cons1_gate(ycirc, 1);
/* Temporary variable for sub-expression on source location: (7,40-7,70) */
share* __tac_var12 = ycirc->PutMUXGate(__tac_var10, __tac_var11, __tac_var9);
/* Temporary variable for sub-expression on source location: (7,75-7,82) */
share* __tac_var13 = ycirc->PutGTGate(ux, uy);
/* Temporary variable for sub-expression on source location: (7,8-7,83) */
share* __tac_var14 = ycirc->PutMUXGate(__tac_var12, __tac_var13, __tac_var7);
return __tac_var14;
}

share* signedarshiftbl(share* x, uint32_t y){

share* ux = x;
/* Temporary variable for sub-expression on source location: (15,28-15,33) */
int32_t __tac_var15 = ( (int32_t)1 <<  (int32_t)31);
/* Temporary variable for sub-expression on source location: (15,28-15,33) */
share* __tac_var16 = put_cons32_gate(ycirc, __tac_var15);

share* signBitX = ycirc->PutANDGate(x, __tac_var16);
/* Temporary variable for sub-expression on source location: (16,21-16,23) */
share* __tac_var17 = put_cons32_gate(ycirc,  (uint32_t)0);
/* Temporary variable for sub-expression on source location: (16,10-16,23) */
share* __tac_var18 = ycirc->PutGTGate(signBitX, __tac_var17);
/* Temporary variable for sub-expression on source location: (16,28-16,30) */
share* __tac_var19 = __tac_var17;
/* Temporary variable for sub-expression on source location: (16,35-16,37) */
share* __tac_var20 = __tac_var17;
/* Temporary variable for sub-expression on source location: (16,35-16,42) */
share* __tac_var21 = ycirc->PutSUBGate(__tac_var17, ux);
/* Temporary variable for sub-expression on source location: (16,34-16,48) */
share* __tac_var22 = arithmetic_right_shift(ycirc, __tac_var21, y);
/* Temporary variable for sub-expression on source location: (16,28-16,49) */
share* __tac_var23 = ycirc->PutSUBGate(__tac_var17, __tac_var22);
/* Temporary variable for sub-expression on source location: (16,54-16,61) */
share* __tac_var24 = arithmetic_right_shift(ycirc, ux, y);
/* Temporary variable for sub-expression on source location: (16,9-16,62) */
share* __tac_var25 = ycirc->PutMUXGate(__tac_var23, __tac_var24, __tac_var18);
return __tac_var25;
}

share* unsignedltbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (20,9-20,14) */
share* __tac_var26 = ycirc->PutGTGate(y, x);
return __tac_var26;
}

share* signedltbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (23,9-23,14) */
share* __tac_var27 = signedgtbl(y, x);
return __tac_var27;
}

share* unsignedleqbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (27,10-27,15) */
share* __tac_var28 = ycirc->PutGTGate(x, y);
/* Temporary variable for sub-expression on source location: (27,8-27,16) */
share* __tac_var29 = ((BooleanCircuit *) ycirc)->PutINVGate(__tac_var28);
return __tac_var29;
}

share* signedleqbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (30,10-30,15) */
share* __tac_var30 = signedgtbl(x, y);
/* Temporary variable for sub-expression on source location: (30,8-30,16) */
share* __tac_var31 = ((BooleanCircuit *) ycirc)->PutINVGate(__tac_var30);
return __tac_var31;
}

share* unsignedgeqbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (34,10-34,15) */
share* __tac_var32 = ycirc->PutGTGate(y, x);
/* Temporary variable for sub-expression on source location: (34,8-34,16) */
share* __tac_var33 = ((BooleanCircuit *) ycirc)->PutINVGate(__tac_var32);
return __tac_var33;
}

share* signedgeqbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (37,10-37,15) */
share* __tac_var34 = signedgtbl(y, x);
/* Temporary variable for sub-expression on source location: (37,8-37,16) */
share* __tac_var35 = ((BooleanCircuit *) ycirc)->PutINVGate(__tac_var34);
return __tac_var35;
}

share* unsignedequalsbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (41,11-41,16) */
share* __tac_var36 = unsignedltbl(x, y);
/* Temporary variable for sub-expression on source location: (41,9-41,17) */
share* __tac_var37 = ((BooleanCircuit *) ycirc)->PutINVGate(__tac_var36);
/* Temporary variable for sub-expression on source location: (41,25-41,30) */
share* __tac_var38 = unsignedltbl(y, x);
/* Temporary variable for sub-expression on source location: (41,23-41,31) */
share* __tac_var39 = ((BooleanCircuit *) ycirc)->PutINVGate(__tac_var38);
/* Temporary variable for sub-expression on source location: (41,8-41,32) */
share* __tac_var40 = ycirc->PutANDGate(__tac_var37, __tac_var39);
return __tac_var40;
}

share* signedequalsbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (44,11-44,16) */
share* __tac_var41 = signedltbl(x, y);
/* Temporary variable for sub-expression on source location: (44,9-44,17) */
share* __tac_var42 = ((BooleanCircuit *) ycirc)->PutINVGate(__tac_var41);
/* Temporary variable for sub-expression on source location: (44,25-44,30) */
share* __tac_var43 = signedltbl(y, x);
/* Temporary variable for sub-expression on source location: (44,23-44,31) */
share* __tac_var44 = ((BooleanCircuit *) ycirc)->PutINVGate(__tac_var43);
/* Temporary variable for sub-expression on source location: (44,8-44,32) */
share* __tac_var45 = ycirc->PutANDGate(__tac_var42, __tac_var44);
return __tac_var45;
}

share* longDivision(share* x, share* y, uint32_t getQuotient){

share* q = put_cons32_gate(ycirc,  (uint32_t)0);

share* divisor = q;

share* cond = put_cons1_gate(ycirc, 0);
for (uint32_t iter =  (int32_t)0; iter <  (int32_t)32; iter++){

uint32_t i = ( (int32_t)31 - iter);
divisor = left_shift(ycirc, divisor,  (uint32_t)1);
/* Temporary variable for sub-expression on source location: (61,32-61,39) */
uint32_t __tac_var46 = ( (uint32_t)1 << i);
/* Temporary variable for sub-expression on source location: (61,32-61,39) */
share* __tac_var47 = put_cons32_gate(ycirc, __tac_var46);
/* Temporary variable for sub-expression on source location: (61,27-61,40) */
share* __tac_var48 = ycirc->PutANDGate(x, __tac_var47);
/* Temporary variable for sub-expression on source location: (61,26-61,47) */
share* __tac_var49 = logical_right_shift(ycirc, __tac_var48, i);
divisor = ycirc->PutADDGate(divisor, __tac_var49);
cond = unsignedgeqbl(divisor, y);
/* Temporary variable for sub-expression on source location: (63,22-63,36) */
share* __tac_var50 = ycirc->PutSUBGate(divisor, y);
divisor = ycirc->PutMUXGate(__tac_var50, divisor, cond);
q = left_shift(ycirc, q,  (uint32_t)1);
/* Temporary variable for sub-expression on source location: (65,19-65,21) */
share* __tac_var51 = put_cons32_gate(ycirc,  (uint32_t)1);
/* Temporary variable for sub-expression on source location: (65,15-65,21) */
share* __tac_var52 = ycirc->PutADDGate(q, __tac_var51);
q = ycirc->PutMUXGate(__tac_var52, q, cond);
}
/* Temporary variable for sub-expression on source location: (68,9-68,34) */
share* __tac_var53 = getQuotient ? q : divisor;
return __tac_var53;
}

share* unsigneddivbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (71,8-71,32) */
share* __tac_var54 = longDivision(x, y, 1);
return __tac_var54;
}

share* unsigneddival(share* x, share* y){

share* bx = ycirc->PutA2YGate(x);

share* by = ycirc->PutA2YGate(y);
/* Temporary variable for sub-expression on source location: (76,8-76,13) */
share* __tac_var55 = unsigneddivbl(bx, by);
return __tac_var55;
}

share* signeddivbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (79,23-79,24) */
share* __tac_var56 = put_cons32_gate(ycirc,  (int32_t)0);

share* isXNeg = signedltbl(x, __tac_var56);
/* Temporary variable for sub-expression on source location: (80,23-80,24) */
share* __tac_var57 = __tac_var56;

share* isYNeg = signedltbl(y, __tac_var56);
/* Temporary variable for sub-expression on source location: (81,26-81,27) */
share* __tac_var58 = __tac_var56;
/* Temporary variable for sub-expression on source location: (81,26-81,31) */
share* __tac_var59 = ycirc->PutSUBGate(__tac_var56, x);

share* ux = ycirc->PutMUXGate(__tac_var59, x, isXNeg);
/* Temporary variable for sub-expression on source location: (82,26-82,27) */
share* __tac_var60 = __tac_var56;
/* Temporary variable for sub-expression on source location: (82,26-82,31) */
share* __tac_var61 = ycirc->PutSUBGate(__tac_var56, y);

share* uy = ycirc->PutMUXGate(__tac_var61, y, isYNeg);

share* ures = unsigneddivbl(ux, uy);

share* isResNeg = ycirc->PutXORGate(isXNeg, isYNeg);
/* Temporary variable for sub-expression on source location: (85,21-85,23) */
share* __tac_var62 = put_cons32_gate(ycirc,  (uint32_t)0);
/* Temporary variable for sub-expression on source location: (85,21-85,30) */
share* __tac_var63 = ycirc->PutSUBGate(__tac_var62, ures);
/* Temporary variable for sub-expression on source location: (85,9-85,38) */
share* __tac_var64 = ycirc->PutMUXGate(__tac_var63, ures, isResNeg);
return __tac_var64;
}

share* signeddival(share* x, share* y){

share* bx = ycirc->PutA2YGate(x);

share* by = ycirc->PutA2YGate(y);
/* Temporary variable for sub-expression on source location: (90,8-90,13) */
share* __tac_var65 = signeddivbl(bx, by);
return __tac_var65;
}

share* unsignedmodbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (98,8-98,33) */
share* __tac_var66 = longDivision(x, y, 0);
return __tac_var66;
}

share* unsignedmodal(share* x, share* y){

share* bx = ycirc->PutA2YGate(x);

share* by = ycirc->PutA2YGate(y);
/* Temporary variable for sub-expression on source location: (103,8-103,13) */
share* __tac_var67 = unsignedmodbl(bx, by);
return __tac_var67;
}

share* signedmodbl(share* x, share* y){
/* Temporary variable for sub-expression on source location: (106,23-106,24) */
share* __tac_var68 = put_cons32_gate(ycirc,  (int32_t)0);

share* isXNeg = signedltbl(x, __tac_var68);
/* Temporary variable for sub-expression on source location: (107,23-107,24) */
share* __tac_var69 = __tac_var68;

share* isYNeg = signedltbl(y, __tac_var68);
/* Temporary variable for sub-expression on source location: (108,26-108,27) */
share* __tac_var70 = __tac_var68;
/* Temporary variable for sub-expression on source location: (108,26-108,31) */
share* __tac_var71 = ycirc->PutSUBGate(__tac_var68, x);

share* ux = ycirc->PutMUXGate(__tac_var71, x, isXNeg);
/* Temporary variable for sub-expression on source location: (109,26-109,27) */
share* __tac_var72 = __tac_var68;
/* Temporary variable for sub-expression on source location: (109,26-109,31) */
share* __tac_var73 = ycirc->PutSUBGate(__tac_var68, y);

share* uy = ycirc->PutMUXGate(__tac_var73, y, isYNeg);

share* urem = unsignedmodbl(ux, uy);
/* Temporary variable for sub-expression on source location: (111,19-111,21) */
share* __tac_var74 = put_cons32_gate(ycirc,  (uint32_t)0);
/* Temporary variable for sub-expression on source location: (111,19-111,28) */
share* __tac_var75 = ycirc->PutSUBGate(__tac_var74, urem);
/* Temporary variable for sub-expression on source location: (111,9-111,36) */
share* __tac_var76 = ycirc->PutMUXGate(__tac_var75, urem, isXNeg);
return __tac_var76;
}

share* signedmodal(share* x, share* y){

share* bx = ycirc->PutA2YGate(x);

share* by = ycirc->PutA2YGate(y);
/* Temporary variable for sub-expression on source location: (116,8-116,13) */
share* __tac_var77 = signedmodbl(bx, by);
return __tac_var77;
}


int64_t ezpc_main (e_role role, char* address, uint16_t port, seclvl seclvl,
uint32_t nvals, uint32_t nthreads, e_mt_gen_alg mt_alg,
e_sharing sharing) {
party = new ABYParty(role, address, port, seclvl, bitlen, nthreads, mt_alg, 520000000);
std::vector<Sharing*>& sharings = party->GetSharings();
ycirc = (sharings)[S_YAO]->GetCircuitBuildRoutine();
acirc = (sharings)[S_ARITH]->GetCircuitBuildRoutine();
bcirc = (sharings)[S_BOOL]->GetCircuitBuildRoutine();


share* a = put_cons32_gate(acirc,  (uint32_t)5);

share* b = put_cons32_gate(acirc,  (uint32_t)10);

share* c;

share* e;

uint32_t d;
c = acirc->PutADDGate(a, b);
c = acirc->PutSUBGate(a, b);
c = acirc->PutMULGate(a, b);
/* Temporary variable for sub-expression on source location: (130,7-130,9) */
share* __tac_var78 = put_cons32_gate(acirc,  (uint32_t)4);
c = unsigneddival(b, __tac_var78);
d = ( (uint32_t)10 %  (uint32_t)4);
/* Temporary variable for sub-expression on source location: (132,5-132,6) */
share* __tac_var79 = ycirc->PutA2YGate(b);
/* Temporary variable for sub-expression on source location: (132,5-132,10) */
share* __tac_var80 = arithmetic_right_shift(ycirc, __tac_var79,  (uint32_t)2);
c = acirc->PutY2AGate(__tac_var80, bcirc);
/* Temporary variable for sub-expression on source location: (133,5-133,6) */
share* __tac_var81 = __tac_var79;
/* Temporary variable for sub-expression on source location: (133,5-133,10) */
share* __tac_var82 = left_shift(ycirc, __tac_var79,  (uint32_t)2);
c = acirc->PutY2AGate(__tac_var82, bcirc);
/* Temporary variable for sub-expression on source location: (134,5-134,6) */
share* __tac_var83 = ycirc->PutA2YGate(a);
/* Temporary variable for sub-expression on source location: (134,7-134,8) */
share* __tac_var84 = __tac_var79;
/* Temporary variable for sub-expression on source location: (134,5-134,8) */
share* __tac_var85 = ycirc->PutXORGate(__tac_var83, __tac_var79);
c = acirc->PutY2AGate(__tac_var85, bcirc);
/* Temporary variable for sub-expression on source location: (135,5-135,6) */
share* __tac_var86 = __tac_var83;
/* Temporary variable for sub-expression on source location: (135,7-135,8) */
share* __tac_var87 = __tac_var79;
/* Temporary variable for sub-expression on source location: (135,5-135,8) */
share* __tac_var88 = ycirc->PutANDGate(__tac_var83, __tac_var79);
c = acirc->PutY2AGate(__tac_var88, bcirc);
/* Temporary variable for sub-expression on source location: (136,5-136,6) */
share* __tac_var89 = __tac_var83;
/* Temporary variable for sub-expression on source location: (136,7-136,8) */
share* __tac_var90 = __tac_var79;
/* Temporary variable for sub-expression on source location: (136,5-136,8) */
share* __tac_var91 = ((BooleanCircuit *) ycirc)->PutORGate(__tac_var83, __tac_var79);
c = acirc->PutY2AGate(__tac_var91, bcirc);
/* Temporary variable for sub-expression on source location: (137,5-137,10) */
int32_t __tac_var92 = (pow( (int32_t)2,  (int32_t)10));
c = put_cons32_gate(acirc, __tac_var92);
/* Temporary variable for sub-expression on source location: (138,5-138,6) */
share* __tac_var93 = __tac_var79;
/* Temporary variable for sub-expression on source location: (138,5-138,11) */
share* __tac_var94 = logical_right_shift(ycirc, __tac_var79,  (uint32_t)2);
c = acirc->PutY2AGate(__tac_var94, bcirc);
/* Temporary variable for sub-expression on source location: (139,5-139,16) */
uint32_t __tac_var95 = (1 && 0);
e = put_cons1_gate(ycirc, __tac_var95);
/* Temporary variable for sub-expression on source location: (140,5-140,17) */
uint32_t __tac_var96 = (0 || 0);
e = put_cons1_gate(ycirc, __tac_var96);
/* Temporary variable for sub-expression on source location: (141,5-141,15) */
uint32_t __tac_var97 = (0 ^ 1);
e = put_cons1_gate(ycirc, __tac_var97);
/* Temporary variable for sub-expression on source location: (142,5-142,6) */
share* __tac_var98 = __tac_var83;
/* Temporary variable for sub-expression on source location: (142,7-142,8) */
share* __tac_var99 = __tac_var79;
e = ycirc->PutGTGate(__tac_var83, __tac_var79);
/* Temporary variable for sub-expression on source location: (143,6-143,7) */
share* __tac_var100 = __tac_var83;
/* Temporary variable for sub-expression on source location: (143,9-143,10) */
share* __tac_var101 = __tac_var79;
e = unsignedequalsbl(__tac_var83, __tac_var79);
/* Temporary variable for sub-expression on source location: (144,5-144,6) */
share* __tac_var102 = __tac_var83;
/* Temporary variable for sub-expression on source location: (144,8-144,9) */
share* __tac_var103 = __tac_var79;
e = unsignedgeqbl(__tac_var83, __tac_var79);
/* Temporary variable for sub-expression on source location: (145,5-145,6) */
share* __tac_var104 = __tac_var83;
/* Temporary variable for sub-expression on source location: (145,8-145,9) */
share* __tac_var105 = __tac_var79;
e = unsignedleqbl(__tac_var83, __tac_var79);
/* Temporary variable for sub-expression on source location: (146,5-146,6) */
share* __tac_var106 = __tac_var83;
/* Temporary variable for sub-expression on source location: (146,7-146,8) */
share* __tac_var107 = __tac_var79;
e = unsignedltbl(__tac_var83, __tac_var79);
party->ExecCircuit();
flush_output_queue(out_q, role, bitlen);
return 0;
}
