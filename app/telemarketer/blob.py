from twilio.rest import Client
from azure.storage.blob import BlockBlobService


class BlobClient:
    client = None

    def create_block_blob_service(self, account_name: str, account_key: str):
        self.client = BlockBlobService(account_name, account_key)

    def get_client(self):
        return self.client

    def get_file_name(self):
        return "history.log"

    def get_container_name(self):
        return "telemarketerlogs"


blob = BlobClient()
