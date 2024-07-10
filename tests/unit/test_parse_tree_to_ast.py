"""Test Conversion of FhY Source Code from CST to AST."""

import pytest
from fhy import error, ir
from fhy.lang import ast

from ..utils import list_to_types

# TODO: make all identifier name equality not in terms of name hint after scope and
#       loading identifiers with table is implemented


def wrong_node_babe(node_a, node_b) -> str:
    """Wrong Node Babe.

    What you see, is what you get. And what you got, is unexpected...

    """
    name = node_a.__name__
    return f'Expected "{name}" (AST) node. Received: "{type(node_b)}"'


def is_primitive_expression_equal(expr1: ast.Expression, expr2: ast.Expression) -> bool:
    """Confirm equality between two primitive expression types."""
    primitive_expression_types = (
        ast.IntLiteral,
        ast.FloatLiteral,
        ast.ComplexLiteral,
        ast.IdentifierExpression,
        ast.TupleExpression,
        ast.TupleAccessExpression,
        ast.ArrayAccessExpression,
        ast.FunctionExpression,
    )
    if (
        not isinstance(expr1, primitive_expression_types)
        or not isinstance(expr2, primitive_expression_types)
        or not isinstance(expr1, expr2.__class__)
        or not isinstance(expr2, expr1.__class__)
    ):
        raise TypeError(
            "Both expressions must be primitive expressions of the same type: "
            f"{type(expr1)}, {type(expr2)}"
        )

    if isinstance(expr1, ast.IntLiteral | ast.FloatLiteral | ast.ComplexLiteral):
        return expr1.value == expr2.value

    elif isinstance(expr1, ast.IdentifierExpression):
        # TODO: remove the name hint portion once a more robust table for pulling
        #       identifiers in the same scope is created
        return expr1.identifier.name_hint == expr2.identifier.name_hint

    elif isinstance(expr1, ast.TupleExpression):
        return len(expr1.expressions) == len(expr2.expressions) and all(
            is_primitive_expression_equal(i, j)
            for i, j in zip(expr1.expressions, expr2.expressions)
        )

    elif isinstance(expr1, ast.TupleAccessExpression):
        return (
            expr1.element_index == expr2.element_index
            and is_primitive_expression_equal(
                expr1.tuple_expression,
                expr2.tuple_expression,
            )
        )

    elif isinstance(expr1, ast.ArrayAccessExpression):
        return len(expr1.indices) == len(expr2.indices) and all(
            is_primitive_expression_equal(i1, i2)
            for i1, i2 in zip(expr1.indices, expr2.indices)
        )

    elif isinstance(expr1, ast.FunctionExpression):
        return is_primitive_expression_equal(expr1.function, expr2.function)

    else:
        return False


def _assert_is_expected_module(node: ast.ASTNode, expected_num_statements: int) -> None:
    assert isinstance(node, ast.Module), wrong_node_babe(ast.Module, node)

    assert all(isinstance(x, ast.Statement) for x in node.statements), (
        'Expected all statements to be "Statement" AST nodes, got '
        + f'"{list_to_types(node.statements)}"'
    )
    assert (
        len(node.statements) == expected_num_statements
    ), f"Expected module to have {expected_num_statements} statements"


def _assert_is_expected_import(node: ast.ASTNode, expected_import: str) -> None:
    assert isinstance(node, ast.Import), wrong_node_babe(ast.Import, node)

    assert isinstance(
        node.name, ir.Identifier
    ), f'Expected import name to be "Identifier", got "{type(node.name)}"'

    assert (
        node.name.name_hint == expected_import
    ), f'Expected import name to be "{expected_import}", got "{node.name.name_hint}"'


def _assert_is_expected_procedure(
    node: ast.ASTNode,
    expected_name: str,
    expected_num_args: int,
    expected_num_statements: int,
) -> None:
    assert isinstance(node, ast.Procedure), wrong_node_babe(ast.Procedure, node)

    assert isinstance(
        node.name, ir.Identifier
    ), f'Expected procedure name to be "Identifier", got "{type(node.name)}"'
    assert (
        node.name.name_hint == expected_name
    ), f'Expected procedure name to be "{expected_name}", got "{node.name.name_hint}"'
    assert all(isinstance(arg, ast.Argument) for arg in node.args), (
        'Expected all arguments to be "Argument" AST nodes, got '
        + f'"{list_to_types(node.args)}"'
    )
    assert len(node.args) == expected_num_args, (
        f"Expected procedure to have {expected_num_args} arguments, got "
        + f"{len(node.args)}"
    )
    assert all(isinstance(statement, ast.Statement) for statement in node.body), (
        'Expected all statements to be "Statement" AST nodes, got '
        + f"{list_to_types(node.body)}"
    )
    assert len(node.body) == expected_num_statements, (
        f"Expected procedure to have {expected_num_statements} statements, got "
        + f"{len(node.body)}"
    )


