from database.connection import execute_query

def test_database_content():
    """בדיקת תוכן מסד הנתונים"""
    try:
        # בדיקת קיום טבלאות
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        tables = execute_query(tables_query, fetch=True)
        print(f"טבלאות קיימות: {[t['table_name'] for t in tables]}")
        
        # בדיקת מספר רשומות בכל טבלה
        for table in ['users', 'maasrot', 'donations', 'households']:
            try:
                count_query = f"SELECT COUNT(*) as count FROM {table}"
                count_result = execute_query(count_query, fetch=True, fetch_one=True)
                print(f"טבלת {table}: {count_result['count']} רשומות")
            except Exception as e:
                print(f"שגיאה בבדיקת טבלה {table}: {e}")
        
        # בדיקת תוכן טבלת משתמשים
        users_query = "SELECT * FROM users LIMIT 3"
        users = execute_query(users_query, fetch=True)
        print(f"דוגמת משתמשים: {users}")
        
    except Exception as e:
        print(f"שגיאה בבדיקת תוכן מסד הנתונים: {e}")

# קרא לפונקציה הזו לפני הרצת הבוט
test_database_content()