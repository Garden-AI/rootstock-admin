import modal
import os

app = modal.App("rootstock-admin")
app.image = modal.Image.debian_slim().pip_install("fastapi[standard]")

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
    from pathlib import Path

    vol.reload()

    manifest_path = Path("/data")
    manifest_files = manifest_path.glob("*.json")
    manifests = []
    for mf in manifest_files:
        with open(mf, "r") as f:
            manifests.append(json.load(f))

    return {"manifests": manifests}
