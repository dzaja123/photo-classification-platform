"""MinIO storage integration for photo uploads."""

import logging
from typing import BinaryIO
from datetime import timedelta

from minio import Minio
from minio.error import S3Error

from app.config import get_settings

logger = logging.getLogger(__name__)


settings = get_settings()


class StorageClient:
    """
    MinIO storage client for photo management.

    Provides methods for uploading, downloading, and deleting photos.
    """

    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info("Created MinIO bucket: %s", self.bucket_name)
        except S3Error as e:
            logger.error("Error creating bucket: %s", e)
            raise

    def upload_file(
        self, file_data: BinaryIO, object_name: str, content_type: str, file_size: int
    ) -> str:
        """
        Upload file to MinIO.

        Args:
            file_data: File binary data
            object_name: Object name in bucket (path)
            content_type: MIME type
            file_size: File size in bytes

        Returns:
            Object name (path) in bucket

        Raises:
            S3Error: If upload fails

        Example:
            >>> storage = StorageClient()
            >>> with open("photo.jpg", "rb") as f:
            ...     path = storage.upload_file(
            ...         f, "photos/user123/photo.jpg", "image/jpeg", 1024
            ...     )
        """
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type,
            )
            return object_name
        except S3Error as e:
            logger.error("Error uploading file: %s", e)
            raise

    def download_file(self, object_name: str) -> bytes:
        """
        Download file from MinIO.

        Args:
            object_name: Object name in bucket

        Returns:
            File binary data

        Raises:
            S3Error: If download fails

        Example:
            >>> storage = StorageClient()
            >>> data = storage.download_file("photos/user123/photo.jpg")
        """
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name, object_name=object_name
            )
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error("Error downloading file: %s", e)
            raise

    def delete_file(self, object_name: str) -> bool:
        """
        Delete file from MinIO.

        Args:
            object_name: Object name in bucket

        Returns:
            True if successful

        Raises:
            S3Error: If deletion fails

        Example:
            >>> storage = StorageClient()
            >>> storage.delete_file("photos/user123/photo.jpg")
            True
        """
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name, object_name=object_name
            )
            return True
        except S3Error as e:
            logger.error("Error deleting file: %s", e)
            raise

    def get_presigned_url(
        self, object_name: str, expires: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Get presigned URL for file access.

        Args:
            object_name: Object name in bucket
            expires: URL expiration time

        Returns:
            Presigned URL

        Example:
            >>> storage = StorageClient()
            >>> url = storage.get_presigned_url("photos/user123/photo.jpg")
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name, object_name=object_name, expires=expires
            )
            return url
        except S3Error as e:
            logger.error("Error generating presigned URL: %s", e)
            raise

    def file_exists(self, object_name: str) -> bool:
        """
        Check if file exists in MinIO.

        Args:
            object_name: Object name in bucket

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.stat_object(
                bucket_name=self.bucket_name, object_name=object_name
            )
            return True
        except S3Error:
            return False


_storage_instance: StorageClient = None


def get_storage_client() -> StorageClient:
    """
    Get singleton storage client instance.

    Returns:
        StorageClient instance
    """
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageClient()
    return _storage_instance
