from fastapi import FastAPI
from config import settings
import psycopg2
from psycopg2 import sql
from gmail_reader import GmailReader

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API Python + PostgreSQL OK"}

@app.get("/config")
def get_config():
    return {
        "env": settings.APP_ENV,
        "db_url": settings.DATABASE_URL
    }

@app.get("/data")
def get_data():
    try:
        with psycopg2.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT NOW()")
                result = cur.fetchone()
                if result:
                    return {"server_time": str(result[0])}  # Format as string for JSON
                else:
                    return {"error": "No data retrieved"}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/import-gmail")
def import_gmail(max_results: int = 10):
    reader = GmailReader()
    count = reader.load_to_postgres(max_results=max_results)
    return {"imported": count}

@app.get("/read-emails")
async def read_emails():
    reader = GmailReader()
    try:
        emails = reader.fetch_emails()
        return {"emails": emails}
    except Exception as e:
        return {"error": str(e)}