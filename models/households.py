import csv
import os
import time
from config import HOUSEHOLDS_FILE, USERS_FILE
from utils.helpers import get_current_datetime_str

def create_household(name, owner_id):
    """
    יוצר משק בית חדש ומחזיר את המזהה שלו
    
    Args:
        name: שם משק הבית
        owner_id: מזהה המשתמש הבעלים
        
    Returns:
        str או None: מזהה משק הבית החדש אם הצליח
    """
    try:
        household_id = str(int(time.time()))  # מזהה ייחודי מבוסס זמן
        with open(HOUSEHOLDS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            creation_date = get_current_datetime_str()
            writer.writerow([household_id, name, creation_date, owner_id])
        return household_id
    except Exception as e:
        print(f"שגיאה ביצירת משק בית: {e}")
        return None

def get_household_info(household_id):
    """
    מחזיר פרטים על משק הבית
    
    Args:
        household_id: מזהה משק הבית
        
    Returns:
        dict או None: פרטי משק הבית
    """
    try:
        if os.path.exists(HOUSEHOLDS_FILE):
            with open(HOUSEHOLDS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # דילוג על הכותרת
                for row in reader:
                    if row and row[0] == household_id:
                        return {
                            'id': row[0],
                            'name': row[1],
                            'creation_date': row[2],
                            'owner_id': row[3] if len(row) > 3 else None
                        }
        return None
    except Exception as e:
        print(f"שגיאה בקבלת פרטי משק בית: {e}")
        return None

def get_household_members(household_id):
    """
    מחזיר רשימה של כל המשתמשים במשק בית מסוים
    
    Args:
        household_id: מזהה משק הבית
        
    Returns:
        list: רשימת המשתמשים במשק הבית
    """
    members = []
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # דילוג על הכותרת
                for row in reader:
                    if row and len(row) > 5 and row[5] == household_id:
                        members.append({
                            'user_id': row[0],
                            'username': row[1],
                            'first_name': row[2],
                            'last_name': row[3],
                            'join_date': row[4]
                        })
        return members
    except Exception as e:
        print(f"שגיאה בקבלת חברי משק בית: {e}")
        return []

def is_household_owner(user_id, household_id):
    """
    בודק אם המשתמש הוא בעל משק הבית
    
    Args:
        user_id: מזהה המשתמש
        household_id: מזהה משק הבית
        
    Returns:
        bool: האם המשתמש הוא הבעלים
    """
    household_info = get_household_info(household_id)
    return household_info and str(household_info.get('owner_id', '')) == str(user_id)
