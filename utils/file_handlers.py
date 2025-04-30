import csv
import os
from config import USERS_FILE, MAASROT_FILE, DONATIONS_FILE, HOUSEHOLDS_FILE

def ensure_files_exist():
    """יוצר את קבצי ה-CSV אם אינם קיימים"""
    
    # וידוא קיום קובץ משתמשים
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'username', 'first_name', 'last_name', 'join_date', 'household_id'])
    
    # וידוא קיום קובץ מעשרות
    if not os.path.exists(MAASROT_FILE):
        with open(MAASROT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'amount', 'source', 'maaser_date', 'deadline'])
    
    # וידוא קיום קובץ תרומות
    if not os.path.exists(DONATIONS_FILE):
        with open(DONATIONS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'amount', 'purpose', 'donation_date', 'donation_method'])

    # וידוא קיום קובץ משקי בית
    if not os.path.exists(HOUSEHOLDS_FILE):
        with open(HOUSEHOLDS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['household_id', 'name', 'creation_date', 'owner_id'])
