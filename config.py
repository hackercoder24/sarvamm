import os

# Get from environment variables (Heroku Config Vars)
API_ID = int(os.environ.get("API_ID", "20491966"))
API_HASH = os.environ.get("API_HASH", "aa1c8f86db7f78fe9bfdd77bb48a5b23")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8176555919:AAES9dnlXgTnCq2tc7BO8gaehGWROTMFEnA")
OWNER_ID = int(os.environ.get("OWNER_ID", "7168441486"))

# Additional admins (comma separated in env)
ADMINS = [7168441486]
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
