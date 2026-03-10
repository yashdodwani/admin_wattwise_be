"""
Helper script to run alembic commands and print output.
Run: python scripts/run_alembic.py <command> [args...]
"""
import subprocess
import sys
import os

os.chdir(r"C:\Users\raksh\OneDrive\Desktop\projects\admin_wattwise_be")

cmd = [sys.executable, "-m", "alembic"] + (sys.argv[1:] if len(sys.argv) > 1 else ["current"])
print(f"Running: {' '.join(cmd)}")

result = subprocess.run(cmd, text=True)
print(f"\nReturn code: {result.returncode}")