def _assert_is_expected_operation(
    node: ast.ASTNode,
    expected_name: str,
    expected_num_args: int,
    expected_num_statements: int,
) -> None:
    assert isinstance(node, ast.Operation), wrong_node_babe(ast.Operation, node)

    assert isinstance(
        node.name, ir.Identifier
    ), f'Expected operation name to be "Identifier", got "{type(node.name)}"'
    assert (
        node.name.name_hint == expected_name
    ), f'Expected operation name to be "{expected_name}", got "{node.name.name_hint}"'
    assert all(isinstance(arg, ast.Argument) for arg in node.args), (
        'Expected all arguments to be "Argument" AST nodes, got '
        + f'"{list_to_types(node.args)}"'
    )
    assert len(node.args) == expected_num_args, (
        f"Expected operation to have {expected_num_args} arguments, got "
        + f"{len(node.args)}"
    )
    assert all(isinstance(statement, ast.Statement) for statement in node.body), (
        'Expected all statements to be "Statement" AST nodes, got '
        + f'"{list_to_types(node.body)}"'
    )
    assert len(node.body) == expected_num_statements, (
        f"Expected operation to have {expected_num_statements} statements, got "
        + f"{len(node.body)}"
    )


def _assert_is_expected_qualified_type(
    node: ast.ASTNode,
    expected_type_qualifier: ir.TypeQualifier,
    expected_base_type_cls: type[ir.Type],
) -> None:
    assert isinstance(node, ast.QualifiedType), wrong_node_babe(ast.QualifiedType, node)

    assert node.type_qualifier == expected_type_qualifier, (
        f'Expected type qualifier to be "{expected_type_qualifier}", '
        + f'got "{node.type_qualifier}"'
    )
    assert isinstance(node.base_type, expected_base_type_cls), (
        f'Expected base type to be "{expected_base_type_cls}", '
        + f'got "{type(node.base_type)}"'
    )


def _assert_is_expected_argument(
    node: ast.ASTNode,
    expected_name: str,
) -> None:
    assert isinstance(node, ast.Argument), wrong_node_babe(ast.Argument, node)

    assert isinstance(node.name, ir.Identifier), wrong_node_babe(
        ir.Identifier, node.name
    )
    assert (
        node.name.name_hint == expected_name
    ), f'Expected argument name to be "{expected_name}", got "{node.name.name_hint}"'


def _assert_is_expected_numerical_type(
    numerical_type: ir.NumericalType,
    expected_primitive_data_type: ir.CoreDataType,
    expected_shape: list[ast.Expression],
) -> None:
    assert isinstance(numerical_type, ir.NumericalType), wrong_node_babe(
        ir.NumericalType, numerical_type
    )

    assert numerical_type.data_type.core_data_type == expected_primitive_data_type, (
        f'Expected primitive data type to be "{expected_primitive_data_type}", got '
        + f'"{numerical_type.data_type.core_data_type}"'
    )

    assert all(isinstance(expr, ast.Expression) for expr in numerical_type.shape), (
        'Expected all shape components to be "Expression" AST nodes, got '
        + f'"{list_to_types(numerical_type.shape)}"'
    )
    assert len(numerical_type.shape) == len(expected_shape), (
        f"Expected numerical type shape to have {len(expected_shape)} components, got "
        + f"{len(numerical_type.shape)}"
    )
    for i, shape_component in enumerate(numerical_type.shape):
        assert is_primitive_expression_equal(shape_component, expected_shape[i]), (
            f"Expected shape component {i} to be equal "
            + f"(expected: {expected_shape[i]}, actual: {shape_component})"
        )


def _assert_is_expected_shape(
    shape: list[ast.Expression], expected_shape: list[ast.Expression]
) -> None:
    assert isinstance(shape, list), f'Expected shape to be a list, got "{type(shape)}"'
    assert all(isinstance(expr, ast.Expression) for expr in shape), (
        'Expected all shape components to be "Expression" AST nodes, got '
        + f'"{list_to_types(shape)}"'
    )
    assert len(shape) == len(
        expected_shape
    ), f"Expected shape to have {len(expected_shape)} components, got {len(shape)}"
    for i, shape_component in enumerate(shape):
        assert is_primitive_expression_equal(shape_component, expected_shape[i]), (
            f"Expected shape component {i} to be equal "
            + f"(expected: {expected_shape[i]}, actual: {shape_component})"
        )


