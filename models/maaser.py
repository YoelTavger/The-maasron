from database.connection import execute_query
from datetime import datetime

def add_maaser(user_id, amount, source, deadline=None):
    """
    מוסיף מעשר חדש
    
    Args:
        user_id: מזהה המשתמש
        amount: סכום המעשר
        source: מקור ההכנסה
        deadline: תאריך יעד לתרומה (אופציונלי)
        
    Returns:
        bool: האם הפעולה הצליחה
    """
    try:
        user_id_str = str(user_id)
        
        print(f"מנסה להוסיף מעשר: סכום={amount}, מקור={source}, משתמש={user_id_str}")
        
        query = "INSERT INTO maasrot (user_id, amount, source, maaser_date, deadline) VALUES (%s, %s, %s, %s, %s) RETURNING id"
        maaser_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        params = (user_id_str, float(amount), source, maaser_date, deadline)
        
        result = execute_query(query, params, fetch=True, fetch_one=True)
        
        if result and 'id' in result:
            print(f"מעשר נוסף בהצלחה עם מזהה {result['id']}")
            return True
        else:
            print("לא הוחזר מזהה אחרי הוספת המעשר")
            return False
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
    try:
        # וודא שמזהה המשתמש הוא מחרוזת
        user_id_str = str(user_id)
        
        query = "SELECT * FROM maasrot WHERE user_id = %s ORDER BY maaser_date DESC"
        maaser_results = execute_query(query, (user_id_str,), fetch=True)
        
        maasrot = []
        for row in maaser_results:
            maasrot.append({
                'id': row['id'],
                'amount': float(row['amount']),
                'source': row['source'],
                'date': row['maaser_date'],
                'deadline': row['deadline']
            })
        
        return maasrot
    except Exception as e:
        print(f"שגיאה בקבלת המעשרות: {e}")
        return []