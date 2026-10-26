#!/usr/bin/env python3
"""Upload local files to Tencent COS using per-file temporary credentials.

Input: JSON file with a list of jobs:
[{"local_path": ..., "bucket": ..., "region": ..., "key": ...,
  "secret_id": ..., "secret_key": ..., "token": ...}, ...]

Output: JSON lines to stdout: {"key": ..., "ok": true/false, "error": ...}
"""
import json
import sys
import traceback

from qcloud_cos import CosConfig, CosS3Client


def main():
    jobs_file = sys.argv[1]
    with open(jobs_file, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    results = []
    for job in jobs:
        key = job["key"]
        try:
            config = CosConfig(
                Region=job["region"],
                SecretId=job["secret_id"],
                SecretKey=job["secret_key"],
                Token=job["token"],
            )
            client = CosS3Client(config)
            with open(job["local_path"], "rb") as fp:
                resp = client.put_object(
                    Bucket=job["bucket"],
                    Body=fp,
                    Key=key,
                    ContentType=job.get("content_type", "application/octet-stream"),
                    EnableMD5=False,
                )
            if resp and "ETag" in resp:
                results.append({"key": key, "ok": True})
            else:
                results.append({"key": key, "ok": False, "error": f"unexpected resp: {resp}"})
        except Exception as e:
            results.append({"key": key, "ok": False, "error": f"{type(e).__name__}: {e}"})
            traceback.print_exc(file=sys.stderr)

    for r in results:
        print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
