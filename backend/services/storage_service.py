import os
import uuid
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError


DEFAULT_EXPIRATION = int(os.environ.get("S3_PRESIGNED_EXPIRES", "900"))


def _bucket_name() -> str:
    bucket = (
        os.environ.get("AWS_S3_BUCKET")
        or os.environ.get("S3_BUCKET")
        or os.environ.get("S3_BUCKET_NAME")
    )
    if not bucket:
        raise RuntimeError("S3 bucket not configured (AWS_S3_BUCKET or S3_BUCKET).")
    return bucket


def _region() -> Optional[str]:
    return os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")


def get_s3_client():
    return boto3.client("s3", region_name=_region())


def build_object_url(key: str) -> str:
    bucket = _bucket_name()
    region = _region()
    if region and region != "us-east-1":
        return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    return f"https://{bucket}.s3.amazonaws.com/{key}"


def generate_avatar_key(resource: str, resource_id: str, file_name: Optional[str] = None) -> str:
    safe_name = (file_name or "").strip()
    ext = ""
    if "." in safe_name:
        ext = safe_name[safe_name.rfind(".") :]
    return f"avatars/{resource}/{resource_id}/{uuid.uuid4().hex}{ext}"


def generate_presigned_upload(
    *,
    key: str,
    content_type: Optional[str] = None,
    expires_in: Optional[int] = None,
) -> Dict[str, Any]:
    bucket = _bucket_name()
    client = get_s3_client()
    params: Dict[str, Any] = {"Bucket": bucket, "Key": key}
    if content_type:
        params["ContentType"] = content_type

    expiry = expires_in or DEFAULT_EXPIRATION
    try:
        url = client.generate_presigned_url(
            "put_object",
            Params=params,
            ExpiresIn=expiry,
        )
    except (BotoCoreError, ClientError, NoCredentialsError) as exc:
        raise RuntimeError(f"Failed to generate presigned URL: {exc}") from exc

    return {
        "upload_url": url,
        "expires_in": expiry,
        "bucket": bucket,
        "key": key,
        "public_url": build_object_url(key),
    }


