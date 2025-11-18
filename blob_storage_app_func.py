from typing import Dict, Any
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

from mysql_app_func import load_yaml

# Load secrets to get the SAS token
secrets: Dict[str, Any] = load_yaml("secrets.yaml")
params: Dict[str, Any] = load_yaml("params.yaml")


def upload_blob(
    account_url: str, container_name: str, blob_name: str, data: bytes, sas_token: str
) -> bool:
    """Upload a blob to Azure Blob Storage.

    Args:
        account_url (str): The URL of the Blob service (e.g., "https://<account_name>.blob.core.windows.net").
        container_name (str): The name of the container to upload the blob to.
        blob_name (str): The name of the blob to create or overwrite.
        data (bytes): The data to upload as a blob.
        sas_token (str): The SAS token for authentication."""
    
    try:
        
        blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)
        container_client = blob_service_client.get_container_client(container_name)

        # Create the container if it does not exist
        try:
            container_client.create_container()
        except ResourceExistsError:
            pass  # Container already exists

        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data, overwrite=True)
        print(f"Blob '{blob_name}' uploaded to container '{container_name}'.")
        return True
    except Exception as e:
        print(f"Failed to upload blob: {e}")
        return False