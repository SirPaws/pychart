from typing import Any, Dict
from src.pychart._interpreter.ast_nodes.expression import (
    Assignment,
    Binary,
    Expr,
    ExprVisitor,
    Grouping,
    Literal,
    Unary,
    Variable,
)
from src.pychart._interpreter.ast_nodes.statement import (
    Block,
    Expression,
    Let,
    Print,
    StmtVisitor,
)
from src.pychart._interpreter.helpers.environment import Environment
from src.pychart._interpreter.helpers.number_helpers import is_number, try_cast_int
from src.pychart._interpreter.token_type.token import Token
from src.pychart._interpreter.token_type.token_type_enum import TokenType


class Interpreter(ExprVisitor, StmtVisitor):
    environment: Environment
    resolver_bindings: Dict[Expr, int]

    def __init__(self, resolver_bindings: Dict[Expr, int]):
        self.environment = Environment()
        self.resolver_bindings = resolver_bindings

    def get(self, name: Token, expr: Expr):
        depth = self.resolver_bindings.get(expr)

        if depth is None:
            raise RuntimeError(f"GET: Could not resolve variable: '{name.lexeme}'")

        return self.environment.get_at(depth, name.lexeme)

    def set(self, name: Token, expr: Expr, value: Any):
        depth = self.resolver_bindings.get(expr)

        if depth is None:
            raise RuntimeError(f"SET: Could not resolve variable: '{name.lexeme}'")

        self.environment.set_at(depth, name.lexeme, value)

    # Expression Visitor
    def binary(self, expr: Binary) -> Any:
        left = expr.left(self)
        right = expr.right(self)

        if expr.operator.token_type == TokenType.STAR:
            return left * right
        elif expr.operator.token_type == TokenType.SLASH:
            return left / right
        elif expr.operator.token_type == TokenType.PLUS:
            state = is_number(left) == is_number(right)
            return left + right if state else str(left) + str(right)
        elif expr.operator.token_type == TokenType.MINUS:
            return left - right
        elif expr.operator.token_type == TokenType.GREATER_EQUAL:
            return left >= right
        elif expr.operator.token_type == TokenType.GREATER:
            return left > right
        elif expr.operator.token_type == TokenType.LESSER_EQUAL:
            return left <= right
        elif expr.operator.token_type == TokenType.LESSER:
            return left < right
        elif expr.operator.token_type == TokenType.EQUAL_EQUAL:
            return left == right
        elif expr.operator.token_type == TokenType.EQUAL:
            raise RuntimeError("Not implemented.")
        elif expr.operator.token_type == TokenType.BANG_EQUAL:
            return left != right

        raise RuntimeError("Call Binary Operator Undefined")

    def unary(self, expr: Unary) -> Any:
        right = expr.right(self)

        if expr.operator.token_type == TokenType.MINUS:
            return 0 - right
        elif expr.operator.token_type == TokenType.BANG:
            return not right

        raise RuntimeError("Call Unary Undefined")

    def literal(self, expr: Literal) -> Any:
        return try_cast_int(expr.value)

    def grouping(self, expr: Grouping) -> Any:
        return expr.expr(self)

    def variable(self, expr: Variable) -> Any:
        return self.get(expr.name, expr)

    def assignment(self, expr: Assignment) -> Any:
        value = expr.initializer(self)

        self.set(expr.name, expr, value)

        return value

    # Statement Visitor
    def expression(self, stmt: Expression) -> Any:
        return stmt.expr(self)

    def print(self, stmt: Print) -> Any:
        value = stmt.expr(self)
        print(value)
        return None

    def let(self, stmt: Let) -> Any:
        value = None
        if stmt.initializer is not None:
            value = stmt.initializer(self)

        self.environment.reverve(stmt.name.lexeme, value)

        return value

    def block(self, stmt: Block) -> Any:
        previous = self.environment
        self.environment = Environment(self.environment)

        for statement in stmt.statements:
            statement(self)

        self.environment = previous
