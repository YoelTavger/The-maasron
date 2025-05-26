from handlers.keyboards import get_main_keyboard, get_cancel_keyboard
from models.users import register_user
from utils.helpers import prevent_duplicate_messages
from config import ADMIN_USER_ID

def register_handlers(bot):
    """
    רישום הטיפולים הבסיסיים
    
    Args:
        bot: מופע הבוט
    """
    # פקודת התחלה
    @bot.message_handler(commands=['start'])
    def start_command(message):
        """טיפול בפקודת התחלה"""
        user = message.from_user
        chat_id = message.chat.id
        
        # מניעת הודעות כפולות
        if not prevent_duplicate_messages(bot, chat_id, f"/start_{user.id}"):
            return
        
        register_user(user)
        
        # שליחת דיווח למנהל על משתמש חדש/חוזר
        if ADMIN_USER_ID:
            try:
                admin_message = f"""🔔 פעילות בבוט:
                
👤 משתמש: {user.first_name} {user.last_name or ''}
🆔 מזהה: {user.id}
👀 שם משתמש: @{user.username or 'ללא'}
⏰ פעולה: הפעלת /start
"""
                bot.send_message(ADMIN_USER_ID, admin_message)
            except Exception as e:
                print(f"שגיאה בשליחת דיווח למנהל: {e}")
        
        welcome_text = f"""👋 שלום {user.first_name}! 

ברוכים הבאים לבוט ניהול המעשרות.
באמצעות הבוט תוכל/י:
- לרשום מעשרות ומקורותיהם
- לתעד תרומות שביצעת
- לראות סטטיסטיקות של המעשרות והתרומות שלך
- לנהל חשבון משק בית משותף

השתמש/י בכפתורים למטה כדי להתחיל 👇"""
        
        bot.send_message(chat_id, welcome_text, reply_markup=get_main_keyboard())
    
    # טיפול בכפתור ביטול פעולה
    @bot.message_handler(func=lambda message: message.text == '❌ בטל פעולה')
    def cancel_operation(message):
        """טיפול בלחיצה על כפתור ביטול"""
        chat_id = message.chat.id
        
        if not prevent_duplicate_messages(bot, chat_id, message.text):
            return
            
        bot.send_message(chat_id, "❌ הפעולה הנוכחית בוטלה.", reply_markup=get_main_keyboard())
    
    # טיפול בהודעות טקסט אחרות
    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        """מטפל בכל הודעה שאינה פקודה מוכרת"""
        chat_id = message.chat.id
        
        if not prevent_duplicate_messages(bot, chat_id, "unknown_message"):
            return
            
        bot.send_message(chat_id, "השתמש בכפתורים למטה או הקלד /start כדי להתחיל.", reply_markup=get_main_keyboard())