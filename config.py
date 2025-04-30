import os
from dotenv import load_dotenv

# טעינת משתני הסביבה מקובץ .env
load_dotenv()

# טוקן API לבוט
API_TOKEN = os.getenv('API_TOKEN')

# נתיב לתיקיית נתונים
DATA_DIR = os.getenv('DATA_DIR', 'data')

# קבצים לשמירת נתונים
USERS_FILE = os.path.join(DATA_DIR, 'users.csv')
MAASROT_FILE = os.path.join(DATA_DIR, 'maasrot.csv')
DONATIONS_FILE = os.path.join(DATA_DIR, 'donations.csv')
HOUSEHOLDS_FILE = os.path.join(DATA_DIR, 'households.csv')
