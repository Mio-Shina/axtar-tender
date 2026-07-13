import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

user = os.environ.get("MYSQLUSER")
password = os.environ.get("MYSQLPASSWORD")
host = os.environ.get("MYSQLHOST")
port = int(os.environ.get("MYSQLPORT", 3306))
db_name = os.environ.get("MYSQLDATABASE")
