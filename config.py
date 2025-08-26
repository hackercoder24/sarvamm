import os

# Get from environment variables (Heroku Config Vars)
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# Additional admins (comma separated in env)
ADMINS = [OWNER_ID]
admin_str = os.environ.get("ADMINS", "")
if admin_str:
    ADMINS.extend([int(x) for x in admin_str.split(",") if x.isdigit()])

# Heroku specific paths
DOWNLOAD_PATH = "/tmp/downloads"
TEMP_PATH = "/tmp/temp"

# Create directories
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
os.makedirs(TEMP_PATH, exist_ok=True)

# Heroku app name (for restart functionality)
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", "")
HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", "")
