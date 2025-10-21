import json
import sys

from fastapi import Request
from fastapi.responses import Response

from app import app
from gateway.chatgpt import chatgpt_html

# Load gpts_context.json with PyInstaller compatibility
def load_gpts_context():
    try:
        # Try to load from bundled resources first (PyInstaller)
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            import pkgutil
            data = pkgutil.get_data(__name__, '../templates/gpts_context.json')
            if data:
                return json.loads(data.decode('utf-8'))
        
        # Fallback to file system
        with open("templates/gpts_context.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load gpts_context.json: {e}")
        return {}

gpts_context = load_gpts_context()


@app.get("/gpts")
async def get_gpts():
    return {"kind": "store"}


@app.get("/g/g-{gizmo_id}")
async def get_gizmo_json(request: Request, gizmo_id: str):
    params = request.query_params
    if params.get("_data") == "routes/g.$gizmoId._index":
        return Response(content=json.dumps(gpts_context, indent=4), media_type="application/json")
    else:
        return await chatgpt_html(request)
