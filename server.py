import os
import json
import subprocess
import requests
from flask import Flask, request
from threading import Thread

k8sinfra_url = os.getenv('K8SINFRA_URL')

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
        'status' : "",
        'url' : ""
    }

    thread = Thread(target=build, args=(title, True))
    thread.daemon = True
    thread.start()

    with open('repo.json', 'w') as json_file:
        json.dump(repo_data, json_file, indent=4)

    return {
        'result' : "build start"
    }

@app.route('/repo/<title>', methods=['PUT'])
def update_repo_info(title):
    json_data = request.get_json(force=True)
    repo = repo_data.get(title)
    if 'status' in json_data:
        repo['status'] = json_data['status']
    if 'url' in json_data:
        repo['url'] = json_data['url']
    return "update";


@app.route('/repo/<title>', methods=['GET'])
def view_repo_info(title):
    return repo_data.get(title)

@app.route('/hook/<title>', methods=['POST'])
def update_repo(title):
    thread = Thread(target=build, args=(title, ))
    thread.daemon = True
    thread.start()
    return "200"

def build(title, isNew=False):
    repo = repo_data.get(title)
    repo['version'] += 1

    cmd_list = [
        ["gcloud", "auth", "print-access-token", "|", "docker", "login", "-u", "oauth2accesstoken" "--password-stdin" "https://asia.gcr.io"],
        ["rm", repo['name'], "-rf"],
        ["git", "clone", f"https://{repo['token']}{'@' if repo['token'] != '' else ''}github.com/{repo['owner']}/{repo['name']}", "-b", repo['branch'], "--single-branch"],
        ["docker", "build", "-t", f"{title}:{repo['version']}", repo['name']],
        ["docker", "tag", f"{title}:{repo['version']}", f"{title}:latest"],
        ["docker", "tag", f"{title}:{repo['version']}", f"asia.gcr.io/k8stestinfra/{title}"],
        ["docker", "push", f"asia.gcr.io/k8stestinfra/{title}"],
        ["rm", repo['name'], "-rf"]
    ]

    for cmd in cmd_list :
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = result.communicate()
        log = out.decode('utf-8') + err.decode('utf-8')
        repo['status'] = log

    repo['status'] = "Build Success."
    with open('repo.json', 'w') as json_file:
        json.dump(repo_data, json_file, indent=4)

    data = {
            "project_name" : title
            "image" : f"{title}:latest"
            "ports" : [8080],
            "envs" : None
        }

    if isNew :
        resp = requests.post(f"{k8sinfra_url}/create", json=data)
    else :
        resp = requests.post(f"{k8sinfra_url}/update", json=data)
    
    print(resp.json())

#run dev server.
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)