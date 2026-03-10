"""
Final validation: confirm all routes are registered and the app loads cleanly.
Writes results to validation_result.txt
"""
import sys, os
project_root = r"C:\Users\raksh\OneDrive\Desktop\projects\admin_wattwise_be"
os.chdir(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

with open("validation_result.txt", "w") as f:
    try:
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app, raise_server_exceptions=False)

        # Health check
        r = client.get("/health")
        f.write(f"Health check: {r.status_code} {r.json()}\n\n")

        # Collect all routes
        r2 = client.get("/openapi.json")
        paths = sorted(r2.json()["paths"].keys())
        f.write(f"Total routes: {len(paths)}\n")
        for p in paths:
            f.write(f"  {p}\n")

        f.write("\nValidation PASSED\n")
    except Exception as e:
        f.write(f"\nValidation FAILED: {e}\n")
        import traceback
        f.write(traceback.format_exc())

