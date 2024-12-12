import keyboard
import sys
import os
color_codes = {
		'0': '\033[30m',  # Black
		'1': '\033[34m',  # Dark Blue
		'2': '\033[32m',  # Dark Green
		'3': '\033[36m',  # Dark Aqua
		'4': '\033[31m',  # Dark Red
		'5': '\033[35m',  # Dark Purple
		'6': '\033[33m',  # Gold
		'7': '\033[37m',  # Gray
		'8': '\033[90m',  # Dark Gray
		'9': '\033[94m',  # Blue
		'a': '\033[92m',  # Green
		'b': '\033[96m',  # Aqua
		'c': '\033[91m',  # Red
		'd': '\033[95m',  # Light Purple
		'e': '\033[93m',  # Yellow
		'f': '\033[97m',  # White
		"g": '\033[1;34m',
		'r': '\033[0m',   # Reset
	}
class VALUE:
	def __init__(self, value):
		self.value=value
	def __repr__(self):
		return str(self.value)
class SCOPE:
	def __init__(self, statements):
		self.statements=statements
	def __repr__(self):
		return str(self.statements)
class RUN:
	def __init__(self, command_args):
		self.args = command_args
	def __repr__(self):
		return f"RUN ({'  '.join(self.args)})"
class BINARYOP:
	def __init__(self, left, op, right):
		self.left=left
		self.right=right
		self.op_token=op
	def __repr__(self):
		return f"BINARY: ({self.left} {self.op_token} {self.right})"
class CONDITION:
	def __init__(self, left, op_token, right):
		self.left = left
		self.right=right
		self.op_token=op_token

	def __repr__(self):
		return f"CONDITION: ({self.left} {self.op_token} {self.right})"
class ASSIGNMENT:
	def __init__(self, left, op_token, right):
		self.left = left
		self.right=right
		self.op_token=op_token

	def __repr__(self):
		return f"ASSIGN: ({self.left} {self.op_token} {self.right})"
class IF:
	def __init__(self, condition, if_statements, else_statements=None):
		self.condition = condition
		self.statements = if_statements
		self.else_statements = else_statements
	def __repr__(self):
		if_statements_str = ', '.join(map(str, self.statements))
		if self.else_statements:
			else_statements_str = ', '.join(map(str, self.else_statements))
			return f"IF {self.condition} THEN [{if_statements_str}] ELSE [{else_statements_str}]"
		else:
			return f"IF {self.condition} THEN [{if_statements_str}]"

def colored_input(text):
	result = ""
	i = 0
	while i < len(text):
		if text[i] == '&' and i + 1 < len(text) and text[i + 1] in color_codes:
			result += color_codes[text[i + 1]]
			i += 2
		else:
			result += text[i]
			i += 1
	result += '\033[0m'
	print(result, end="")
	try:
		return input().strip()
	except KeyboardInterrupt:
		pass

def colored_print(text, end="\n"):

	result = ""
	i = 0
	while i < len(text):
		if text[i] == '&' and i + 1 < len(text) and text[i + 1] in color_codes:
			result += color_codes[text[i + 1]]
			i += 2
		else:
			result += text[i]
			i += 1
	result += '\033[0m'
	print(result, end=end)

def format_color(text):

	result = ""
	i = 0
	while i < len(text):
		if text[i] == '&' and i + 1 < len(text) and text[i + 1] in color_codes:
			result += color_codes[text[i + 1]]
			i += 2
		else:
			result += text[i]
			i += 1
	result += '\033[0m'
	return result

def format_data(data):
	dat={}
	for d in data.split("\n"):
		if not d.strip():
			continue
		key = d.split(":")[0]
		value = d.split(": ")[1]
		dat[key] = value
	return dat

datav=None

def format_PWD(PWD, data=datav):
	global datav
	if data!=None:
		datav=data

	if PWD.startswith(datav.get("Home_Directory")):
		return f"~{PWD.removeprefix(datav.get("Home_Directory"))}"
	A = PWD.replace("./", "")
	if A != "/":
		if PWD.startswith("/"):
			A = PWD.lstrip("/")
		elif PWD.endswith("/"):
			A = PWD.rstrip("/")
	return A

def write_data(k,v):
	with open("./pysh_subsystem/.userdata", "a") as f:
		f.write(f"{k}: {v}\n")

import json

def JSON_PRINT(ast):
	def convert_to_dict(node):
		if isinstance(node, list):
			return [convert_to_dict(child) for child in node]
		elif isinstance(node, VALUE):
			return node.value
		elif isinstance(node, SCOPE):
			return convert_to_dict(node.statements)
		elif isinstance(node, RUN):
			return {"RUN": node.args}
		elif isinstance(node, BINARYOP):
			return {"OP": node.op_token, "LEFT": convert_to_dict(node.left), "RIGHT": convert_to_dict(node.right)}
		elif isinstance(node, CONDITION):
			return {"OP": node.op_token, "LEFT": convert_to_dict(node.left), "RIGHT": convert_to_dict(node.right)}
		elif isinstance(node, ASSIGNMENT):
			return {"OP": node.op_token, "LEFT": convert_to_dict(node.left), "RIGHT": convert_to_dict(node.right)}
		elif isinstance(node, IF):
			if_statements = convert_to_dict(node.statements)
			else_statements = convert_to_dict(node.else_statements) if node.else_statements else None
			return {"IF": convert_to_dict(node.condition), "THEN": if_statements, "ELSE": else_statements}
		else:
			return str(node)
	ast_dict = convert_to_dict(ast)
	print(json.dumps(ast_dict, indent=4))

image_formats = [
	"BMP", "DIB", "RLE", "JPEG", "JPG", "JPE", "JFIF", "JFI", "JP2", "J2K", "JPF", "JPM", "JPX", "JPC",
	"PNG", "PBM", "PGM", "PPM", "PAM", "PNM", "PCX", "PCT", "PIC", "PXR", "PSD", "PSB", "PDD", "PDP",
	"GIF", "TIFF", "TIF", "TGA", "TARGA", "VDA", "VST", "VTF", "WBMP", "XBM", "XPM", "XWD", "YUV",
	"DDS", "EXR", "HDR", "KTX", "MNG", "PCD", "PIC", "PCT", "PGM", "PICT", "PNM", "PSD", "PSB", "PXR",
	"QOI", "RAS", "RGB", "RGBA", "SGI", "SUN", "SVG", "TGA", "TIFF", "TIF", "VTF", "WBMP", "XBM", "XPM",
	"YUV", "ZIF", "ZVI", "ZVR"
]
