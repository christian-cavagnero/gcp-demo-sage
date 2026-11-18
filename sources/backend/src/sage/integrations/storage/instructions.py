"""Read runtime instructions from Google Cloud Storage."""

import logging
from functools import lru_cache

from google.cloud import storage
from google.cloud.exceptions import NotFound

from sage.config import get_app_config

log = logging.getLogger(__name__)


@lru_cache
def _get_storage_client() -> storage.Client:
    config = get_app_config()
    return storage.Client(project=config.project_id)


def load_instructions() -> str:
    """Fetch istruzioni.md from the configured GCS bucket on every request."""
    config = get_app_config()
    if not config.instructions_bucket:
        return ""

    try:
        client = _get_storage_client()
        bucket = client.bucket(config.instructions_bucket)
        blob = bucket.blob(config.instructions_blob)
        return blob.download_as_text(encoding="utf-8").strip()
    except NotFound:
        log.warning(
            "File %s non trovato nel bucket %s",
            config.instructions_blob,
            config.instructions_bucket,
        )
        return ""
    except Exception:
        log.exception(
            "Errore durante la lettura di %s dal bucket %s",
            config.instructions_blob,
            config.instructions_bucket,
        )
        return ""
