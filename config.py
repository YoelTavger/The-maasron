import os
from dotenv import load_dotenv

# טעינת משתני הסביבה מקובץ .env
load_dotenv()

# טוקן API לבוט
API_TOKEN = os.getenv('API_TOKEN')

# הגדרות למסד נתונים PostgreSQL
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# הגדרות לסביבת Render
IS_RENDER = os.getenv('RENDER', 'false').lower() == 'true'
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv('PORT', 10000))

# הגדרות מנהל הבוט
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')  # מזהה המנהל לקבלת דוחות ומעקב