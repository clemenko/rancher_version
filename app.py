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

def get_versions ():
    rke_data = json.loads(requests.get("https://update.rke2.io/v1-release/channels").text)
    rke_out = json.dumps(rke_data["data"][0]["latest"]).replace('"', '')

    late_rke_out = json.dumps(rke_data["data"][1]["latest"]).replace('"', '')

    k3s_data = json.loads(requests.get("https://update.k3s.io/v1-release/channels").text)
    k3s_out = json.dumps(k3s_data["data"][0]["latest"]).replace('"', '')

    k3s_rke_out = json.dumps(k3s_data["data"][1]["latest"]).replace('"', '')

    cert_data = json.loads(requests.get("https://api.github.com/repos/cert-manager/cert-manager/releases/latest", headers=headers).text)
    cert_out = json.dumps(cert_data["tag_name"]).replace('"', '')

    rancher_data = json.loads(requests.get("https://api.github.com/repos/rancher/rancher/releases/latest", headers=headers).text)
    rancher_out = json.dumps(rancher_data["tag_name"]).replace('"', '')

    longhorn_data = json.loads(requests.get("https://api.github.com/repos/longhorn/longhorn/releases/latest", headers=headers).text)
    longhorn_out = json.dumps(longhorn_data["tag_name"]).replace('"', '')

    neuvector_data = json.loads(requests.get("https://api.github.com/repos/neuvector/neuvector/releases/latest", headers=headers).text)
    neuvector_out = json.dumps(neuvector_data["tag_name"]).replace('"', '')

    harvester_data = json.loads(requests.get("https://api.github.com/repos/harvester/harvester/releases/latest", headers=headers).text)
    harvester_out = json.dumps(harvester_data["tag_name"]).replace('"', '')

    hauler_data = json.loads(requests.get("https://api.github.com/repos/rancherfederal/hauler/releases/latest", headers=headers).text)
    hauler_out = json.dumps(hauler_data["tag_name"]).replace('"', '')

    return rancher_out, rke_out, late_rke_out, k3s_out, k3s_rke_out, longhorn_out, neuvector_out, cert_out, harvester_out, hauler_out


@app.route('/json', methods=['GET'])
def json_all_the_things():
    rancher_out, rke_out, late_rke_out, k3s_out, k3s_rke_out, longhorn_out, neuvector_out, cert_out, harvester_out, hauler_out = get_versions()

    return jsonify({'k3s stable': k3s_out, 'k3s latest': k3s_rke_out, 'rke2 stable': rke_out, 'rke latest': late_rke_out, 'cert-manager': cert_out, 'rancher': rancher_out, 'longhorn': longhorn_out, 'neuvector': neuvector_out, 'harvester': harvester_out, 'hauler': hauler_out}), 200

@app.route('/', methods=['GET'])
def curl_all_the_things():
    rancher_out, rke_out, late_rke_out, k3s_out, k3s_rke_out, longhorn_out, neuvector_out, cert_out, harvester_out, hauler_out = get_versions()
    
    return render_template('index.html', rancher_ver=rancher_out, rke_ver=rke_out, late_rke_ver=late_rke_out, k3s_ver=k3s_out, late_k3s_ver=k3s_rke_out, longhorn_ver=longhorn_out, neu_ver=neuvector_out, cert_ver=cert_out, harv_ver=harvester_out, hauler_ver=hauler_out)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False)
