from twilio.rest import Client


class TwilioClient:
    client = None

    def set_credentials(self, sid: str, key: str):
        self.client = Client(sid, key)

    def get_client(self):
        return self.client


twilio = TwilioClient()
