from handlers.keyboards import get_main_keyboard, get_cancel_keyboard
from models.users import register_user

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
        register_user(user)
        
        welcome_text = f"""👋 שלום {user.first_name}! 

ברוכים הבאים לבוט ניהול המעשרות.
באמצעות הבוט תוכל/י:
- לרשום מעשרות ומקורותיהם
- לתעד תרומות שביצעת
- לראות סטטיסטיקות של המעשרות והתרומות שלך
- לנהל חשבון משק בית משותף

השתמש/י בכפתורים למטה כדי להתחיל 👇"""
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())
    
    # טיפול בכפתור ביטול פעולה
    @bot.message_handler(func=lambda message: message.text == '❌ בטל פעולה')
    def cancel_operation(message):
        """טיפול בלחיצה על כפתור ביטול"""
        chat_id = message.chat.id
        bot.send_message(chat_id, "❌ הפעולה הנוכחית בוטלה.", reply_markup=get_main_keyboard())
    
    # טיפול בהודעות טקסט אחרות
    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        """מטפל בכל הודעה שאינה פקודה מוכרת"""
        bot.send_message(message.chat.id, "השתמש בכפתורים למטה או הקלד /start כדי להתחיל.", reply_markup=get_main_keyboard())
        