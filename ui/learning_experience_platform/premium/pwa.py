"""PWA helpers — manifest path, install prompt copy, SW registration snippet."""

from __future__ import annotations

from typing import Any


MANIFEST_PATH = "static/lxp/manifest.webmanifest"
SERVICE_WORKER_PATH = "static/lxp/sw.js"


def pwa_config() -> dict[str, Any]:
    return {
        "manifest": MANIFEST_PATH,
        "service_worker": SERVICE_WORKER_PATH,
        "installable": True,
        "offline_shell": True,
        "background_sync_tag": "lxp-sync",
        "push_optional": True,
        "splash_theme": "#2F6F5E",
        "graceful_fallback": True,
        "register_snippet": """
        if ('serviceWorker' in navigator) {
          navigator.serviceWorker.register('/static/lxp/sw.js').catch(function(){});
        }
        """,
    }


def render_install_hint() -> str:
    return (
        "Install Alora LXP for offline lessons. "
        "Unsupported browsers keep full web functionality without installation."
    )
