import os
import json
import subprocess
from flask import Flask, request

app = Flask(__name__)

try :
    json_file = open('repo.json', 'r')
    repo_data = json.load(json_file)
except IOError :
    repo_data = {}
else :
    json_file.close()

@app.route('/', methods=['GET'])
def index():
    return "docker build System."

@app.route('/repo', methods=['POST'])
def add_repo():
    #get information to db from post body.
    #repo name -> reponame_branch
    #branch name -> branch_name
    json_data = request.get_json(force=True)
    title = json_data.get('title')
    url = json_data.get('url').split('/')
    owner = url[-2]
    repo_name = url[-1]
    token = json_data.get('token', '')
    branch = json_data.get('branch', 'master')
    
    repo_data[title] = {
        'owner' : owner,
        'name' : repo_name,
        'token' : token,
        'branch' : branch,
        'version' : 0,
        'log' : ""
    }
    
    build(title)

    with open('repo.json', 'w') as json_file:
        json.dump(repo_data, json_file, indent=4)


    return {
        'result' : "success"
    }

@app.route('/repo/<title>', methods=['GET'])
def view_repo_info(title):
    return repo_data.get(title)

@app.route('/hook/<title>', methods=['POST'])
def update_repo(title):
    build(title)
    return "200"

def build(title):
    repo = repo_data.get(title)
    repo['version'] += 1

    cmd_list = [
        ["rm", repo['name'], "-rf"],
        ["git", "clone", f"https://{repo['token']}{'@' if repo['token'] != '' else ''}github.com/{repo['owner']}/{repo['name']}", "-b", repo['branch'], "--single-branch"],
        ["docker", "build", "-t", f"{title}:{repo['version']}", repo['name']],
        ["rm", repo['name'], "-rf"]
    ]

    for cmd in cmd_list :
        print(cmd)
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = result.communicate()
        log = out.decode('utf-8') + err.decode('utf-8')
        repo['log'] = log

    repo['log'] = "Build Success."
    with open('repo.json', 'w') as json_file:
        json.dump(repo_data, json_file, indent=4)

#run dev server.
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)