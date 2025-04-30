import csv
import os
from config import MAASROT_FILE
from utils.helpers import get_current_datetime_str

def add_maaser(user_id, amount, source, deadline=None):
    """
    מוסיף 
    
    Args:
        user_id: מזהה המשתמש
        amount: סכום המעשר
        source: מקור ההכנסה
        deadline: תאריך יעד לתרומה (אופציונלי)
        
    Returns:
        bool: האם הפעולה הצליחה
    """
    try:
        with open(MAASROT_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            maaser_date = get_current_datetime_str()
            writer.writerow([user_id, amount, source, maaser_date, deadline])
        return True
    except Exception as e:
        print(f"שגיאה בהוספת מעשר: {e}")
        return False

def get_user_maasrot(user_id):
    """
    מחזיר את רשימת המעשרות של משתמש מסוים
    
    Args:
        user_id: מזהה המשתמש
        
    Returns:
        list: רשימת המעשרות
    """
    maasrot = []
    try:
        if os.path.exists(MAASROT_FILE):
            with open(MAASROT_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # דילוג על הכותרת
                for row in reader:
                    if row and row[0] == str(user_id):
                        try:
                            amount = float(row[1])
                            maasrot.append({
                                'amount': amount,
                                'source': row[2],
                                'date': row[3],
                                'deadline': row[4] if len(row) > 4 else None
                            })
                        except (ValueError, IndexError):
                            continue
        return maasrot
    except Exception as e:
        print(f"שגיאה בקבלת המעשרות: {e}")
        return []
