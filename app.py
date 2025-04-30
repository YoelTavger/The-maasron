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
        time.sleep(1)
        
        # הרצת הבוט - בדיקה אם רץ בסביבת Render
        if os.environ.get('RENDER'):
            # הגדרת webhook עבור Render
            PORT = int(os.environ.get('PORT', 5000))
            WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
            
            bot.set_webhook(url=WEBHOOK_URL)
            # הפעלת שרת webhook
            from flask import Flask, request
            
            app = Flask(__name__)
            
            @app.route('/' + API_TOKEN, methods=['POST'])
            def webhook():
                update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
                bot.process_new_updates([update])
                return ''
            
            @app.route('/')
            def index():
                return "בוט פעיל!"
            
            app.run(host='0.0.0.0', port=PORT)
        else:
            # הרצה רגילה עם polling
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print("הבוט הופסק על ידי המשתמש.")
    except Exception as e:
        print(f"שגיאה קריטית בהפעלת הבוט: {e}")

if __name__ == "__main__":
    main()
### test