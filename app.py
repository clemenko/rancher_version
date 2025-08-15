from flask import Flask, render_template, jsonify
from flask_caching import Cache
import os
import json
import asyncio
import httpx
from threading import Thread
from time import sleep
from typing import Dict

# ----------------------------
# App configuration
# ----------------------------
version = "2.1"
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# GitHub API configuration
GITHUB_TOKEN = os.getenv('GITHUB2_TOKEN')
HEADERS = {'Authorization': f'Bearer {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}

# Store the latest version data in memory
version_cache: Dict[str, str] = {}

# ----------------------------
# Async API Helper Functions
# ----------------------------
async def fetch_github_release(client: httpx.AsyncClient, repo: str) -> str:
    """Fetch the latest GitHub release tag for a given repo."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json().get('tag_name', '') or "no release found"
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        app.logger.error(f"GitHub API error for {repo}: {e}")
        return "error fetching release"

async def fetch_channel_version(client: httpx.AsyncClient, channel: str) -> str:
    """Fetch the latest stable version from the channel API."""
    url = f"https://update.{channel}.io/v1-release/channels"
    try:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        head, _, _ = json.dumps(data["data"][0]["latest"]).replace('"', '').partition('+')
        return head
    except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, KeyError, IndexError) as e:
        app.logger.error(f"Channel API error for {channel}: {e}")
        return "upstream server issue"

# ----------------------------
# Version Aggregation
# ----------------------------
async def get_versions_async() -> Dict[str, str]:
    """Fetch versions for all monitored applications in parallel."""
    sources = {
        "rancher": ("github", "rancher/rancher"),
        "rke2 stable": ("channel", "rke2"),
        "k3s stable": ("channel", "k3s"),
        "longhorn": ("github", "longhorn/longhorn"),
        "neuvector": ("github", "neuvector/neuvector"),
        "cert-manager": ("github", "cert-manager/cert-manager"),
        "harvester": ("github", "harvester/harvester"),
        "hauler": ("github", "hauler-dev/hauler"),
    }

    async with httpx.AsyncClient(headers=HEADERS) as client:
        tasks = [
            fetch_github_release(client, identifier) if source_type == "github"
            else fetch_channel_version(client, identifier)
            for _, (source_type, identifier) in sources.items()
        ]
        results = await asyncio.gather(*tasks)

    return dict(zip(sources.keys(), results))

# ----------------------------
# Background Cache Refresher
# ----------------------------
def refresh_versions(interval: int = 1800):
    """Refresh the in-memory cache every `interval` seconds."""
    global version_cache
    while True:
        app.logger.info("Refreshing version cache...")
        try:
            version_cache = asyncio.run(get_versions_async())
            app.logger.info(f"Cache updated: {version_cache}")
        except Exception as e:
            app.logger.error(f"Error refreshing version cache: {e}")
        sleep(interval)

# Start background refresh thread
Thread(target=refresh_versions, daemon=True).start()

# ----------------------------
# Flask Routes
# ----------------------------
@app.route('/json', methods=['GET'])
def json_all_the_things():
    return jsonify(version_cache), 200

@app.route('/', methods=['GET'])
def curl_all_the_things():
    return render_template('index.html', **{
        "rancher_ver": version_cache.get("rancher", "loading..."),
        "rke_ver": version_cache.get("rke2 stable", "loading..."),
        "k3s_ver": version_cache.get("k3s stable", "loading..."),
        "longhorn_ver": version_cache.get("longhorn", "loading..."),
        "neu_ver": version_cache.get("neuvector", "loading..."),
        "cert_ver": version_cache.get("cert-manager", "loading..."),
        "harv_ver": version_cache.get("harvester", "loading..."),
        "hauler_ver": version_cache.get("hauler", "loading..."),
    })

# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == '__main__':
    # Warm up cache before first request
    version_cache = asyncio.run(get_versions_async())
    app.run(host='0.0.0.0', debug=False)
