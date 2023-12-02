import os
import traceback
from settings import *
from pathlib import Path
from loguru import logger
from azure.storage.blob import BlobServiceClient
from tenacity import retry, stop_after_attempt, wait_exponential

class AzureBlobOp:
    def __init__(
        self,
        BLOB_KEY: str = "AZURE_STORAGE_CONNECTION_STRING"
    ):
        self.connection_string = None

        if BLOB_KEY not in os.environ:
            raise Exception(f"Environment variable {BLOB_KEY} missing!")
        self.connection_string = os.getenv(BLOB_KEY)
        # * get connect informations from connect string
        self.connection_info = self._build_connect_infos(self.connection_string)

    def _build_connect_infos(
        self,
        connection_string: str
    ) -> dict:
        '''get connection info from connection string'''
        connection_info = {}
        tmps = connection_string.split(";")
        for tmp in tmps:
            key, value = tmp.split("=", 1)
            connection_info[key] = value
        return connection_info

    @retry(stop=stop_after_attempt(RETRIES), wait=wait_exponential(multiplier=BACKOFF, min=DELAY), reraise=True, retry_error_callback=logger.error)
    def upload_blob(
        self,
        file: Path | bytes,
        blob_name: str,
        container: str = os.getenv("AZURE_BLOB_CONTAINER", "test"),
        overwrite: bool = True
    ) -> tuple:
        '''upload blob'''
        res_status = 0
        res_message = "Success"
        res_url = None

        c = self.connection_info
        with BlobServiceClient.from_connection_string(self.connection_string) as blob_service_client:
            try:
                blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
                # If blob already exists and no overwrite is chosen, directly return
                if blob_client.exists():
                    if not overwrite:
                        res_url = f"{c['DefaultEndpointsProtocol']}://{c['AccountName']}.blob.{c['EndpointSuffix']}/{container}/{blob_name}"
                        return res_status, res_message, res_url
                    else:
                        # Remove the existing blob prior to uploading again
                        blob_client.delete_blob()
                if isinstance(file, Path):
                    with open(file, "rb") as data:
                        blob_client.upload_blob(data)
                elif isinstance(file, bytes):
                    blob_client.upload_blob(file)
            except:
                logger.error(traceback.format_exc())
                raise

        # Add 'url' field to res which is the URL to the blob
        res_url = f"{c['DefaultEndpointsProtocol']}://{c['AccountName']}.blob.{c['EndpointSuffix']}/{container}/{blob_name}"
        return res_status, res_message, res_url