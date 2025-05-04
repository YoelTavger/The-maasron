from database.connection import execute_query
from datetime import datetime

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
        # וודא שמזהה המשתמש הוא מחרוזת
        user_id_str = str(user.id)
        
        print(f"רישום/עדכון משתמש: id={user_id_str}, household_id={household_id}")
        
        # בדיקה אם המשתמש כבר קיים
        query = "SELECT * FROM users WHERE user_id = %s"
        existing_user = execute_query(query, (user_id_str,), fetch=True, fetch_one=True)
        
        if existing_user:
            # עדכון משק הבית אם נדרש
            if household_id is not None:
                update_query = "UPDATE users SET household_id = %s WHERE user_id = %s"
                execute_query(update_query, (household_id, user_id_str))
                print(f"עודכן משק הבית של המשתמש ל-{household_id}")
            return False
        else:
            # הוספת משתמש חדש
            username = user.username if user.username else ''
            first_name = user.first_name if user.first_name else ''
            last_name = user.last_name if user.last_name else ''
            join_date = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            insert_query = "INSERT INTO users (user_id, username, first_name, last_name, join_date, household_id) VALUES (%s, %s, %s, %s, %s, %s)"
            execute_query(insert_query, (user_id_str, username, first_name, last_name, join_date, household_id))
            print(f"נוצר משתמש חדש: {user_id_str}")
            return True
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
        # וודא שמזהה המשתמש הוא מחרוזת
        user_id_str = str(user_id)
        
        query = "SELECT household_id FROM users WHERE user_id = %s"
        result = execute_query(query, (user_id_str,), fetch=True, fetch_one=True)
        
        if result and result['household_id']:
            return result['household_id']
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
        # וודא שמזהה המשתמש הוא מחרוזת
        user_id_str = str(user_id)
        
        query = "UPDATE users SET household_id = NULL WHERE user_id = %s"
        execute_query(query, (user_id_str,))
        print(f"הוסר משתמש {user_id_str} ממשק הבית")
        return True
    except Exception as e:
        print(f"שגיאה בהסרת משתמש ממשק בית: {e}")
        return False

def ensure_user_exists(user_id, username=None, first_name=None, last_name=None):
    """
    מוודא שהמשתמש קיים במסד הנתונים
    
    Args:
        user_id: מזהה המשתמש
        username: שם המשתמש (אופציונלי)
        first_name: שם פרטי (אופציונלי)
        last_name: שם משפחה (אופציונלי)
        
    Returns:
        bool: האם המשתמש קיים או נוצר בהצלחה
    """
    try:
        # וודא שמזהה המשתמש הוא מחרוזת
        user_id_str = str(user_id)
        
        # בדיקה אם המשתמש קיים
        query = "SELECT * FROM users WHERE user_id = %s"
        existing_user = execute_query(query, (user_id_str,), fetch=True, fetch_one=True)
        
        if existing_user:
            return True
        
        # אם המשתמש לא קיים, נוסיף אותו
        query = "INSERT INTO users (user_id, username, first_name, last_name, join_date) VALUES (%s, %s, %s, %s, %s)"
        execute_query(
            query, 
            (user_id_str, username or "", first_name or "", last_name or "", datetime.now().strftime('%Y-%m-%d %H:%M'))
        )
        
        print(f"נוצר משתמש חדש עם מזהה {user_id_str}")
        return True
    except Exception as e:
        print(f"שגיאה בוידוא קיום משתמש: {e}")
        return False
