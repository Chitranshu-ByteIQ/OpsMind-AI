# Backend Plan

Add `app/routes/tools.py` and `app/routes/dashboard.py`; `app/main.py` only mounts routers and owns system/chat endpoints. All external-client exceptions are converted to safe 502 responses by the application exception handler.
