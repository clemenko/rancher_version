from flask import Flask, render_template, request, jsonify, redirect, url_for

import os
import requests
import json

version = "0.1"
app = Flask(__name__)

gh_token = os.getenv('GITHUB2_TOKEN')
if gh_token:
    headers = {'authorization': 'Bearer {}'.format(gh_token)}
else:
    headers = ""

def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    with requests.Session() as session:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('tag_name', '')
        return ''
        
def get_versions ():
    rke_data = json.loads(requests.get("https://update.rke2.io/v1-release/channels").text)
    rke_out = json.dumps(rke_data["data"][0]["latest"]).replace('"', '')

    k3s_data = json.loads(requests.get("https://update.k3s.io/v1-release/channels").text)
    k3s_out = json.dumps(k3s_data["data"][0]["latest"]).replace('"', '')

    cert_out = get_latest_release("cert-manager/cert-manager")
    rancher_out = get_latest_release("rancher/rancher")
    longhorn_out = get_latest_release("longhorn/longhorn")
    neuvector_out = get_latest_release("neuvector/neuvector")
    harvester_out = get_latest_release("harvester/harvester")
    hauler_out = get_latest_release("rancherfederal/hauler")

    return rancher_out, rke_out, k3s_out, longhorn_out, neuvector_out, cert_out, harvester_out, hauler_out


@app.route('/json', methods=['GET'])
def json_all_the_things():
    rancher_out, rke_out, k3s_out, longhorn_out, neuvector_out, cert_out, harvester_out, hauler_out = get_versions()

    return jsonify({'k3s stable': k3s_out, 'rke2 stable': rke_out, 'cert-manager': cert_out, 'rancher': rancher_out, 'longhorn': longhorn_out, 'neuvector': neuvector_out, 'harvester': harvester_out, 'hauler': hauler_out}), 200

@app.route('/', methods=['GET'])
def curl_all_the_things():
    rancher_out, rke_out, k3s_out, longhorn_out, neuvector_out, cert_out, harvester_out, hauler_out = get_versions()
    
    return render_template('index.html', rancher_ver=rancher_out, rke_ver=rke_out, k3s_ver=k3s_out, longhorn_ver=longhorn_out, neu_ver=neuvector_out, cert_ver=cert_out, harv_ver=harvester_out, hauler_ver=hauler_out)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False)
