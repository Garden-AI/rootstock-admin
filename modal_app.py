import modal

app = modal.App("rootstock-admin")
app.image = (
    modal.Image.debian_slim()
    .pip_install("fastapi[standard]", "jinja2")
    .add_local_dir("./templates/", remote_path="/templates")
)

vol = modal.Volume.from_name("rootstock-admin", create_if_missing=True)


@app.function(volumes={"/data": vol})
@modal.fastapi_endpoint(method="POST", requires_proxy_auth=True)
def manifest(manifest: dict):
    import json

    name = manifest.get("cluster")
    with open(f"/data/{name}.json", "w") as f:
        json.dump(manifest, f)
    return manifest


@app.function(volumes={"/data": vol})
@modal.fastapi_endpoint()
def dashboard():
    import json
    from pathlib import Path
    from fastapi.responses import HTMLResponse
    from jinja2 import Environment, FileSystemLoader, select_autoescape

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
            manifests.append(json.load(f))

    return HTMLResponse(t.render(manifests=manifests))
