from flask import Flask, abort, request
import os
import random
Server = Flask(__name__)

root = "./pysh_extra_cmds"

KEYLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYLIST+=KEYLIST.lower()
KEYLIST+="0123456789"
KEYLIST = list(KEYLIST)

@Server.get("/download/<app_name>/v/<app_version>")
def app_download(app_name, app_version):
	if os.path.isdir(root+"/"+app_name):
		if os.path.isfile(root+"/"+app_name+"/"+app_version+".pysh"):
			with open(f"{root}/{app_name}/{app_version}.pysh","r", encoding="utf8") as f:
				return f.read()
		abort(404)
		return "INVALID VERSION!"
	else:
		abort(404)
		return "APP NAME NOT FOUND"

@Server.errorhandler(404)
def handle_bad_request404(e):
    return 'This App or App Version is not found.', 404
@Server.errorhandler(405)
def handle_bad_request405(e):
    return 'This App already exists.', 405

@Server.get("/upload/new/<app_name>")
def create_new_app(app_name):
	if os.path.isdir(root+"/"+app_name):
		abort(405)
	else:
		os.mkdir(root+"/"+app_name)
		s=create_key()
		with open(root+"/"+app_name+"/__key.env", "w") as f:
			f.write(s)
		return s

def create_key():
	s=""
	for i in range(32):
		s+=random.choice(KEYLIST)
	return s

@Server.get("/upload/<app_name>/<app_key>/new")
def app_upload_new_version(app_name, app_key):
	if os.path.isdir(root+"/"+app_name):
		with open(root+"/"+app_name+"/__key.env","r", encoding="utf8") as f:
			key=f.read()

		if key != app_key:
			abort(404)
			return

		content = request.args.get('content')
		latest=0
		for version in os.listdir(root+"/"+app_name):
			if version == "__key.env":
				continue
			version_num = version.removesuffix(".pysh")
			if latest < int(version_num):
				latest = int(version_num)
		latest+=1
		with open(root+"/"+app_name+f"/{latest}.pysh", "w") as f:
			f.write(content)
		return "Successfully Updated!"
	else:
		abort(404)
@Server.get("/info/<app_name>/version")
def app_get_version_latest(app_name):
	for version in os.listdir(root+"/"+app_name):
		if version == "__key.env":
			continue
		version_num = version.removesuffix(".pysh")
		latest=-1
		if latest < int(version_num):
			latest = int(version_num)
		else:
			if latest==-1:
				abort(404)
				return "NO VERSION FOR THIS APP IS FOUND"
		return str(latest)
@Server.get("/download/<app_name>")
def app_download_latest(app_name):
	if os.path.isdir(root+"/"+app_name):
		latest=-1
		for version in os.listdir(root+"/"+app_name):
			if version == "__key.env":
				continue
			version_num = version.removesuffix(".pysh")
			if latest < int(version_num):
				latest = int(version_num)
		else:
			if latest==-1:
				abort(404)
				return "NO VERSION FOR THIS APP IS FOUND"
		with open(f"{root}/{app_name}/{latest}.pysh","r", encoding="utf8") as f:
			return f.read()
	else:
		abort(404)
		return "APP NAME NOT FOUND"

Server.run(host="0.0.0.0")