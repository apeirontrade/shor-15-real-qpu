"""Submit any experiment's circuit to IQM Garnet (Amazon Braket, eu-north-1) and save the raw counts.

Usage: .venv/bin/python qpu.py ecdlp|grover [shots]
Cost (AWS price page, checked 2026-10-30): $0.30 per task + $0.00145 per shot.
"""
import json
import re
import sys
import time

import boto3
from braket.aws import AwsDevice, AwsSession

GARNET = "arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet"

name = sys.argv[1]
shots = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
if name == "ecdlp":
    from ecdlp import build
    circ = build(4, 3)[0]
elif name == "grover":
    from grover import build
    circ = build()
else:
    raise SystemExit(f"unknown experiment {name}")
print(f"{name}: estimated cost ${0.30 + 0.00145 * shots:.2f}")

device = AwsDevice(GARNET, aws_session=AwsSession(boto3.Session(region_name="eu-north-1")))
task = device.run(circ, shots=shots)
public_id = re.sub(r":\d{12}:", ":<account>:", task.id)  # keep the AWS account number out of saved files
print("task:", public_id)
while task.state() not in ("COMPLETED", "FAILED", "CANCELLED"):
    time.sleep(20)
print("state:", task.state())
res = task.result()
json.dump({"device": "IQM Garnet (Amazon Braket)", "experiment": name, "task": public_id, "shots": shots,
           "raw_counts": dict(res.measurement_counts),
           "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
          open(f"results/{name}_qpu.json", "w"), indent=1)
print("saved", f"results/{name}_qpu.json")
