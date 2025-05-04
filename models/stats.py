from database.connection import execute_query

def get_stats(user_id, household=False):
    """
    מחזיר סטטיסטיקות של משתמש מסוים או משק בית
    
    Args:
        user_id: מזהה המשתמש
        household: האם להציג סטטיסטיקות של משק בית
        
    Returns:
        dict: סטטיסטיקות המשתמש או משק הבית
    """
    try:
        # וודא שמזהה המשתמש הוא מחרוזת
        user_id_str = str(user_id)
        
        # קבלת מזהה משק הבית של המשתמש אם נדרש
        household_id = None
        if household:
            query = "SELECT household_id FROM users WHERE user_id = %s"
            result = execute_query(query, (user_id_str,), fetch=True, fetch_one=True)
            if result and result['household_id']:
                household_id = result['household_id']
        
        # מערכי אחסון לנתונים
        maasrot = []
        donations = []
        
        # קבלת סטטיסטיקות אישיות או של משק בית
        if household and household_id:
            # קבלת כל המשתמשים במשק הבית
            query = "SELECT user_id, first_name, last_name, username FROM users WHERE household_id = %s"
            household_members = execute_query(query, (household_id,), fetch=True)
            
            # וודא שכל המזהים הם מחרוזות
            member_ids = [str(member['user_id']) for member in household_members]
            member_map = {str(m['user_id']): get_member_display_name(m) for m in household_members}
            
            # קבלת מעשרות של כל חברי משק הבית
            query = """
                SELECT m.*, u.first_name, u.last_name, u.username
                FROM maasrot m
                JOIN users u ON m.user_id = u.user_id
                WHERE m.user_id = ANY(%s)
                ORDER BY m.maaser_date DESC
            """
            maaser_results = execute_query(query, (member_ids,), fetch=True)
            
            # קבלת תרומות של כל חברי משק הבית
            query = """
                SELECT d.*, u.first_name, u.last_name, u.username
                FROM donations d
                JOIN users u ON d.user_id = u.user_id
                WHERE d.user_id = ANY(%s)
                ORDER BY d.donation_date DESC
            """
            donation_results = execute_query(query, (member_ids,), fetch=True)
            
            # עיבוד תוצאות המעשרות
            for row in maaser_results:
                user_id_key = str(row['user_id'])  # וודא שהמפתח למילון הוא מחרוזת
                contributor_name = member_map.get(user_id_key, "משתמש לא ידוע")
                maasrot.append({
                    'id': row['id'],
                    'amount': float(row['amount']),
                    'source': row['source'],
                    'date': row['maaser_date'],
                    'deadline': row['deadline'],
                    'contributor': contributor_name  # הוספת שם התורם
                })
            
            # עיבוד תוצאות התרומות
            for row in donation_results:
                user_id_key = str(row['user_id'])  # וודא שהמפתח למילון הוא מחרוזת
                contributor_name = member_map.get(user_id_key, "משתמש לא ידוע")
                donations.append({
                    'id': row['id'],
                    'amount': float(row['amount']),
                    'purpose': row['purpose'],
                    'date': row['donation_date'],
                    'method': row['donation_method'],
                    'contributor': contributor_name  # הוספת שם התורם
                })
            
            # חישוב סיכומים
            total_maaser = sum(item['amount'] for item in maasrot)
            total_donated = sum(item['amount'] for item in donations)
            
        else:
            # קבלת מעשרות של המשתמש
            query = "SELECT * FROM maasrot WHERE user_id = %s ORDER BY maaser_date DESC"
            maaser_results = execute_query(query, (user_id_str,), fetch=True)
            
            # קבלת תרומות של המשתמש
            query = "SELECT * FROM donations WHERE user_id = %s ORDER BY donation_date DESC"
            donation_results = execute_query(query, (user_id_str,), fetch=True)
            
            # עיבוד תוצאות המעשרות
            for row in maaser_results:
                maasrot.append({
                    'id': row['id'],
                    'amount': float(row['amount']),
                    'source': row['source'],
                    'date': row['maaser_date'],
                    'deadline': row['deadline']
                })
            
            # עיבוד תוצאות התרומות
            for row in donation_results:
                donations.append({
                    'id': row['id'],
                    'amount': float(row['amount']),
                    'purpose': row['purpose'],
                    'date': row['donation_date'],
                    'method': row['donation_method']
                })
            
            # חישוב סיכומים
            total_maaser = sum(item['amount'] for item in maasrot)
            total_donated = sum(item['amount'] for item in donations)
        
        # חישוב יתרה
        balance = total_maaser - total_donated
        
        return {
            'total_maaser': total_maaser,
            'total_donated': total_donated,
            'balance': balance,
            'maasrot': maasrot,
            'donations': donations,
            'household': household and household_id is not None
        }
    except Exception as e:
        print(f"שגיאה בקבלת סטטיסטיקות: {e}")
        return None

def get_member_display_name(member):
    """
    יוצר שם תצוגה למשתמש
    
    Args:
        member: מילון עם פרטי המשתמש
        
    Returns:
        str: שם תצוגה למשתמש
    """
    if member['first_name']:
        if member['last_name']:
            return f"{member['first_name']} {member['last_name']}"
        return member['first_name']
    if member['username']:
        return f"@{member['username']}"
    return f"משתמש {member['user_id']}"