#Config for backend.
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = "iotbay-workshop4-group01"
    DATABASE = "iotbay.db"