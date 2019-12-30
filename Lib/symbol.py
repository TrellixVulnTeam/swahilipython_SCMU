"""Non-terminal symbols of Python grammar (kutoka "graminit.h")."""

#  This file ni automatically generated; please don't muck it up!
#
#  To update the symbols kwenye this file, 'cd' to the top directory of
#  the python source tree after building the interpreter na run:
#
#    python3 Tools/scripts/generate_symbol_py.py Include/graminit.h Lib/symbol.py
#
# ama just
#
#    make regen-symbol

#--start constants--
single_input = 256
file_input = 257
eval_input = 258
decorator = 259
decorators = 260
decorated = 261
async_funceleza = 262
funceleza = 263
parameters = 264
typedargslist = 265
tfpeleza = 266
varargslist = 267
vfpeleza = 268
stmt = 269
simple_stmt = 270
small_stmt = 271
expr_stmt = 272
annassign = 273
testlist_star_expr = 274
augassign = 275
del_stmt = 276
pass_stmt = 277
flow_stmt = 278
koma_stmt = 279
endelea_stmt = 280
return_stmt = 281
yield_stmt = 282
raise_stmt = 283
import_stmt = 284
import_name = 285
import_kutoka = 286
import_as_name = 287
dotted_as_name = 288
import_as_names = 289
dotted_as_names = 290
dotted_name = 291
global_stmt = 292
nonlocal_stmt = 293
assert_stmt = 294
compound_stmt = 295
async_stmt = 296
if_stmt = 297
while_stmt = 298
for_stmt = 299
try_stmt = 300
with_stmt = 301
with_item = 302
except_clause = 303
suite = 304
namedexpr_test = 305
test = 306
test_nocond = 307
lambeleza = 308
lambdef_nocond = 309
or_test = 310
and_test = 311
not_test = 312
comparison = 313
comp_op = 314
star_expr = 315
expr = 316
xor_expr = 317
and_expr = 318
shift_expr = 319
arith_expr = 320
term = 321
factor = 322
power = 323
atom_expr = 324
atom = 325
testlist_comp = 326
trailer = 327
subscriptlist = 328
subscript = 329
sliceop = 330
exprlist = 331
testlist = 332
dictorsetmaker = 333
classeleza = 334
arglist = 335
argument = 336
comp_iter = 337
sync_comp_kila = 338
comp_kila = 339
comp_ikiwa = 340
encoding_decl = 341
yield_expr = 342
yield_arg = 343
func_body_suite = 344
func_type_input = 345
func_type = 346
typelist = 347
#--end constants--

sym_name = {}
kila _name, _value kwenye list(globals().items()):
    ikiwa type(_value) ni type(0):
        sym_name[_value] = _name
toa _name, _value
