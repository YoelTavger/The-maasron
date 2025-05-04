def reset_database():
    """
    מאפס את מסד הנתונים - מוחק את כל הטבלאות ויוצר אותן מחדש
    
    זהירות: פעולה זו תמחק את כל הנתונים!
    יש להשתמש בה רק בעת הצורך לאיפוס מוחלט
    """
    from database.connection import execute_query, get_connection
    from database.schema import create_tables
    
    try:
        print("מתחיל איפוס מסד נתונים...")
        
        # פקודות למחיקת כל הטבלאות בסדר נכון (בגלל מפתחות זרים)
        drop_tables_queries = [
            "DROP TABLE IF EXISTS donations",
            "DROP TABLE IF EXISTS maasrot",
            "DROP TABLE IF EXISTS households",
            "DROP TABLE IF EXISTS users"
        ]
        
        # ביצוע המחיקות
        for query in drop_tables_queries:
            execute_query(query)
            print(f"טבלה נמחקה: {query}")
        
        # יצירת הטבלאות מחדש
        connection = get_connection()
        create_tables(connection)
        connection.close()
        
        print("מסד הנתונים אופס בהצלחה!")
        return True
    except Exception as e:
        print(f"שגיאה באיפוס מסד הנתונים: {e}")
        return False

# כדי להשתמש בפונקציה, פשוט קרא לה מתוך main:
# אם תרצה להפעיל אותה רק בתנאים מסוימים, תוכל להוסיף תנאי כגון:
# if os.environ.get('RESET_DB', 'false').lower() == 'true':
#     reset_database()