def _assert_is_expected_index_type(
    index_type: ir.IndexType,
    expected_low: ast.Expression,
    expected_high: ast.Expression,
    expected_stride: ast.Expression | None,
) -> None:
    assert isinstance(index_type, ir.IndexType), wrong_node_babe(
        ir.IndexType, index_type
    )

    assert isinstance(index_type.lower_bound, ast.Expression), wrong_node_babe(
        ast.Expression, index_type.lower_bound
    )

    assert is_primitive_expression_equal(index_type.lower_bound, expected_low), (
        "Expected lower bound to be equal "
        + f"(expected: {expected_low}, actual: {index_type.lower_bound})"
    )
    assert isinstance(index_type.upper_bound, ast.Expression), wrong_node_babe(
        ast.Expression, index_type.upper_bound
    )

    assert is_primitive_expression_equal(index_type.upper_bound, expected_high), (
        "Expected upper bound to be equal "
        + f"(expected: {expected_high}, actual: {index_type.upper_bound})"
    )
    if expected_stride is not None:
        assert isinstance(index_type.stride, ast.Expression), wrong_node_babe(
            ast.Expression, index_type.stride
        )
        assert is_primitive_expression_equal(index_type.stride, expected_stride), (
            "Expected stride to be equal "
            + f"(expected: {expected_stride}, actual: {index_type.stride})"
        )


def _assert_is_expected_declaration_statement(
    node: ast.ASTNode,
    expected_variable_name: ir.Identifier,
    expected_expression: ast.Expression | None,
) -> None:
    assert isinstance(node, ast.DeclarationStatement), wrong_node_babe(
        ast.DeclarationStatement, node
    )

    assert isinstance(node.variable_name, ir.Identifier), wrong_node_babe(
        ir.Identifier, node.variable_name
    )

    assert node.variable_name.name_hint == expected_variable_name.name_hint, (
        f'Expected variable name to be "{expected_variable_name.name_hint}", '
        + f'got "{node.variable_name.name_hint}"'
    )
    assert isinstance(node.variable_type, ast.QualifiedType), wrong_node_babe(
        ast.QualifiedType, node.variable_type
    )
    if node.expression is not None:
        assert isinstance(node.expression, ast.Expression), wrong_node_babe(
            ast.Expression, node.expression
        )

    if expected_expression is not None:
        assert is_primitive_expression_equal(
            node.expression, expected_expression
        ), f'Expected expression to be "{expected_expression}", got "{node.expression}"'


def _assert_is_expected_expression_statement(
    node: ast.ASTNode,
    expected_left_expression: ast.Expression | None,
    expected_right_expression: ast.Expression,
) -> None:
    assert isinstance(node, ast.ExpressionStatement), wrong_node_babe(
        ast.ExpressionStatement, node
    )

    if expected_left_expression is not None:
        assert isinstance(node.left, ast.Expression), wrong_node_babe(
            ast.Expression, node.left
        )

        assert is_primitive_expression_equal(node.left, expected_left_expression), (
            "Expected left expression to be equal "
            + f"(expected: {expected_left_expression}, actual: {node.left})"
        )
    assert isinstance(node.right, ast.Expression), wrong_node_babe(
        ast.Expression, node.right
    )
    assert is_primitive_expression_equal(node.right, expected_right_expression), (
        "Expected right expression to be equal "
        + f"(expected: {expected_right_expression}, actual: {node.right})"
    )


def _assert_is_expected_return_statement(
    node: ast.ASTNode, expected_expression: ast.Expression
) -> None:
    assert isinstance(node, ast.ReturnStatement), wrong_node_babe(
        ast.ReturnStatement, node
    )
    assert isinstance(node.expression, ast.Expression), wrong_node_babe(
        ast.Expression, node.expression
    )
    assert is_primitive_expression_equal(node.expression, expected_expression), (
        "Expected expression to be equal "
        + f"(expected: {expected_expression}, actual: {node.expression})"
    )


# ====
# CORE
# ====
def test_empty_file(construct_ast):
    """Test that an empty file is converted correctly."""
    source: str = ""
    _ast = construct_ast(source)
    _assert_is_expected_module(_ast, 0)


# =========
# FUNCTIONS
# =========
@pytest.mark.parametrize(
    ["source"],
    [
        ("proc foo(){}",),  # Procedure Only
        ("proc foo<>() {}",),  # with Template Type
        ("proc foo[]() {}",),  # with Index
        ("proc foo<>[]() {}",),  # Both Template and Index
    ],
)
def test_empty_procedure(construct_ast, source: str):
    """Test that an empty procedure is converted correctly."""
    # source: str = "proc foo(){}"
    _ast = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    procedure = _ast.statements[0]
    _assert_is_expected_procedure(procedure, "foo", 0, 0)


@pytest.mark.parametrize(
    ["name"],
    [
        ("x",),
        ("arg",),
        ("arg1",),
        ("arg_1",),
        # Check Identity Names similar to Keywords
        ("importer",),
        ("from_there",),
        ("astype",),
        ("tuples",),
        ("indexed",),
        ("proctor",),
        ("operator",),
        ("natives",),
        ("reduction",),
        ("if_true",),
        ("else_if",),
        ("return_value",),
    ],
)
def test_empty_procedure_with_qualified_argument(construct_ast, name: str):
    """Test an empty procedure with a single qualified argument and argument names."""
    source: str = "proc foo(input int32 %s){}" % name
    _ast = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    procedure = _ast.statements[0]
    _assert_is_expected_procedure(procedure, "foo", 1, 0)

    arg = procedure.args[0]
    _assert_is_expected_argument(arg, name)

    arg_qualified_type = arg.qualified_type
    _assert_is_expected_qualified_type(
        arg_qualified_type, ir.TypeQualifier.INPUT, ir.NumericalType
    )
    arg_base_type = arg_qualified_type.base_type
    _assert_is_expected_numerical_type(arg_base_type, ir.CoreDataType.INT32, [])


