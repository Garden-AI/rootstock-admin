# Rootstock Admin

Admin backend for the [Rootstock](https://github.com/Garden-AI/rootstock) project. This is a [Modal](https://modal.com) app that collects and displays environment manifests from Rootstock deployments across different clusters.

## Overview

Rootstock Admin provides a central dashboard for monitoring Rootstock installations. Clusters periodically report their environment configurations via POST requests, and the dashboard displays this information in a web UI.

## Endpoints

| Environment | Endpoint | URL |
|-------------|----------|-----|
| Dev | Dashboard | https://garden-ai-dev--rootstock-admin-dashboard.modal.run |
| Dev | Manifest API | https://garden-ai-dev--rootstock-admin-manifest.modal.run |
| Prod | Dashboard | https://garden-ai-prod--rootstock-admin-dashboard.modal.run |
| Prod | Manifest API | https://garden-ai-prod--rootstock-admin-manifest.modal.run |

### Manifest API `POST`
Receives and stores environment manifests from Rootstock clusters. Requires proxy authentication.

**Payload:** JSON manifest containing cluster name, rootstock version, Python version, maintainer info, and environment details.

### Dashboard `GET`
Public dashboard displaying all registered clusters and their environments. Shows:
- Cluster metadata (name, version, root path, maintainer)
- Environment status, dependencies, source code, and checkpoints

## Development

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- [Modal](https://modal.com) account and CLI configured

### Setup
```bash
uv sync
```

### Run locally
```bash
modal serve modal_app.py
```

### Deploy
```bash
# Development
modal deploy modal_app.py

# Production
modal deploy --env=prod modal_app.py
```

The app uses separate Modal volumes for dev and prod environments (`rootstock-admin-dev` and `rootstock-admin-prod`).

## Project Structure

```
├── modal_app.py              # Modal app with manifest and dashboard endpoints
├── templates/
│   └── index.html.jinja      # Dashboard template
├── pyproject.toml
└── uv.lock
```
