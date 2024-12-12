import sys
from pysh_essentials import *

if __file__.startswith("/") or __file__.startswith("\\"):
	colored_print("&cLinux is currently unsupported!")
	colored_print("&cPlease use a superior file system!")
	sys.exit()
print("""
Welcome to PYSH (Python Shell V1.0)

Github Repository : https://github.com/H1387Lmao/PYSH
""".strip())

import traceback
import time
import os
import functools
import difflib
import keyboard
import pysh_filemgr as filemgr
from pysh_interpreter import run_script
import math
import getpass

IS_SUDO=False
IS_CONFIRMED=False

def trace_function_calls(frame, event, arg):
	if event == "line":
		code = frame.f_code
		filename = code.co_filename
		if filename.startswith('<'):
			# If the filename starts with '<', it's a frozen module, so we can't open it
			return trace_function_calls
		lineno = frame.f_lineno
		try:
			with open(filename, "r") as f:
				lines = f.readlines()
				line_of_code = lines[lineno - 1].strip()
		except OSError as e:
			print(f"Error: {e}")
			print(f"Invalid filename: {filename}")
			return trace_function_calls
		if trace_function_calls.cancelled:
			raise KeyboardInterrupt  # Stop execution
	return trace_function_calls

trace_function_calls.cancelled = False  # Attribute to track cancellation

def trace_decorator(func):
	@functools.wraps(func)  # Preserve the original function's metadata
	def wrapper(*args, **kwargs):
		sys.settrace(trace_function_calls)
		try:
			result = func(*args, **kwargs)
		except KeyboardInterrupt:
			colored_print(f"&c'{func.__name__}'  cancelled.")
			sys.stderr = sys.__stderr__
		finally:
			sys.settrace(None)
		return None
	return wrapper

def move_down_hierarchy(target_path):
	global PWD
	
	PWD_WithoutRoot = PWD.removeprefix(PWD[:1])
	if target_path.startswith("~"):
		PWD = filemgr.get_home()
		return True
	if target_path.startswith('..'):
		if PWD == "/":
			return True
		target = "/".join(PWD_WithoutRoot.split("/")[:-1])
		if not target:
			target = "/"
		PWD = target
		if not PWD.startswith("/"):
			PWD = "/"+PWD
		return True
	else:
		target = f"./pysh_subsystem{PWD}/{target_path}"
		if os.path.isdir(target):
			PWD += "/"+target_path
			if PWD.removeprefix("/").startswith("/"):
				PWD = PWD.removeprefix("/")
			return True
		else:
			if os.path.isfile(target):
				colored_print(f"&c'{target_path}' is a file")
				return False
			else:
				colored_print(f"&c'{target_path}' is not found.")
				return False

@trace_decorator
def cd(*args, **kwargs):
	global PWD
	old = PWD
	if len(args[0]) >= 1:
		target_path = args[0][0]
		if target_path.startswith("/"):
			PWD = "/"
			target_path = target_path[1:]
		sub_paths = target_path.split("/")
		if sub_paths[-1]==".." and len(sub_paths)!=1:
			colored_print("&cE: &fPerhaps you forgot to put '/' ?")
		for path in sub_paths:
			if not move_down_hierarchy(path):
				PWD = old
	else:
		colored_print("&cNo target location passed.")
		return
@trace_decorator
def quit(*args, **kwargs):
	sys.exit(0)

@trace_decorator
def clear(*args, **kwargs):
	try:
		os.system("cls")
	except:
		os.system("clear")
def run(*args, **kwargs):
	global run_command
	if len(args[0]) >= 1:
		if args[0][0].endswith(".py"):
			colored_print(f"&cUnable to run {args[0][0]}, because the specified extenstion is a python file.")
			return
		abs_path=__file__.removesuffix("\\pysh.py")+f"/pysh_subsystem/{PWD[1:]}".replace("/", "\\")
		try:
			run_script(f"{abs_path}\\{args[0][0]}", run_command)
		except Exception as e:
			colored_print(f"&cAn error occured when compiling!")
			colored_print(f"&c{e}")
	else:
		colored_print("&cNo target script passed.")
		return
@trace_decorator
def pwd(*args, **kwargs):
	print(format_PWD(PWD, filemgr.get_data()))

@trace_decorator
def sudo(*args, **kwargs):
	global IS_SUDO
	global IS_CONFIRMED
	if not IS_SUDO:
		password=getpass.getpass(format_color("&8Enter your password: "))
		if password != filemgr.get_root_pass():
			colored_print("&cIncorrect password.")
			return
		IS_SUDO=True
		IS_CONFIRMED = True
	if len(args[0])<1:
		colored_print("&cNo command passed.")
		return
	else:
		run_command(" ".join(args[0]), is_root=True)

