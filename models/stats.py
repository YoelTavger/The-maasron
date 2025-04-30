import csv
import os
from config import MAASROT_FILE, DONATIONS_FILE, USERS_FILE
from models.users import get_user_household

def get_stats(user_id, household=False):
    """
    מחזיר סטטיסטיקות של משתמש מסוים או משק בית
    
    Args:
        user_id: מזהה המשתמש
        household: האם להציג סטטיסטיקות של משק בית
        
    Returns:
        dict: סטטיסטיקות המשתמש או משק הבית
    """
    total_maaser = 0
    total_donated = 0
    maasrot = []
    donations = []
    
    try:
        # אם נבקש סטטיסטיקות של משק בית, נקבל את מזהה משק הבית
        household_id = None
        user_ids = [str(user_id)]
        
        if household:
            household_id = get_user_household(user_id)
            if household_id:
                # איסוף כל המשתמשים במשק הבית
                user_ids = []
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)  # דילוג על הכותרת
                    for row in reader:
                        if row and len(row) > 5 and row[5] == household_id:
                            user_ids.append(row[0])
        
        # קריאת מעשרות
        if os.path.exists(MAASROT_FILE):
            with open(MAASROT_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # דילוג על הכותרת
                for row in reader:
                    if row and row[0] in user_ids:
                        try:
                            amount = float(row[1])
                            total_maaser += amount
                            maasrot.append({
                                'amount': amount,
                                'source': row[2],
                                'date': row[3],
                                'deadline': row[4] if len(row) > 4 else None
                            })
                        except (ValueError, IndexError):
                            continue
        
        # קריאת תרומות
        if os.path.exists(DONATIONS_FILE):
            with open(DONATIONS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # דילוג על הכותרת
                for row in reader:
                    if row and row[0] in user_ids:
                        try:
                            amount = float(row[1])
                            total_donated += amount
                            donations.append({
                                'amount': amount,
                                'purpose': row[2],
                                'date': row[3],
                                'method': row[4] if len(row) > 4 else "לא צוין"
                            })
                        except (ValueError, IndexError):
                            continue
        
        # חישוב יתרה
        balance = total_maaser - total_donated
        
        return {
            'total_maaser': total_maaser,
            'total_donated': total_donated,
            'balance': balance,
            'maasrot': maasrot,
            'donations': donations,
            'household': household_id is not None
        }
    except Exception as e:
        print(f"שגיאה בקבלת סטטיסטיקות: {e}")
        return None
