from flask import Flask, request, Response
import requests
import logging
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
app = Flask(__name__, static_folder=None)

DOMAIN_TARGETS = {
    "<dominio1>": "<ip_aplicacao1>",
    "<dominio2>": "<ip_aplicacao2>",
}

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def proxy(path):
    host_header = request.headers.get("X-Forwarded-Host") or request.host
    host = host_header.split(":")[0] 

    target_url = DOMAIN_TARGETS.get(host)
    if not target_url:
        return Response(f"Domínio {host} não configurado.", status=400)

    # Ignorar arquivos .map
    if path.endswith(".map"):
        return Response("", status=200, content_type="application/json")

    # Montar URL final
    full_url = urljoin(target_url + "/", path)

    resp = requests.request(
        method=request.method,
        url=full_url,
        headers={k: v for k, v in request.headers if k.lower() != 'host'},
        params=request.args,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=True,
        stream=True
    )

    body = resp.content

    excluded_headers = ["content-encoding", "transfer-encoding", "content-length", "connection"]
    headers = [(name, value) for (name, value) in resp.headers.items() if name.lower() not in excluded_headers]

    return Response(body, status=resp.status_code, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
