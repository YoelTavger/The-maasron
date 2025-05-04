import time
from database.connection import execute_query
from datetime import datetime

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
        # וודא שמזהה הבעלים הוא מחרוזת
        owner_id_str = str(owner_id)
        
        print(f"מנסה ליצור משק בית חדש: שם={name}, בעלים={owner_id_str}")
        
        household_id = str(int(time.time()))  # מזהה ייחודי מבוסס זמן
        creation_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        query = "INSERT INTO households (household_id, name, creation_date, owner_id) VALUES (%s, %s, %s, %s) RETURNING household_id"
        params = (household_id, name, creation_date, owner_id_str)
        
        result = execute_query(query, params, fetch=True, fetch_one=True)
        
        if result and 'household_id' in result:
            print(f"משק בית נוצר בהצלחה עם מזהה {result['household_id']}")
            return result['household_id']
        else:
            print("לא הוחזר מזהה אחרי יצירת משק הבית")
            return None
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
        query = "SELECT * FROM households WHERE household_id = %s"
        result = execute_query(query, (household_id,), fetch=True, fetch_one=True)
        
        if result:
            return {
                'id': result['household_id'],
                'name': result['name'],
                'creation_date': result['creation_date'],
                'owner_id': result['owner_id']
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
        query = "SELECT user_id, username, first_name, last_name, join_date FROM users WHERE household_id = %s"
        results = execute_query(query, (household_id,), fetch=True)
        
        for row in results:
            members.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'join_date': row['join_date']
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
    try:
        # וודא שמזהה המשתמש הוא מחרוזת
        user_id_str = str(user_id)
        
        query = "SELECT owner_id FROM households WHERE household_id = %s"
        result = execute_query(query, (household_id,), fetch=True, fetch_one=True)
        
        return result and str(result['owner_id']) == user_id_str
    except Exception as e:
        print(f"שגיאה בבדיקת בעלות משק בית: {e}")
        return False