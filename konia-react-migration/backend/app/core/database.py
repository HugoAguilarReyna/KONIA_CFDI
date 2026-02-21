from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "cfdi_db")

class Database:
    client: MongoClient = None
    db = None

    def connect(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        print(f"Connected to MongoDB at {MONGO_URI}")

    def close(self):
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")

    def get_db(self):
        if self.db is None:
            self.connect()
        return self.db

db = Database()

def get_database():
    return db.get_db()
