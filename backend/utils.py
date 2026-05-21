import json
import logging
import os

import boto3
import psycopg2
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_cache: SecretCache | None = None


def _get_cache() -> SecretCache:
    global _cache
    if _cache is None:
        client = boto3.session.Session().client(
            service_name="secretsmanager",
            region_name=os.getenv("AWS_REGION", "eu-west-2"),
        )
        _cache = SecretCache(config=SecretCacheConfig(), client=client)
    return _cache


def get_db_connection(secret_name: str) -> psycopg2.extensions.connection:
    secret = json.loads(_get_cache().get_secret_string(secret_name))
    return psycopg2.connect(
        host=secret["host"],
        port=secret["port"],
        dbname=secret.get("dbname", "postgres"),
        user=secret["username"],
        password=secret["password"],
    )
