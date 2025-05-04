import psycopg2
from psycopg2.extras import DictCursor
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from database.schema import create_tables

def get_connection():
    """
    יוצר ומחזיר חיבור למסד הנתונים
    
    Returns:
        connection: חיבור למסד הנתונים
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"שגיאה בהתחברות למסד הנתונים: {e}")
        raise

def init_database():
    """
    מאתחל את מסד הנתונים - יוצר טבלאות אם הן לא קיימות
    
    Returns:
        bool: האם האתחול הצליח
    """
    try:
        conn = get_connection()
        create_tables(conn)
        conn.close()
        print("מסד הנתונים אותחל בהצלחה")
        return True
    except Exception as e:
        print(f"שגיאה באתחול מסד הנתונים: {e}")
        return False

def execute_query(query, params=None, fetch=False, fetch_one=False):
    """
    מבצע שאילתה על מסד הנתונים
    
    Args:
        query: מחרוזת השאילתה
        params: פרמטרים לשאילתה (אופציונלי)
        fetch: האם להחזיר תוצאות (ברירת מחדל: False)
        fetch_one: האם להחזיר שורה אחת בלבד (ברירת מחדל: False)
        
    Returns:
        תוצאות השאילתה, או None אם fetch=False
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(query, params or ())
        
        result = None
        if fetch:
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        
        conn.commit()
        return result
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"שגיאה בביצוע שאילתה: {e}")
        raise
    finally:
        if conn:
            conn.close()

def test_connection():
    """
    בודק אם החיבור למסד הנתונים תקין
    
    Returns:
        bool: האם החיבור הצליח
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        return True
    except Exception as e:
        print(f"שגיאה בבדיקת חיבור למסד הנתונים: {e}")
        return False