import telebot
import os
import time
from config import API_TOKEN, DATA_DIR
from utils.file_handlers import ensure_files_exist
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
    
    # יצירת תיקיית נתונים אם לא קיימת
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # וידוא קיום קבצי נתונים
    ensure_files_exist()
    
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
        
        # להסיר webhook קיים ולהפעיל long polling
        bot.remove_webhook()
        print('שלב 1')
        time.sleep(1)
        
        # הרצת הבוט - בדיקה אם רץ בסביבת Render
        if os.environ.get('RENDER', '').lower() == 'true':
            print(f"הפעלה במצב webhook בסביבת Render")
            
            # הגדרת webhook עבור Render
            PORT = int(os.environ.get('PORT', 10000))
            WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
            
            if not WEBHOOK_URL:
                print("אזהרה: WEBHOOK_URL לא מוגדר. משתמש בכתובת ברירת מחדל.")
                SERVICE_URL = os.environ.get('RENDER_EXTERNAL_URL', f"https://{os.environ.get('RENDER_SERVICE_NAME')}.onrender.com")
                WEBHOOK_URL = f"{SERVICE_URL}/{API_TOKEN}"
            
            print(f"מגדיר webhook בכתובת: {WEBHOOK_URL}")
            bot.remove_webhook()
            time.sleep(0.5)
            bot.set_webhook(url=WEBHOOK_URL)
            
            from flask import Flask, request
            app = Flask(__name__)
            
            @app.route('/' + API_TOKEN, methods=['POST'])
            def webhook():
                try:
                    print(f"התקבלה בקשת webhook!")
                    json_string = request.get_data().decode('utf-8')
                    update = telebot.types.Update.de_json(json_string)
                    bot.process_new_updates([update])
                    return ''
                except Exception as e:
                    print(f"שגיאה בטיפול ב-webhook: {e}")
                    return 'error'
            
            @app.route('/')
            def index():
                return "בוט פעיל!"
            
            print(f"מפעיל שרת Flask על פורט {PORT}")
            app.run(host='0.0.0.0', port=PORT)
        else:
            print("הפעלה במצב polling בסביבה מקומית")
            bot.remove_webhook()
            time.sleep(0.5)
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print("הבוט הופסק על ידי המשתמש.")
    except Exception as e:
        print(f"שגיאה קריטית בהפעלת הבוט: {e}")

if __name__ == "__main__":
    main()
