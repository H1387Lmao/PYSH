import os
from pysh_essentials import *
import sys
import getpass

data={}
done_init=False

def init(no_save=False):
	global done_init
	if os.path.isdir("./pysh_subsystem"):
		get_data()
		return

	os.mkdir("./pysh_subsystem")

	while True:
		USERNAME = colored_input("&eEnter UNIX Username: ")
		for char in "!@#$%^*()/.,\\ :'\"{}()-=~`_+|<>\t\n":
			if char in USERNAME:
				break
		else:
			break
		colored_print("&cUsername has invalid characters.")
	PASSWORD = getpass.getpass(format_color("&eEnter Password: "))

	os.mkdir(f"./pysh_subsystem/{USERNAME}")

	write_data("Username", USERNAME)
	write_data("Password", PASSWORD)
	write_data("Home_Directory", f"/{USERNAME}")
	get_data()

def get_user():
	get_data()
	return data.get("Username", format_color("&c???"))

def get_data():
	global data
	if os.path.isfile("./pysh_subsystem/.userdata"):
		with open("./pysh_subsystem/.userdata", 'r') as f:
			data = format_data(f.read())
			return data
	else:
		return
def get_root_pass():
	get_data()
	return data.get("Password", format_color("&c???"))
def get_home():
	get_data()
	if data.get("Home_Directory", None) is None:
		colored_print("&cUnable to find home directory!")
	return data.get("Home_Directory", format_color("&c???"))