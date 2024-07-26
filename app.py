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

def get_from_github(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    with requests.Session() as session:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('tag_name', '')
        return ''
        
def get_from_channels(channel):
    temp_data = json.loads(requests.get("https://update.{}.io/v1-release/channels".format(channel)).text)
    head, sep, tail = json.dumps(temp_data["data"][0]["latest"]).replace('"', '').partition('+')
    return head

def get_versions ():
    rke_out = get_from_channels("rke2")
    k3s_out = get_from_channels("k3s")
    rancher_out = get_from_channels("rancher")
    #rancher_out = get_from_github("rancher/rancher")

    cert_out = get_from_github("cert-manager/cert-manager")
    longhorn_out = get_from_github("longhorn/longhorn")
    neuvector_out = get_from_github("neuvector/neuvector")
    harvester_out = get_from_github("harvester/harvester")
    hauler_out = get_from_github("rancherfederal/hauler")

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
