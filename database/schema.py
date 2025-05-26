def create_tables(conn):
    """יוצר את הטבלאות במסד הנתונים אם הן לא קיימות"""
    cursor = conn.cursor()
    
    # יצירת טבלת משתמשים
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        join_date TEXT,
        household_id TEXT,
        currency TEXT DEFAULT 'ILS'
    )
    ''')
    
    # הוספת עמודת currency למשתמשים קיימים (אם לא קיימת)
    cursor.execute('''
    DO $$ 
    BEGIN 
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='users' AND column_name='currency') THEN
            ALTER TABLE users ADD COLUMN currency TEXT DEFAULT 'ILS';
        END IF;
    END $$;
    ''')
    
    # יצירת טבלת מעשרות
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maasrot (
        id SERIAL PRIMARY KEY,
        user_id TEXT,
        amount NUMERIC(15, 2),
        source TEXT,
        maaser_date TEXT,
        deadline TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    # יצירת טבלת תרומות
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS donations (
        id SERIAL PRIMARY KEY,
        user_id TEXT,
        amount NUMERIC(15, 2),
        purpose TEXT,
        donation_date TEXT,
        donation_method TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    # יצירת טבלת משקי בית
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS households (
        household_id TEXT PRIMARY KEY,
        name TEXT,
        creation_date TEXT,
        owner_id TEXT,
        FOREIGN KEY (owner_id) REFERENCES users (user_id)
    )
    ''')
    
    conn.commit()