def test_empty_procedure_with_a_qualified_argument_with_shape(construct_ast):
    """Test an Empty procedure containing Arguments with Shape."""
    source: str = "proc foo(input int32[m, n] x){}"
    _ast = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    procedure = _ast.statements[0]
    _assert_is_expected_procedure(procedure, "foo", 1, 0)

    arg = procedure.args[0]
    _assert_is_expected_argument(arg, "x")

    arg_qualified_type = arg.qualified_type
    _assert_is_expected_qualified_type(
        arg_qualified_type, ir.TypeQualifier.INPUT, ir.NumericalType
    )
    arg_type_shape = arg_qualified_type.base_type.shape
    _assert_is_expected_shape(
        arg_type_shape,
        [
            ast.IdentifierExpression(identifier=ir.Identifier("m")),
            ast.IdentifierExpression(identifier=ir.Identifier("n")),
        ],
    )


@pytest.mark.parametrize(
    ["source"],
    [
        ("op foo() -> output int32 {}",),  # Operation Only
        ("op foo<>() -> output int32 {}",),  # with Template Type
        ("op foo[]() -> output int32 {}",),  # with Index
        ("op foo<>[]() -> output int32 {}",),  # Both Template and Index
    ],
)
def test_empty_operation(construct_ast, source: str):
    """Test that an Empty Operation is Converted Correctly."""
    _ast = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    operation: ast.Operation = _ast.statements[0]
    _assert_is_expected_operation(operation, "foo", 0, 0)


def test_empty_operation_return_type(construct_ast):
    """Test that an Empty Operation with a Return Type is Converted Correctly."""
    source: str = "op foo(input int32[n, m] x) -> output int32[n, m] {}"
    _ast = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    operation: ast.Operation = _ast.statements[0]
    _assert_is_expected_operation(operation, "foo", 1, 0)

    arg = operation.args[0]
    _assert_is_expected_argument(arg, "x")

    arg_qualified_type = arg.qualified_type
    _assert_is_expected_qualified_type(
        arg_qualified_type, ir.TypeQualifier.INPUT, ir.NumericalType
    )
    arg_base_type: ir.Type = arg_qualified_type.base_type
    _assert_is_expected_numerical_type(
        arg_base_type,
        ir.CoreDataType.INT32,
        [
            ast.IdentifierExpression(identifier=ir.Identifier("n")),
            ast.IdentifierExpression(identifier=ir.Identifier("m")),
        ],
    )

    return_type = operation.return_type
    _assert_is_expected_qualified_type(
        return_type, ir.TypeQualifier.OUTPUT, ir.NumericalType
    )
    return_type_shape = return_type.base_type.shape
    _assert_is_expected_shape(
        return_type_shape,
        [
            ast.IdentifierExpression(identifier=ir.Identifier("n")),
            ast.IdentifierExpression(identifier=ir.Identifier("m")),
        ],
    )


@pytest.mark.parametrize(
    ["templates"],
    [(["T"],), (["T", "K"],), (["V", "Ex", "F"],)],
)
def test_operation_template_types(construct_ast, templates: list[str]):
    """Test that an Empty Operation with a Return Type is Converted Correctly."""
    source: str = "op foo<%s>(input int32[n, m] x) -> output int32[n, m] {}"
    _ast = construct_ast(source % ", ".join(templates))
    _assert_is_expected_module(_ast, 1)

    operation: ast.Operation = _ast.statements[0]
    _assert_is_expected_operation(operation, "foo", 1, 0)

    assert len(operation.templates) == len(
        templates
    ), "Expected Same Number of Template Types."
    for j, k in zip(operation.templates, templates):
        assert isinstance(j, ir.TemplateDataType), wrong_node_babe(
            ir.TemplateDataType, j
        )
        (
            j._data_type.name_hint == k,
            f"Expected Same Identifier Name: {j._data_type.name_hint}",
        )


