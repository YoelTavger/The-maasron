import telebot
import os
import time
from config import API_TOKEN, IS_RENDER, WEBHOOK_URL, PORT
from database.connection import init_database, test_connection
from database.reset_database import reset_database
from handlers.common import register_handlers
from handlers.maaser_handlers import register_maaser_handlers
from handlers.donation_handlers import register_donation_handlers
from handlers.household_handlers import register_household_handlers
from handlers.stats_handlers import register_stats_handlers

def main():
    """
    פונקציית הכניסה הראשית של הבוט
    """
    # בדיקה שקיים טוקן תקין
    if not API_TOKEN:
        raise ValueError("חסר טוקן API! וודא שקובץ .env מוגדר כראוי.")
    
    # בדיקת חיבור למסד הנתונים
    print("בודק חיבור למסד נתונים PostgreSQL...")
    if not test_connection():
        raise ValueError("לא ניתן להתחבר למסד הנתונים. בדוק את פרטי ההתחברות ב-ENV.")
    
    # מוחק מסד נתונים
    #reset_database()

    # אתחול מסד הנתונים
    print("מאתחל מסד נתונים...")
    init_database()
    
    # יצירת מופע הבוט
    bot = telebot.TeleBot(API_TOKEN)
    
    # הוספת טמפ_דאטה לבוט לשמירת נתונים בזיכרון
    bot.temp_data = {}
    
    # רישום כל הטיפולים בפקודות
    register_maaser_handlers(bot)
    register_donation_handlers(bot)
    register_household_handlers(bot)
    register_stats_handlers(bot)
    register_handlers(bot)

    
    # הפעלת הבוט
    try:
        print("הבוט מופעל! לחץ Ctrl+C כדי לעצור.")
        
        # בחירת מצב הפעלה לפי הסביבה (webhook לרנדר או polling מקומי)
        if IS_RENDER:
            # הגדרת webhook עבור Render
            print(f"מפעיל במצב webhook עבור Render")
            
            if not WEBHOOK_URL:
                print("אזהרה: WEBHOOK_URL לא מוגדר. ייתכן שהבוט לא יעבוד כראוי.")
                # השתמש בכתובת ברירת מחדל אם לא הוגדרה
                webhook_url = f"https://{os.environ.get('RENDER_SERVICE_NAME')}.onrender.com/{API_TOKEN}"
            else:
                webhook_url = WEBHOOK_URL
            
            # הסרת webhook קיים והגדרת webhook חדש
            bot.remove_webhook()
            time.sleep(1)
            bot.set_webhook(url=webhook_url)
            
            # הפעלת שרת Flask לקבלת עדכונים
            from flask import Flask, request
            app = Flask(__name__)
            
            @app.route('/' + API_TOKEN, methods=['POST'])
            def webhook():
                try:
                    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
                    bot.process_new_updates([update])
                    return ''
                except Exception as e:
                    print(f"שגיאה בטיפול בעדכון: {e}")
                    return 'error'
            
            @app.route('/')
            def index():
                return "בוט מעשרות פעיל!"
            
            # הפעלת שרת
            app.run(host='0.0.0.0', port=PORT)
        else:
            # הפעלה במצב polling (מקומי)
            print("מפעיל במצב polling")
            bot.remove_webhook()
            time.sleep(1)
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print("הבוט הופסק על ידי המשתמש.")
    except Exception as e:
        print(f"שגיאה קריטית בהפעלת הבוט: {e}")

if __name__ == "__main__":
    main()
