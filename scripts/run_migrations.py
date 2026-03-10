"""
Runs alembic commands and writes all output to alembic_result.txt
"""
import subprocess
import sys
import os

os.chdir(r"C:\Users\raksh\OneDrive\Desktop\projects\admin_wattwise_be")

out_path = "alembic_result.txt"

with open(out_path, "w", encoding="utf-8") as f:
    def run(args):
        cmd = [sys.executable, "-m", "alembic"] + args
        f.write(f"\n{'='*60}\n>>> {' '.join(args)}\n{'='*60}\n")
        f.flush()
        proc = subprocess.run(cmd, stdout=f, stderr=f, text=True)
        f.write(f"\n[exit code: {proc.returncode}]\n")
        f.flush()
        return proc.returncode

    rc = run(["current"])
    f.write(f"\ncurrent done (rc={rc})\n"); f.flush()

    rc = run(["revision", "--autogenerate", "-m", "init_all_tables"])
    f.write(f"\nrevision done (rc={rc})\n"); f.flush()

    if rc == 0:
        rc = run(["upgrade", "head"])
        f.write(f"\nupgrade done (rc={rc})\n"); f.flush()
    else:
        f.write("\nSkipping upgrade due to revision error\n"); f.flush()

    f.write("\nALL DONE\n")
