from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# Get user's repositories
def get_user_repos(username, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(f"https://api.github.com/users/{username}/repos", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Transfer the repository to the new owner
def transfer_repo(repo, new_owner, username, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    data = {
        "new_owner": new_owner
    }
    response = requests.post(f"https://api.github.com/repos/{username}/{repo}/transfer", headers=headers, data=json.dumps(data))
    return response.status_code == 202

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_repos', methods=['POST'])
def get_repos():
    username = request.form['username']
    token = request.form['token']
    repos = get_user_repos(username, token)
    if repos is not None:
        return jsonify(repos)
    else:
        return jsonify({"error": "Unable to fetch repositories"})

@app.route('/transfer', methods=['POST'])
def transfer():
    repo = request.form['repo']
    new_owner = request.form['new_owner']
    username = request.form['username']
    token = request.form['token']
    success = transfer_repo(repo, new_owner, username, token)
    if success:
        return jsonify({"message": f"Repository {repo} transferred successfully to {new_owner}"})
    else:
        return jsonify({"error": f"Failed to transfer repository {repo}"})

if __name__ == '__main__':
    app.run(debug=True)