def test_operation_template_type_body(construct_ast):
    """Test that an Template type Identifier IDs are equivalent."""
    source: str = "op foo<T>(input T[n, m] x) -> output int32[n, m] {temp T[n, m] A;}"
    _ast = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    operation: ast.Operation = _ast.statements[0]
    _assert_is_expected_operation(operation, "foo", 1, 1)

    template = operation.templates[0]
    assert isinstance(template, ir.TemplateDataType), wrong_node_babe(
        ir.TemplateDataType, template
    )

    statement: ast.Statement = operation.body[0]
    assert isinstance(statement, ast.DeclarationStatement), wrong_node_babe(
        ast.DeclarationStatement, statement
    )

    numerical: ir.NumericalType = statement.variable_type.base_type
    assert (
        numerical.data_type._data_type.id == template._data_type.id
    ), "Expected same TemplateDataType Identifier ID."


# ==========
# STATEMENTS
# ==========
def test_absolute_import(construct_ast):
    """Test Absolute Import Statement."""
    source: str = "import foo.bar;"
    _ast = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    _assert_is_expected_import(statement, "foo.bar")


def test_declaration_statement_without_assignment(construct_ast):
    """Tests a single Declaration Statement without assigning a value to variable."""
    source: str = "temp int32 i;"
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    _assert_is_expected_declaration_statement(statement, ir.Identifier("i"), None)

    qualified = statement.variable_type
    _assert_is_expected_qualified_type(
        qualified, ir.TypeQualifier.TEMP, ir.NumericalType
    )
    _assert_is_expected_shape(qualified.base_type.shape, [])


def test_expression_statement_without_assignment(construct_ast):
    """Test Construction of simple Expression Statements."""
    source = "5 + 5;"
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.ExpressionStatement), wrong_node_babe(
        ast.ExpressionStatement, statement
    )

    assert statement.left is None, f"Expected No Left Hand Expression: {statement.left}"
    assert isinstance(statement.right, ast.BinaryExpression), wrong_node_babe(
        ast.BinaryExpression, statement.right
    )


def test_expression_statement_with_assignment(construct_ast):
    """Test Construction of simple Expression Statements with variable Assignment."""
    source = "A = 5 + 5;"
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.ExpressionStatement), wrong_node_babe(
        ast.ExpressionStatement, statement
    )

    assert is_primitive_expression_equal(
        statement.left, ast.IdentifierExpression(identifier=ir.Identifier("A"))
    )

    assert isinstance(statement.right, ast.BinaryExpression), wrong_node_babe(
        ast.BinaryExpression, statement.right
    )


def test_selection_statement(construct_ast):
    """Test an If (selection) Statement."""
    source: str = "if (1) {i = 1;} else {j = 1;}"
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.SelectionStatement), wrong_node_babe(
        ast.SelectionStatement, statement
    )
    assert isinstance(statement.condition, ast.IntLiteral), wrong_node_babe(
        ast.IntLiteral, statement.condition
    )

    assert len(statement.true_body) == 1, "Expected 1 Statement in True Body."
    assert len(statement.false_body) == 1, "Expected 1 Statement in False Body."


def test_for_all_statement(construct_ast):
    """Test an Iteration (For All) Statement (loop)."""
    source: str = "forall (i) {}"
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.ForAllStatement), wrong_node_babe(
        ast.ForAllStatement, statement
    )
    assert isinstance(statement.index, ast.IdentifierExpression), wrong_node_babe(
        ast.IdentifierExpression, statement.index
    )
    assert statement.index.identifier.name_hint == "i", (
        'Expected index name hint to be "i", got '
        + f'"{statement.index.identifier.name_hint}"'
    )
    assert (
        len(statement.body) == 0
    ), f"Expected body to have 0 statements, got {len(statement.body)}"


def test_return_statement(construct_ast):
    """Test a Return Statement."""
    source: str = "return i;"  # Semantically Incorrect.
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    _assert_is_expected_return_statement(
        statement, ast.IdentifierExpression(identifier=ir.Identifier("i"))
    )


# ===========
# EXPRESSIONS
# ===========
@pytest.mark.parametrize(["operator"], [(j,) for j in ast.UnaryOperation])
def test_unary_expression(construct_ast, operator: ast.UnaryOperation):
    """Test Construction of Unary Expression with correct Operator."""
    source: str = "temp int32 i = %s5;" % operator.value
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.DeclarationStatement), wrong_node_babe(
        ast.DeclarationStatement, statement
    )

    expression = statement.expression
    assert isinstance(expression, ast.UnaryExpression), wrong_node_babe(
        ast.UnaryExpression, expression
    )
    assert (
        expression.operation == operator
    ), f'Expected "{operator}" operation. Received: "{expression.operation}"'

    assert is_primitive_expression_equal(expression.expression, ast.IntLiteral(value=5))


@pytest.mark.parametrize(["operator"], [(i,) for i in ast.BinaryOperation])
def test_binary_expressions(construct_ast, operator: ast.BinaryOperation):
    """Tests Construction of all Available Binary Expression Operators."""
    source: str = f"temp float32 i = 5 {operator.value} 6;"  # Semantically Incorrect
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.DeclarationStatement), wrong_node_babe(
        ast.DeclarationStatement, statement
    )

    expression = statement.expression
    assert isinstance(expression, ast.BinaryExpression), wrong_node_babe(
        ast.BinaryExpression, expression
    )
    assert (
        expression.operation == operator
    ), f'Expected "{operator}" operation. Received: "{expression.operation}"'

    assert is_primitive_expression_equal(expression.left, ast.IntLiteral(value=5))
    assert is_primitive_expression_equal(expression.right, ast.IntLiteral(value=6))


