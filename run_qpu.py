"""Run the Shor-15 circuit on IQM Garnet (Amazon Braket, eu-north-1) and save the raw result.

Usage: .venv/bin/python run_qpu.py [--light] [shots]
Cost (AWS price page, checked 2026-10-30): $0.30 per task + $0.00145 per shot.
"""
import json
import re
import sys
import time

import boto3
from braket.aws import AwsDevice, AwsSession

from shor15 import build, factors_from, marginal

GARNET = "arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet"

light = "--light" in sys.argv
args = [a for a in sys.argv[1:] if a != "--light"]
shots = int(args[0]) if args else 1000
print(f"estimated cost: ${0.30 + 0.00145 * shots:.2f}")

device = AwsDevice(GARNET, aws_session=AwsSession(boto3.Session(region_name="eu-north-1")))
task = device.run(build(light), shots=shots)
tag = "light" if light else "full"
public_id = re.sub(r":\d{12}:", ":<account>:", task.id)  # keep the AWS account number out of saved files
print("task:", public_id)
open(f"results/qpu_task_{tag}.txt", "w").write(public_id + "\n")

while task.state() not in ("COMPLETED", "FAILED", "CANCELLED"):
    time.sleep(20)
print("state:", task.state())
res = task.result()
m = marginal(res.measurement_counts)
for v, c in m.items():
    print(f"{v:03b} ({v}/8)  {c:5d}  -> r, factors = {factors_from(v)}")
json.dump({"device": "IQM Garnet (Amazon Braket)", "task": public_id, "light": light, "shots": shots,
           "raw_counts": dict(res.measurement_counts), "marginal": m,
           "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
          open(f"results/qpu_result_{tag}.json", "w"), indent=1)
