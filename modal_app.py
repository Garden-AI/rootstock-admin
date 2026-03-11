import modal
import os

app = modal.App("rootstock-admin")
app.image = (
    modal.Image.debian_slim()
    .pip_install("fastapi[standard]", "jinja2")
    .add_local_dir("./templates/", remote_path="/templates")
)

env = os.environ.get("MODAL_ENVIRONMENT", "dev")
vol = modal.Volume.from_name(f"rootstock-admin-{env}", create_if_missing=True)


@app.function(volumes={"/data": vol})
@modal.fastapi_endpoint(method="POST", requires_proxy_auth=True)
def manifest(manifest: dict):
    import json

    vol.reload()
    name = manifest.get("cluster")
    with open(f"/data/{name}.json", "w") as f:
        json.dump(manifest, f)

    vol.commit()
    return manifest


@app.function(volumes={"/data": vol})
@modal.fastapi_endpoint()
def dashboard():
    import json
    from datetime import datetime
    from pathlib import Path
    from fastapi.responses import HTMLResponse
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    vol.reload()

    env = Environment(
        loader=FileSystemLoader("/templates"),
        autoescape=select_autoescape(),
    )
    t = env.get_template("index.html.jinja")

    manifest_path = Path("/data")
    manifest_files = manifest_path.glob("*.json")
    manifests = []
    for mf in manifest_files:
        with open(mf, "r") as f:
            data = json.load(f)
            if "last_updated" in data:
                try:
                    dt = datetime.fromisoformat(data["last_updated"])
                    data["last_updated"] = dt.strftime("%b %d, %Y")
                except ValueError:
                    pass
            manifests.append(data)

    return HTMLResponse(t.render(manifests=manifests))