def test_ternary_expressions(construct_ast):
    """Test a Ternary Conditional Expression."""
    source: str = "temp float32 i = 5 < 6 ? 7 : 8;"
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.DeclarationStatement), wrong_node_babe(
        ast.DeclarationStatement, statement
    )

    expression = statement.expression
    assert isinstance(expression, ast.TernaryExpression), wrong_node_babe(
        ast.TernaryExpression, expression
    )

    assert isinstance(expression.condition, ast.BinaryExpression), wrong_node_babe(
        ast.BinaryExpression, expression.condition
    )
    assert is_primitive_expression_equal(expression.true, ast.IntLiteral(value=7))
    assert is_primitive_expression_equal(expression.false, ast.IntLiteral(value=8))


@pytest.mark.parametrize(["name"], [("A",), ("A1",), ("A_",)])
def test_tuple_access_expression(construct_ast, name: str):
    """Test a Tuple Access Expression."""
    source: str = "x = %s.1;" % name
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]

    _assert_is_expected_expression_statement(
        statement,
        ast.IdentifierExpression(identifier=ir.Identifier("x")),
        ast.TupleAccessExpression(
            tuple_expression=ast.IdentifierExpression(identifier=ir.Identifier(name)),
            element_index=1,
        ),
    )


def test_tuple_access_function_expression(construct_ast):
    """Test a tuple access expression against a function primitive expression."""
    source: str = "x = f().1;"
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    _assert_is_expected_expression_statement(
        statement,
        ast.IdentifierExpression(identifier=ir.Identifier("x")),
        ast.TupleAccessExpression(
            tuple_expression=ast.FunctionExpression(
                function=ast.IdentifierExpression(identifier=ir.Identifier("f"))
            ),
            element_index=1,
        ),
    )


@pytest.mark.parametrize(
    ["source", "nargs", "name"],
    [
        ("temp int32 i = foo();", 0, "foo"),  # only Function Call
        ("temp int32 i = foo(A);", 1, "foo"),  # only Function Call
        ("temp int32 i = module.method();", 0, "module.method"),
        ("temp int32 i = module.method(A);", 1, "module.method"),
        ("temp int32 i = foo[]();", 0, "foo"),  # with Index
        ("temp int32 i = foo[](A);", 1, "foo"),  # with Index
        ("temp int32 i = module.method[]();", 0, "module.method"),
        ("temp int32 i = module.method[](A);", 1, "module.method"),
        ("temp int32 i = foo<>();", 0, "foo"),  # with Template Types
        ("temp int32 i = foo<>(A);", 1, "foo"),  # with Template Types
        ("temp int32 i = module.method<>();", 0, "module.method"),
        ("temp int32 i = module.method<>(A);", 1, "module.method"),
        ("temp int32 i = foo<>[]();", 0, "foo"),  # both Template Types and Index
        ("temp int32 i = foo<>[](A);", 1, "foo"),  # both Template Types and Index
        ("temp int32 i = module.method<>[]();", 0, "module.method"),
        ("temp int32 i = module.method<>[](A);", 1, "module.method"),
    ],
)
def test_function_expression(construct_ast, source: str, nargs: int, name: str):
    """Test Function Call Expression within a Declaration Statement."""
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.DeclarationStatement), wrong_node_babe(
        ast.DeclarationStatement, statement
    )

    expression = statement.expression
    assert isinstance(expression, ast.FunctionExpression), wrong_node_babe(
        ast.FunctionExpression, expression
    )
    assert is_primitive_expression_equal(
        expression.function, ast.IdentifierExpression(identifier=ir.Identifier(name))
    )

    template = expression.template_types
    assert len(template) == 0, f"Expected no template types, got {len(template)}"
    index = expression.indices
    assert len(index) == 0, f"Expected no indices, got {len(index)}"

    assert (
        len(expression.args) == nargs
    ), f"Expected {nargs} arguments, got {len(expression.args)}"

    if nargs:
        expect = ast.IdentifierExpression(identifier=ir.Identifier("A"))
        assert is_primitive_expression_equal(expression.args[0], expect)


@pytest.mark.parametrize(
    ["source"],
    [
        ("foo();",),  # only Function Call
        ("foo<>();",),  # with Template Types
        ("foo[]();",),  # with Index
        ("foo<>[]();",),  # both Template Types and Index
        ("module.method();",),
        ("module.method[]();",),
        ("module.method<>();",),
        ("module.method<>[]();",),
    ],
)
def test_function_expression_as_expression_statement(construct_ast, source: str):
    """Test Function Call Expression within as an Expression Statement."""
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.ExpressionStatement), wrong_node_babe(
        ast.ExpressionStatement, statement
    )

    assert statement.left is None, f"Unexpected Left Expression: {statement.left}"
    assert isinstance(statement.right, ast.FunctionExpression), wrong_node_babe(
        ast.FunctionExpression, statement.right
    )


