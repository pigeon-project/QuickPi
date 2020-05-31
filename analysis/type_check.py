# import ast
import typing
from ast import AST, Num, Str, expr, Bytes, stmt, AnnAssign, BoolOp, Assign, Expr, Raise, With, AsyncWith, BinOp, Add, \
    operator

from .mata_info import Context, ClassInfo, FunctionInfo, OneNameSpace, ObjectBind, TraitInfo, QTypeVar
from .mata_info import TypeInfo, TypeRef, NoneType, BottomType
from .mata_info import builtin_bytes, builtin_float, builtin_int, builtin_str
from .utils import AnalysisError, PosInfo, AnalysisWarning, TypeCheckError


# trait_map = {
#     And: 'And',
#     Or: 'Or',
#     Not: 'Or',
#     Add: 'And'
# }


# def type_assert(ast: AST, tp: TypeInfo):
#     pass

def apply_typevar(type_expr: TypeInfo, ):
    pass


def unify(t1: TypeInfo, t2: TypeInfo):
    if isinstance(t1, TypeRef) or isinstance(t2, TypeRef):
        if isinstance(t1, TypeRef):
            t1 = t1.get_true_type()
        if isinstance(t2, TypeRef):
            t2 = t2.get_true_type()
        unify(t1, t2)
        return
    if isinstance(t1, ClassInfo) and isinstance(t2, ClassInfo):
        if t1.fullname == t2.fullname and t1.type_vars == t2.type_vars:
            return
        raise TypeCheckError(f"type '{t1.fullname}{t1.type_vars}' is not '{t2.fullname}{t2.type_vars}'", t2.pos,
                             t2.top_level)
    if isinstance(t1, TraitInfo) and isinstance(t2, TraitInfo):
        if t1.fullname == t2.fullname and len(t1.type_vars) == 0:
            return
        raise TypeCheckError(f"trait '{t1.fullname}' is not '{t2.fullname}'", t2.pos, t2.top_level)
    if isinstance(t1, QTypeVar) and isinstance(t2, QTypeVar):
        if t1.trait_constraint == t2.trait_constraint:
            return
        raise TypeCheckError(f"found '{t2.trait_constraint}' need '{t1.trait_constraint}'", t2.pos, t2.top_level)
    if isinstance(t1, QTypeVar) and isinstance(t2, TraitInfo):
        t1.trait_constraint.append(t2)
        return
    if isinstance(t1, TraitInfo) and isinstance(t2, QTypeVar):
        if t1 in t2.trait_constraint:
            return
        raise TypeCheckError(f"found '{t2.trait_constraint}' need '{t1}'", t2.pos, t2.top_level)


def check_arith_operation(context: Context, ast: AST, op: operator) -> TypeInfo:
    left_type = type_infer(context, ast.values[0])
    trait = context.get_top_level().find_name(op.__class__.__name__)
    assert isinstance(trait, TraitInfo)
    unify(left_type, trait)
    # todo: apply typevar?


def expr_infer(context: Context, ast: expr) -> TypeInfo:
    if isinstance(ast, Str):
        return builtin_str
    if isinstance(ast, Num):
        if isinstance(ast.n, int):
            return builtin_int
        if isinstance(ast.n, float):
            return builtin_float
        assert False
    if isinstance(ast, Bytes):
        return builtin_bytes
    if isinstance(ast, BoolOp) or isinstance(ast, BinOp):
        return check_arith_operation(context, ast, ast.op)

    raise RuntimeError('喵喵喵喵喵？')
    # left_type.
    # type_assert(ast.values[0], builtin_bool)
    # type_assert(ast.values[1], builtin_bool)
    # return builtin_bool
    # if isinstance(ast, Call):
    #     return TypeRef('bytes', 'qpy.builtin.bytes')


def block_infer(context: Context, exprs: typing.List[Expr]) -> TypeInfo:
    for i in exprs[:-1]:
        if isinstance(i, expr):
            expr_check(context, i)
        if isinstance(i, stmt):
            stmt_check(context, i.value)
    return expr_infer(context, exprs[-1].value)


def type_infer(context: Context, ast: AST) -> TypeInfo:
    if isinstance(ast, expr):
        return expr_infer(context, ast)
    # if isinstance(ast, )

    pass


def ann_assign_check(context: Context, ast: AnnAssign):
    if isinstance(context, ClassInfo):
        raise AnalysisError("Context invalid", PosInfo(ast), context.get_top_level())
    name = context.find_name(ast.target.id)

    assert False


def assign_check(context: Context, ast: Assign):
    pass


def with_check(context: Context, ast: typing.Union[With, AsyncWith]):
    c1 = context  # 为了绕过类型检查
    if not isinstance(context, OneNameSpace):
        raise AnalysisError("context error", PosInfo(ast), context.get_top_level())
    for i in ast.items:
        res = expr_infer(c1, i.context_expr)
        trait = context.get_top_level().find_name('IDisposable')
        assert isinstance(trait, TraitInfo)
        unify(res, trait)
        if i.optional_vars:
            rid = i.optional_vars.id
            context.add_symbol(rid, ObjectBind(
                rid, c1.get_top_level().get_prev_name() + rid, res))
        else:
            print(AnalysisWarning(f'Unused value of type {res}', PosInfo(i), c1.get_top_level()))
    return block_infer(c1, ast.body)


def expr_check(context: Context, ast: expr):
    rt = expr_infer(context, ast)
    if not (isinstance(rt, BottomType) or isinstance(rt, NoneType)):
        print(AnalysisWarning(f'Unused value of type {rt}', PosInfo(ast), context.get_top_level()))


def stmt_check(context: Context, ast: stmt):
    if isinstance(ast, Expr):
        expr_check(context, ast.value)
    if isinstance(ast, AnnAssign):
        ann_assign_check(context, ast)
    if isinstance(ast, Assign):
        assign_check(context, ast)
    if isinstance(ast, Raise):
        if isinstance(context, FunctionInfo):
            context.add_throw_type(type_infer(context, ast.exc))
        else:
            raise AnalysisError("context error", PosInfo(ast), context.get_top_level())
    if isinstance(ast, With):
        with_check(context, ast)
    if isinstance(ast, AsyncWith):
        # TODO: check function is async function code
        if isinstance(context, FunctionInfo) and context.is_async:
            print(AnalysisWarning("await is not in async function", PosInfo(ast), context.get_top_level()))
        with_check(context, ast)
    pass


def type_check(context: Context, ast: AST):
    if isinstance(ast, stmt):
        return stmt_check(context, ast)
    # type_infer(context, ast)
