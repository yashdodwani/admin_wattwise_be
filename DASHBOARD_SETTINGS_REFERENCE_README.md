# Dashboard, Settings, and Reference APIs

This module adds analytics and configuration APIs for the WattWise Admin Portal.

## Added route files

- `routes/dashboard_routes.py`
- `routes/settings_routes.py`
- `routes/reference_routes.py`

## Added models

- `models/settings.py`
  - `BillingSettings`
  - `NotificationPreference`
- `models/reference_data.py`
  - `State`
  - `Discom`

## Added schemas

- `schemas/dashboard_schema.py`
- `schemas/settings_schema.py`
- `schemas/reference_schema.py`

## Migration

Apply the new migration after setting `DATABASE_URL` in `.env`:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

## Route smoke tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_dashboard_settings_reference.py -q
```

## Run server

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

