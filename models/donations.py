import csv
import os
from config import DONATIONS_FILE
from utils.helpers import get_current_datetime_str

def add_donation(user_id, amount, purpose, method):
    """
    מוסיף תרומה שבוצעה
    
    Args:
        user_id: מזהה המשתמש
        amount: סכום התרומה
        purpose: מטרת התרומה
        method: אמצעי התשלום
        
    Returns:
        bool: האם הפעולה הצליחה
    """
    try:
        with open(DONATIONS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            donation_date = get_current_datetime_str()
            writer.writerow([user_id, amount, purpose, donation_date, method])
        return True
    except Exception as e:
        print(f"שגיאה בהוספת תרומה: {e}")
        return False

def get_user_donations(user_id):
    """
    מחזיר את רשימת התרומות של משתמש מסוים
    
    Args:
        user_id: מזהה המשתמש
        
    Returns:
        list: רשימת התרומות
    """
    donations = []
    try:
        if os.path.exists(DONATIONS_FILE):
            with open(DONATIONS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # דילוג על הכותרת
                for row in reader:
                    if row and row[0] == str(user_id):
                        try:
                            amount = float(row[1])
                            donations.append({
                                'amount': amount,
                                'purpose': row[2],
                                'date': row[3],
                                'method': row[4] if len(row) > 4 else "לא צוין"
                            })
                        except (ValueError, IndexError):
                            continue
        return donations
    except Exception as e:
        print(f"שגיאה בקבלת התרומות: {e}")
        return []
