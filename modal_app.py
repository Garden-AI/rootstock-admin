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


@app.function(volumes={"/data": vol}, min_containers=1)
@modal.asgi_app()
def dashboard():
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    web_app = FastAPI()
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @web_app.get("/")
    def get_manifests():
        import json
        from pathlib import Path

        vol.reload()
        manifests = [json.loads(p.read_text()) for p in Path("/data").glob("*.json")]
        return {"manifests": manifests}

    return web_app
