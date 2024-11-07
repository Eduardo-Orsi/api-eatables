import requests
import msal

class EmailSender:
    def __init__(self, client_id, client_secret, tenant_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.scope = ["https://graph.microsoft.com/.default"]
        self.token = self.get_access_token()

    def get_access_token(self):
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id, authority=authority, client_credential=self.client_secret
        )
        result = app.acquire_token_silent(self.scope, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=self.scope)
        if "access_token" in result:
            return result['access_token']
        else:
            raise Exception("Could not obtain access token: " + str(result.get("error_description")))

    def send_email(self, to_emails: list[str], subject: str, content: str, content_type='Text'):
        url = 'https://graph.microsoft.com/v1.0/users/sac@lovechocolate.com.br/sendMail'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        email_message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": content_type,
                    "content": content
                },
                "toRecipients": [
                    {"emailAddress": {"address": email}} for email in to_emails
                ],
            }
        }
        response = requests.post(url, headers=headers, json=email_message, timeout=10)
        if response.status_code == 202:
            print('Email sent successfully.')
        else:
            print('Failed to send email.')
            print('Status Code:', response.status_code)
            print('Response:', response.text)
