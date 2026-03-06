import modal

app = modal.App("rootstock-admin")
app.image = (
    modal.Image.debian_slim()
    .pip_install("fastapi[standard]", "jinja2")
    .add_local_dir("./templates/", remote_path="/templates")
)

vol = modal.Volume.from_name("rootstock-admin", create_if_missing=True)


@app.function(volumes={"/data": vol})
@modal.fastapi_endpoint(method="POST")
def manifest(manifest: dict):
    import json

    name = manifest.get("cluster")
    with open(f"/data/{name}.json", "w") as f:
        json.dump(manifest, f)
    return manifest


fake_manifest = {
    "schema_version": "1",
    "cluster": "della",
    "root": "/scratch/gpfs/SHARED/rootstock",
    "maintainer": {"name": "Hayden Holbrook", "email": "hholbrook@uchicago.edu"},
    "rootstock_version": "0.5.0",
    "python_version": "3.10.19",
    "last_updated": "2026-03-05T14:30:00Z",
    "environments": {
        "mace_env": {
            "status": "ready",
            "built_at": "2026-03-01T12:05:00Z",
            "source_hash": "sha256:abc123...",
            "python_requires": ">=3.10",
            "dependencies": {"mace-torch": "0.3.6", "torch": "2.2.0", "ase": "3.23.0"},
            "checkpoints": ["small", "medium", "large"],
        },
        "uma_env": {
            "status": "ready",
            "built_at": "2026-03-03T09:00:00Z",
            "source_hash": "sha256:def456...",
            "python_requires": ">=3.10",
            "dependencies": {"fairchem-core": "1.2.0", "torch": "2.2.0"},
            "checkpoints": ["uma-s-1p1"],
        },
    },
}


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
