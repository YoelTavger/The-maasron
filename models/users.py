import csv
import os
from config import USERS_FILE
from utils.helpers import get_current_datetime_str

def register_user(user, household_id=None):
    """
    רושם משתמש חדש אם אינו קיים במערכת
    או מעדכן את משק הבית שלו אם נדרש
    
    Args:
        user: אובייקט המשתמש מטלגרם
        household_id: מזהה משק הבית (אופציונלי)
        
    Returns:
        bool: האם נוצר משתמש חדש
    """
    try:
        # בדיקה אם המשתמש כבר קיים
        existing_users = []
        user_exists = False
        
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)  # דילוג על הכותרת
                
                # קריאת כל השורות לזיכרון
                rows = list(reader)
                for row in rows:
                    if row and str(row[0]) == str(user.id):
                        user_exists = True
                        # אם קיבלנו מספר משק בית חדש, נעדכן אותו
                        if household_id is not None and len(row) > 5:
                            row[5] = household_id
        
        # רישום או עדכון המשתמש
        if not user_exists:
            with open(USERS_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                username = user.username if user.username else ''
                first_name = user.first_name if user.first_name else ''
                last_name = user.last_name if user.last_name else ''
                join_date = get_current_datetime_str()
                writer.writerow([user.id, username, first_name, last_name, join_date, household_id])
            return True
        elif household_id is not None and user_exists:
            # עדכון מספר משק הבית במקרה הצורך
            with open(USERS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
        return False
    except Exception as e:
        print(f"שגיאה ברישום משתמש: {e}")
        return False

def get_user_household(user_id):
    """
    מחזיר את מזהה משק הבית של המשתמש
    
    Args:
        user_id: מזהה המשתמש
        
    Returns:
        str או None: מזהה משק הבית אם נמצא
    """
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # דילוג על הכותרת
                for row in reader:
                    if row and str(row[0]) == str(user_id) and len(row) > 5 and row[5]:
                        return row[5]
        return None
    except Exception as e:
        print(f"שגיאה בקבלת משק בית: {e}")
        return None

def remove_user_from_household(user_id):
    """
    מסיר את המשתמש ממשק הבית שלו
    
    Args:
        user_id: מזהה המשתמש
        
    Returns:
        bool: האם הפעולה הצליחה
    """
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)
            
            updated = False
            for row in rows:
                if row and str(row[0]) == str(user_id) and len(row) > 5 and row[5]:
                    row[5] = ""  # ניקוי שדה משק הבית
                    updated = True
            
            if updated:
                with open(USERS_FILE, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)
                return True
        return False
    except Exception as e:
        print(f"שגיאה בהסרת משתמש ממשק בית: {e}")
        return False
