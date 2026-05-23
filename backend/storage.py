import json
import logging
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError

from backend.config import S3_BUCKET, S3_PREFIX

logger = logging.getLogger(__name__)

_s3_client = None


def _s3():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3")
    return _s3_client


def _use_s3() -> bool:
    return bool(S3_BUCKET)


def _to_key(rel_path: str) -> str:
    return f"{S3_PREFIX}/{rel_path}" if S3_PREFIX else rel_path


def exists(rel_path: str) -> bool:
    if _use_s3():
        try:
            _s3().head_object(Bucket=S3_BUCKET, Key=_to_key(rel_path))
            return True
        except ClientError:
            return False
    return Path(rel_path).exists()


def list_keys(rel_dir: str) -> list[str]:
    """Return relative paths of all .json objects/files in rel_dir."""
    if _use_s3():
        prefix = _to_key(rel_dir.rstrip("/") + "/")
        paginator = _s3().get_paginator("list_objects_v2")
        keys = []
        for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith(".json"):
                    rel = key[len(S3_PREFIX) + 1:] if S3_PREFIX else key
                    keys.append(rel)
        return keys
    return [str(p) for p in Path(rel_dir).glob("*.json")]


def read_json(rel_path: str) -> Any:
    if _use_s3():
        obj = _s3().get_object(Bucket=S3_BUCKET, Key=_to_key(rel_path))
        return json.loads(obj["Body"].read().decode("utf-8"))
    return json.loads(Path(rel_path).read_text(encoding="utf-8"))


def write_json(rel_path: str, data: Any) -> None:
    if _use_s3():
        _s3().put_object(
            Bucket=S3_BUCKET,
            Key=_to_key(rel_path),
            Body=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
            ContentType="application/json",
        )
    else:
        path = Path(rel_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
