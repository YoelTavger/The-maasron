from database.connection import execute_query
from datetime import datetime

def add_donation(user_id, amount, purpose, method):
    """
    מוסיף תרומה חדשה
    
    Args:
        user_id: מזהה המשתמש
        amount: סכום התרומה
        purpose: מטרת התרומה
        method: אמצעי התשלום
        
    Returns:
        bool: האם הפעולה הצליחה
    """
    try:
        # וודא שמזהה המשתמש הוא מחרוזת
        user_id_str = str(user_id)
        
        print(f"מנסה להוסיף תרומה: סכום={amount}, מטרה={purpose}, משתמש={user_id_str}")
        
        query = "INSERT INTO donations (user_id, amount, purpose, donation_date, donation_method) VALUES (%s, %s, %s, %s, %s) RETURNING id"
        donation_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        params = (user_id_str, float(amount), purpose, donation_date, method)
        
        result = execute_query(query, params, fetch=True, fetch_one=True)
        
        if result and 'id' in result:
            print(f"תרומה נוספה בהצלחה עם מזהה {result['id']}")
            return True
        else:
            print("לא הוחזר מזהה אחרי הוספת התרומה")
            return False
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
    try:
        # וודא שמזהה המשתמש הוא מחרוזת
        user_id_str = str(user_id)
        
        query = "SELECT * FROM donations WHERE user_id = %s ORDER BY donation_date DESC"
        donation_results = execute_query(query, (user_id_str,), fetch=True)
        
        donations = []
        for row in donation_results:
            donations.append({
                'id': row['id'],
                'amount': float(row['amount']),
                'purpose': row['purpose'],
                'date': row['donation_date'],
                'method': row['donation_method']
            })
        
        return donations
    except Exception as e:
        print(f"שגיאה בקבלת התרומות: {e}")
        return []