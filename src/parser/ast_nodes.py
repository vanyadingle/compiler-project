"""
AST Node definitions for MiniLang.
Each node can serialize itself to a JSON-serializable dict for the frontend.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional


class ASTNode:
    """Base class for all AST nodes."""

    def to_dict(self) -> dict:
        raise NotImplementedError

    def _node(self, label: str, children: List[dict] = None, value: str = None) -> dict:
        d: dict = {"name": label}
        if value is not None:
            d["value"] = value
        if children:
            d["children"] = children
        return d


# ── Program ────────────────────────────────────────────────────────────────────

@dataclass
class Program(ASTNode):
    declarations: List[ASTNode] = field(default_factory=list)

    def to_dict(self):
        return self._node("Program", [d.to_dict() for d in self.declarations])


# ── Declarations ───────────────────────────────────────────────────────────────

@dataclass
class FunctionDecl(ASTNode):
    name: str
    params: List["Param"]
    return_type: Optional[str]
    body: "Block"

    def to_dict(self):
        children = []
        if self.params:
            children.append(self._node("Params", [p.to_dict() for p in self.params]))
        if self.return_type:
            children.append(self._node("ReturnType", value=self.return_type))
        children.append(self.body.to_dict())
        return self._node(f"FunctionDecl", children, value=self.name)


@dataclass
class Param(ASTNode):
    name: str
    type_name: str

    def to_dict(self):
        return self._node("Param", value=f"{self.type_name} {self.name}")


# ── Statements ─────────────────────────────────────────────────────────────────

@dataclass
class Block(ASTNode):
    stmts: List[ASTNode]

    def to_dict(self):
        return self._node("Block", [s.to_dict() for s in self.stmts] or None)


@dataclass
class VarDecl(ASTNode):
    type_name: str
    name: str
    initializer: Optional[ASTNode]

    def to_dict(self):
        children = [self.initializer.to_dict()] if self.initializer else None
        return self._node("VarDecl", children, value=f"{self.type_name} {self.name}")


@dataclass
class AssignStmt(ASTNode):
    name: str
    value: ASTNode

    def to_dict(self):
        return self._node("Assign", [self.value.to_dict()], value=self.name)


@dataclass
class ReturnStmt(ASTNode):
    expr: Optional[ASTNode]

    def to_dict(self):
        children = [self.expr.to_dict()] if self.expr else None
        return self._node("Return", children)


@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_block: Block
    else_block: Optional[Block]

    def to_dict(self):
        children = [
            self._node("Condition", [self.condition.to_dict()]),
            self._node("Then", [self.then_block.to_dict()]),
        ]
        if self.else_block:
            children.append(self._node("Else", [self.else_block.to_dict()]))
        return self._node("If", children)


@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: Block

    def to_dict(self):
        return self._node("While", [
            self._node("Condition", [self.condition.to_dict()]),
            self.body.to_dict(),
        ])


@dataclass
class ForStmt(ASTNode):
    init: Optional[ASTNode]
    condition: Optional[ASTNode]
    update: Optional[ASTNode]
    body: Block

    def to_dict(self):
        children = []
        if self.init:
            children.append(self._node("Init", [self.init.to_dict()]))
        if self.condition:
            children.append(self._node("Condition", [self.condition.to_dict()]))
        if self.update:
            children.append(self._node("Update", [self.update.to_dict()]))
        children.append(self.body.to_dict())
        return self._node("For", children)


@dataclass
class PrintStmt(ASTNode):
    expr: ASTNode

    def to_dict(self):
        return self._node("Print", [self.expr.to_dict()])


@dataclass
class ExprStmt(ASTNode):
    expr: ASTNode

    def to_dict(self):
        return self._node("ExprStmt", [self.expr.to_dict()])


# ── Expressions ────────────────────────────────────────────────────────────────

@dataclass
class BinaryExpr(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

    def to_dict(self):
        return self._node("BinaryOp", [self.left.to_dict(), self.right.to_dict()], value=self.op)


@dataclass
class UnaryExpr(ASTNode):
    op: str
    operand: ASTNode

    def to_dict(self):
        return self._node("UnaryOp", [self.operand.to_dict()], value=self.op)


@dataclass
class CallExpr(ASTNode):
    callee: str
    args: List[ASTNode]

    def to_dict(self):
        children = [a.to_dict() for a in self.args] or None
        return self._node("Call", children, value=self.callee)


@dataclass
class Identifier(ASTNode):
    name: str

    def to_dict(self):
        return self._node("Identifier", value=self.name)


@dataclass
class IntLiteral(ASTNode):
    value: int

    def to_dict(self):
        return self._node("IntLiteral", value=str(self.value))


@dataclass
class FloatLiteral(ASTNode):
    value: float

    def to_dict(self):
        return self._node("FloatLiteral", value=str(self.value))


@dataclass
class BoolLiteral(ASTNode):
    value: bool

    def to_dict(self):
        return self._node("BoolLiteral", value=str(self.value).lower())


@dataclass
class StringLiteral(ASTNode):
    value: str

    def to_dict(self):
        return self._node("StringLiteral", value=f'"{self.value}"')
