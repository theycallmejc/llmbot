"""Allowlisted local tools; never executes model-provided code or shell commands."""
import ast
import operator

class ToolError(ValueError): pass
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}

def calculator(expression: str) -> float:
    if len(expression) > 200: raise ToolError("Expression is too long.")
    def evaluate(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS: return _OPS[type(node.op)](evaluate(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS: return _OPS[type(node.op)](evaluate(node.left), evaluate(node.right))
        raise ToolError("Only arithmetic expressions are allowed.")
    try: return evaluate(ast.parse(expression, mode="eval").body)
    except (SyntaxError, ZeroDivisionError) as error: raise ToolError("Invalid arithmetic expression.") from error

TOOLS = {"calculator": calculator}

def execute(name: str, arguments: dict[str, str]) -> dict[str, object]:
    if name != "calculator": raise ToolError("That tool is not available.")
    return {"name": name, "result": calculator(arguments.get("expression", ""))}