def test_function_expression_with_templates(construct_ast):
    """Test Function Call Expression within as an Expression Statement."""
    _ast: ast.Module = construct_ast("proc foo<T>(input T[m,n] A) { bar<T>(); }")
    _assert_is_expected_module(_ast, 1)

    proc = _ast.statements[0]
    assert isinstance(proc, ast.Procedure), wrong_node_babe(ast.Procedure, proc)
    template = proc.templates[0]
    assert isinstance(template, ir.TemplateDataType), wrong_node_babe(
        ir.TemplateDataType, template
    )

    statement = proc.body[0]
    assert isinstance(statement, ast.ExpressionStatement), wrong_node_babe(
        ast.ExpressionStatement, statement
    )

    # Check argument too.
    arg = proc.args[0]
    assert isinstance(arg, ast.Argument), wrong_node_babe(ast.Argument, arg)
    assert isinstance(arg.qualified_type.base_type, ir.NumericalType), wrong_node_babe(
        ir.NumericalType, arg.qualified_type.base_type
    )
    arg_temp = arg.qualified_type.base_type.data_type
    assert isinstance(arg_temp, ir.TemplateDataType), wrong_node_babe(
        ir.TemplateDataType, arg_temp
    )
    assert (
        template._data_type.id == arg_temp._data_type.id
    ), "Expected same TemplateDataType Identifier ID."

    function = statement.right
    assert isinstance(function, ast.FunctionExpression), wrong_node_babe(
        ast.FunctionExpression, function
    )
    ftemp = function.template_types[0]
    assert isinstance(ftemp, ir.TemplateDataType), wrong_node_babe(
        ir.TemplateDataType, ftemp
    )

    assert (
        template._data_type.id == ftemp._data_type.id
    ), "Expected same TemplateDataType Identifier ID."


def test_tensor_access_expression(construct_ast):
    """Test construction of a Tensor Access Expression."""
    source: str = "A[i] = 1;"  # Semantically Invalid
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    _assert_is_expected_expression_statement(
        statement,
        ast.ArrayAccessExpression(
            array_expression=ast.IdentifierExpression(identifier=ir.Identifier("A")),
            indices=[ast.IdentifierExpression(identifier=ir.Identifier("i"))],
        ),
        ast.IntLiteral(value=1),
    )


def test_tuple_expression(construct_ast):
    """Test construction of a tuple expression."""
    source: str = "b = (a,);"
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    _assert_is_expected_expression_statement(
        statement,
        ast.IdentifierExpression(identifier=ir.Identifier("b")),
        ast.TupleExpression(
            expressions=[ast.IdentifierExpression(identifier=ir.Identifier("a"))]
        ),
    )


# =====
# TYPES
# =====
def test_index_type(construct_ast):
    """Test Construction of an Index Type."""
    source: str = "temp index[1:m] i;"  # Semantically Invalid
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.DeclarationStatement), wrong_node_babe(
        ast.DeclarationStatement, statement
    )
    _assert_is_expected_qualified_type(
        statement.variable_type, ir.TypeQualifier.TEMP, ir.IndexType
    )
    _assert_is_expected_index_type(
        statement.variable_type.base_type,
        ast.IntLiteral(value=1),
        ast.IdentifierExpression(identifier=ir.Identifier("m")),
        None,
    )


@pytest.mark.parametrize(
    ["source"],
    [
        ("output tuple[int32[m, n], int32] i;",),
        ("output tuple[int32[m, n], int32,] i;",),
    ],
)
def test_tuple_type(construct_ast, source: str):
    """Test construction of Tuple Type."""
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.DeclarationStatement), wrong_node_babe(
        ast.DeclarationStatement, statement
    )
    assert statement.variable_name.name_hint == "i", 'Expected Variable Name "i"'
    _assert_is_expected_qualified_type(
        statement.variable_type, ir.TypeQualifier.OUTPUT, ir.TupleType
    )

    _tuple: ir.TupleType = statement.variable_type.base_type
    assert len(_tuple._types) == 2, "Expected 2 Types in TupleType Definition."
    t1, t2 = _tuple._types
    _assert_is_expected_numerical_type(
        t1,
        ir.CoreDataType.INT32,
        [
            ast.IdentifierExpression(identifier=ir.Identifier("m")),
            ast.IdentifierExpression(identifier=ir.Identifier("n")),
        ],
    )
    _assert_is_expected_numerical_type(t2, ir.CoreDataType.INT32, [])


