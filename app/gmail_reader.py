from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import email
import psycopg2
from psycopg2.extras import execute_values
from config import settings
import os

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

class GmailReader:
    def __init__(self):
        self.creds = None

    def authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        # Load existing credentials if available
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If no valid credentials, run authentication flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save credentials for future use
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        self.creds = creds

    def fetch_emails(self, max_results=20):
        """Fetch emails from Gmail inbox."""
        if not self.creds:
            self.authenticate()

        service = build("gmail", "v1", credentials=self.creds)
        results = service.users().messages().list(
            userId="me", maxResults=max_results
        ).execute()

        messages = results.get("messages", [])
        parsed = []

        for msg in messages:
            msg_data = service.users().messages().get(
                userId="me", id=msg["id"], format="raw"
            ).execute()

            raw = base64.urlsafe_b64decode(msg_data["raw"])
            email_msg = email.message_from_bytes(raw)

            parsed.append({
                "subject": email_msg.get("Subject"),
                "sender": email_msg.get("From"),
                "date": email_msg.get("Date"),
                "body": self.extract_body(email_msg)
            })

        return parsed

    def extract_body(self, msg):
        """Extract plain text body from email."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode(errors="ignore")
        else:
            return msg.get_payload(decode=True).decode(errors="ignore")
        return ""

    def load_to_postgres(self, table_name="emails", max_results=20):
        """Insert Gmail emails into PostgreSQL."""
        emails = self.fetch_emails(max_results=max_results)

        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor()

        query = f"""
        INSERT INTO {table_name} (subject, sender, date, body)
        VALUES %s
        """

        data = [
            (e["subject"], e["sender"], e["date"], e["body"])
            for e in emails
        ]

        try:
            execute_values(cur, query, data)
            conn.commit()
            return len(data)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()