@trace_decorator
def cat(*args, **kwargs):
	global IS_CONFIRMED
	is_root = kwargs.get("root")

	if not is_root:
		if not PWD.startswith("/hello"):
			colored_print("&cAccess Denied")
			return
	if len(args[0]) >= 1:
		abs_path = get_abs()
		for file in args[0]:
			path = abs_path+"/"+file
			if os.path.isfile(path):
				if not kwargs.get("is_confirmed"):
					if file==".userdata":
						password=getpass.getpass(format_color("&8Enter your password: "))
						if password != filemgr.get_root_pass():
							colored_print("&cIncorrect password.")
							return
				colored_print(f"&b{file}")
				with open(path, 'r') as f:
					print(f.read())
			else:
				colored_print(f"&cFile not found: '{file}'.")
				continue
	else:
		colored_print("&cNo target file passed.")
	


@trace_decorator
def abs_pwd(*args, **kwargs):
	abs_path=__file__.removesuffix("\\pysh.py")+f"/pysh_subsystem/{PWD[1:]}".replace("/", "\\")
	print(abs_path)

def get_abs():
	abs_path=__file__.removesuffix("\\pysh.py")+f"/pysh_subsystem/{PWD[1:]}".replace("/", "\\")
	return abs_path

def is_command(func):
	if callable(func):
		return hasattr(func, '__wrapped__')
	return False

def ask():
	global PWD
	try:
		FORMATTED_PWD = format_PWD(PWD, filemgr.get_data())
		colored_print(f"&9PYSH&a@{filemgr.get_user()}&f:&9{FORMATTED_PWD}&f$", end=" ")
		return input().strip()
	except EOFError:
		sys.stderr = sys.__stderr__
		return ""
	except KeyboardInterrupt:
		colored_print("&c^C")
		sys.stderr = sys.__stderr__
		return ""



def get_possible_commands(input_command):
	if not input_command:
		return
	suggestions = difflib.get_close_matches(input_command, commands, n=1, cutoff=0.6)

	if suggestions:
		colored_print(f"&eDid you mean this command: {suggestions[0]} (Y/N)", end="\n: ")
		try:
			choice = input().lower()
		except KeyboardInterrupt:
			sys.stderr = sys.__stderr__
			print("n")
			return
		except EOFError:
			sys.stderr = sys.__stderr__
		if choice == "y":
			return suggestions[0]
		elif choice == "n":
			colored_print("&eAll available commands:")
			suggestions = difflib.get_close_matches(input_command, commands, n=3, cutoff=0.6)
			for suggestion in suggestions:
				colored_print(f"&b - {suggestion}")
			return False
		else:
			return False
	else:
		colored_print(f"&cCommand not found: '{input_command}'")
		return False

def ls(*args, **kwargs):
	global PWD

	is_root = kwargs.get("root")

	if not is_root:
		if not PWD.startswith("/hello"):
			colored_print("&cAccess Denied")
			return

	# Get the list of files and folders
	abs_path = __file__.removesuffix("\\pysh.py")+f"/pysh_subsystem/{PWD[1:]}".replace("/", "\\")
	files_and_folders = os.listdir(f"{abs_path}")

	max_length = max(len(item) for item in files_and_folders) if files_and_folders else 0

	num_columns = int(math.sqrt(len(files_and_folders)))
	if num_columns * num_columns < len(files_and_folders):
		num_columns += 1

	# Print the grid
	for i in range(0, len(files_and_folders), num_columns):
		row = files_and_folders[i:i+num_columns]
		for item in row:
			if os.path.isfile(f"{abs_path}\\{item}"):
				color = "&f"
				if item.endswith(".userdata"):
					color="&8"
				for img in image_formats:
					if item.upper().endswith(f".{img}"):
						color = "&d"
						break
				colored_print(f"{color}{item.ljust(max_length)}", end="  ")
			else:
				colored_print(f"&1{item.ljust(max_length)}", end="  ")
		print()
		

@trace_decorator
def echo(*args, **kwargs):
	if len(args)==0:
		print("")
	else:
		print(" ".join(args[0]))

def run_command(shell_input, is_root=False):
	global IS_CONFIRMED
	if not shell_input.strip():
		return

	args = shell_input.split(" ")

	cmdlet = args.pop(0)

	if cmdlet in commands:
		globals()[cmdlet](args, root=is_root, is_confirmed=IS_CONFIRMED)
		IS_CONFIRMED=False
	else:
		try:
			command = get_possible_commands(cmdlet)
			if command:
				globals()[command](args)
		except KeyboardInterrupt:
			pass
commands = [command.__name__ for command in globals().values() if is_command(command)]
commands.append("run")
commands.append("ls")
def start_shell():
	global PWD
	sys.stderr = sys.__stderr__
	os.system("cls" if os.name == "nt" else "clear")
	PWD=filemgr.get_home()
	while True:
		try:
			shell_input = ask()
		except KeyboardInterrupt:
			sys.stderr = sys.__stderr__
			colored_print("&c^C")
			continue
		except EOFError:
			sys.stderr = sys.__stderr__
			continue
		run_command(shell_input)

if __name__ == "__main__":
	PWD = format_color("&c???")

	filemgr.init(no_save=True)
	start_shell()
