import ply.lex as lex
import ply.yacc as yacc
import os
from pysh_essentials import *
atokens = [
	"string", "identifier", "int", "plus", "minus", "div", "mul", "lBrace", "rBrace", "lParen", "rParen"
]

keywords=[
	"IF","EQ", "NEQ", "SET", "RUN", "ELSE"
]

tokens=atokens+keywords

t_ignore = "\t "
t_minus = "-"
t_plus = r"\+"
t_div = "/"
t_lBrace = "{"
t_rBrace = "}"
t_lParen = r"\("
t_rParen = r"\)"
t_mul = r"\*"

def t_int(t):
	r'\d+'
	t.value=int(t.value)
	return t

def t_string(t):
	r'"[A-Za-z0-9\.%,/\[\]{}%]*"'
	return t

def t_identifier(t):
	r'[A-Za-z_\.%].[A-Za-z0-9_\.%]*'
	if t.value in keywords:
		t.type = t.value
	return t

def t_command(t):
	r'RUN [A-Za-z_\.% ].[A-Za-z0-9_\. %]*'
	return t

def t_NEWLINE(t):
	r'\n'
	t.lexer.lineno+=1

def p_program(p):
	"""
	program : statements
	"""
	p[0]=p[1]
def p_run_arguments(p):
	"""
	run_args : run_args identifier
			 | identifier
	"""
	if len(p)==2:
		p[0]=[p[1]]
	elif len(p)==3:
		p[1].append(p[2])
		p[0]=p[1]
def p_condition(p):
	"""
	condition : lParen expr EQ expr rParen
			  | lParen expr NEQ expr rParen
	"""
	p[0] = CONDITION(p[2],p[3],p[4])
def p_statement_if(p):
	"""
	statement : IF condition lBrace statements rBrace
			  | IF condition lBrace statements rBrace ELSE lBrace statements rBrace
	"""
	if len(p)==6:
		p[0] = IF(p[2], p[4])
	else:
		p[0] = IF(p[2], p[4], p[8])

def p_statements(p):
	"""
	statements : statements statement
			   | statement
	"""
	if len(p)==2:
		p[0]=[p[1]]
	elif len(p)==3:
		p[1].append(p[2])
		p[0]=p[1]
def p_statement_assign(p):
	"""
	statement : SET identifier EQ expr
	"""
	p[0]=ASSIGNMENT(p[2], p[3], p[4])
def p_statement_run(p):
	"""
	statement : RUN run_args
	"""
	p[0]=RUN(p[2])
def p_atom(p):
	"""
	atom : int
		 | string
		 | identifier
		 | lParen expr rParen
	"""
	if len(p)==4:
		p[0]=p[2]
	else:
		p[0]=VALUE(p[1])

def p_factor(p):
	"""
	factor : atom mul atom
		   | atom div atom
		   | atom
	"""
	if len(p)==4:
		p[0]=BINARYOP(p[1], p[2], p[3])
	else:
		p[0]=p[1]

def p_expr(p):
	"""
	expr : factor plus factor
		 | factor minus factor
		 | factor
	"""
	if len(p)==4:
		p[0]=BINARYOP(p[1], p[2], p[3])
	else:
		p[0]=p[1]
def p_error(p):
	raise SyntaxError("Syntax error at '%s'" % p.value if p else "Syntax error at EOF")
def t_error(t):
	raise SyntaxError(f"Invalid character: {t}")
class Interpreter:
	def __init__(self, script_runner):
		self.variables = {}
		self.script_runner=script_runner

	def interpret(self, node):
		if isinstance(node, list):
			for child in node:
				self.interpret(child)
		elif isinstance(node, ASSIGNMENT):
			self.variables[node.left] = self.evaluate(node.right)
		elif isinstance(node, IF):
			if self.evaluate(node.condition):
				self.interpret(node.statements)
			elif node.else_statements:
				self.interpret(node.else_statements)
		elif isinstance(node, RUN):
			self.run_command(node.args)
		else:
			raise Exception(f"Unknown node type: {type(node)}")

	def evaluate(self, node):
		if isinstance(node, VALUE):
			if node.value in self.variables:
				return self.variables[node.value]
			return node.value
		elif isinstance(node, BINARYOP):
			left = self.evaluate(node.left)
			right = self.evaluate(node.right)

			if node.op_token == '+':
				return left + right
			elif node.op_token == '-':
				return left - right
			elif node.op_token == '*':
				return left * right
			elif node.op_token == '/':
				return left / right
			else:
				raise Exception(f"Unknown operator: {node.op_token}")
		elif isinstance(node, CONDITION):
			left = self.evaluate(node.left)
			right = self.evaluate(node.right)
			if node.op_token == 'EQ':
				return left == right
			elif node.op_token == 'NEQ':
				return left != right
		elif isinstance(node, str):  # Assuming it's an identifier
			return self.variables.get(node, None)
		else:
			raise Exception(f"Unknown node type for evaluation: {type(node)}")

	def run_command(self, args):
		shell_input = " ".join(args)
		self.script_runner(shell_input)

def run_script(script_name, script_runner):
	if os.path.isfile(script_name):
		with open(script_name, "r") as f:
			content = f.read()
		lexer = lex.lex()
		parser = yacc.yacc()
		ast = parser.parse(content)
		interpreter = Interpreter(script_runner)
		interpreter.interpret(ast)