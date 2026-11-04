"""Run Django migrations against the configured production database during Vercel builds.

The RUN_DJANGO_MIGRATIONS flag is configured for Production only in Vercel.
This prevents Preview deployments from modifying the live Aiven database.
"""
import os
import subprocess
import sys


if os.environ.get("RUN_DJANGO_MIGRATIONS", "").strip() != "1":
    print("Skipping database migrations: RUN_DJANGO_MIGRATIONS is not enabled for this environment.")
    raise SystemExit(0)

commands = [
    [sys.executable, "manage.py", "migrate", "--noinput"],
    # Create fictional sample companies and drives for the first live demo.
    # The command is idempotent and does not create demo login accounts.
    [sys.executable, "manage.py", "seed_demo"],
]

for command in commands:
    print("Running:", " ".join(command[1:]))
    subprocess.run(command, check=True)
