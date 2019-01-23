# coding: UTF-8
from dotenv import load_dotenv
load_dotenv(verbose=True)

import os

access_token=os.getenv("access_token")
access_secret=os.getenv("access_secret")
user = os.getenv("user")
password = os.getenv("password")
host = os.getenv("host")
db = os.getenv("db")