@pytest.mark.parametrize(
    ["source", "value"],
    [
        ("1;", 1),
        ("0b0101;", 5),
        ("0B01;", 1),
        ("0x1;", 1),
        ("0XFF;", 255),
        ("0o1;", 1),
        ("0O7;", 7),
    ],
)
def test_int_literal(construct_ast, source: str, value: int):
    """Test IntLiteral Construction of different Format Representations."""
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.ExpressionStatement), wrong_node_babe(
        ast.ExpressionStatement, statement
    )
    assert is_primitive_expression_equal(statement.right, ast.IntLiteral(value=value))


@pytest.mark.parametrize(
    ["source", "value"],
    [
        ("1.0;", 1.0),
        (".2;", 0.2),
        (" 1.;", 1.0),
        (" 1e2;", 100.0),
        ("1.2e3;", 1200.0),
    ],
)
def test_float_literal(construct_ast, source: str, value: float):
    """Test FloatLiteral Construction of different Format Representations."""
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.ExpressionStatement), wrong_node_babe(
        ast.ExpressionStatement, statement
    )
    assert is_primitive_expression_equal(statement.right, ast.FloatLiteral(value=value))


@pytest.mark.parametrize(
    ["source", "value"],
    [
        ("1.0j;", 1.0j),
        ("1j;", 1j),
        ("1e10j;", 1e10j),
        ("0.2j;", 0.2j),
        (".2j;", 0.2j),
    ],
)
def test_complex_literal(construct_ast, source: str, value: complex):
    _ast: ast.Module = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    statement = _ast.statements[0]
    assert isinstance(statement, ast.ExpressionStatement), wrong_node_babe(
        ast.ExpressionStatement, statement
    )
    assert is_primitive_expression_equal(
        statement.right, ast.ComplexLiteral(value=value)
    )


# =============
# MISCELLANEOUS
# =============
def test_line_comment(construct_ast):
    """Test that comments are skipped, creating an empty Module."""
    source: str = "# this is a comment!"
    _ast = construct_ast(source)
    _assert_is_expected_module(_ast, 0)


def test_empty_procedure_with_line_comment(construct_ast):
    """Test procedure is found and constructed with line comments in the mix."""
    source: str = "# this is a comment!\nproc foo(input int32[m,n] A) {}"
    _ast = construct_ast(source)
    _assert_is_expected_module(_ast, 1)

    proc = _ast.statements[0]
    _assert_is_expected_procedure(proc, "foo", 1, 0)

    # Procedure should be on second line
    line = proc.span.line.start
    assert line == 2, f"Expected Procedure to be on Second Line: {line}"

    # NOTE: New line character is in first column.
    col = proc.span.line.start
    assert col == 2, f"Expected Procedure to be on First Column: {col}"


# ===============
# EXPECTED ERRORS
# ===============
def test_syntax_error_no_argument_name(construct_ast):
    """Raise FhYSyntaxError when an function Argument is defined without a Name."""
    source: str = "op foo(input int32[m,n]) -> output int32 {}"
    with pytest.raises(error.FhYSyntaxError):
        _ast = construct_ast(source)


def test_syntax_error_no_procedure_name(construct_ast):
    """Raise Syntax Error when an Operation is defined without a Name."""
    source: str = "proc () {}"
    # NOTE: This raises the Antlr Syntax Error, not from our visitor class.
    #       This means we do not gain coverage in parse tree converter for this case.
    with pytest.raises(error.FhYSyntaxError):
        _ast = construct_ast(source)


def test_syntax_error_no_operation_name(construct_ast):
    """Raise Syntax Error when an Operation is defined without a Name."""
    source: str = "op (input int32[m,n] A) -> output int32 {}"
    # NOTE: This raises the Antlr Syntax Error, not from our visitor class.
    #       This means we do not gain coverage in parse tree converter for this case.
    with pytest.raises(error.FhYSyntaxError):
        _ast = construct_ast(source)


def test_syntax_error_no_operation_return_type(construct_ast):
    """Raise FhYSyntaxError when an Operation is defined without a return type."""
    source: str = "op func(input int32[m,n] A) {}"
    with pytest.raises(error.FhYSyntaxError):
        _ast = construct_ast(source)


def test_invalid_function_keyword(construct_ast):
    """Raise FhySyntaxError when Function is Declared with Invalid Keyword."""
    source: str = "def foo(input int32[m,n] A) -> output int32[m,n] {}"
    with pytest.raises(error.FhYSyntaxError):
        _ast = construct_ast(source)


@pytest.mark.parametrize(
    ["source"],
    [
        ("lorem ipsum dolor sit amet;",),  # With Semicolon
        ("lorem ipsum dolor sit amet",),  # No Semicolon
    ],
)
def test_gibberish(construct_ast, source: str):
    """Gibberish (unrecognized text according to fhy grammar) Raises FhySyntaxError."""
    with pytest.raises(error.FhYSyntaxError):
        _ast = construct_ast(source)
