from handlers.keyboards import get_main_keyboard, get_cancel_keyboard
from models.maaser import add_maaser
from utils.helpers import validate_date_format, send_error_message, prevent_duplicate_messages
import time

def register_maaser_handlers(bot):
    """
    רישום הטיפולים למעשרות
    
    Args:
        bot: מופע הבוט
    """
    
    # טיפול במעשר חדש
    @bot.message_handler(func=lambda message: message.text == '💼 מעשר חדש')
    def new_maaser(message):
        """טיפול בבקשה להוסיף מעשר חדש"""
        chat_id = message.chat.id
        
        if not prevent_duplicate_messages(bot, chat_id, message.text):
            return
            
        msg = bot.send_message(chat_id, "הזן את סכום המעשר:", reply_markup=get_cancel_keyboard())
        bot.register_next_step_handler(msg, process_maaser_amount)

    def process_maaser_amount(message):
        """מעבד את הסכום למעשר"""
        chat_id = message.chat.id
        
        # בדיקה אם המשתמש ביקש לבטל
        if message.text == '❌ בטל פעולה':
            bot.send_message(chat_id, "❌ הפעולה בוטלה.", reply_markup=get_main_keyboard())
            return
        
        try:
            amount = float(message.text)
            if amount <= 0:
                msg = bot.send_message(chat_id, "⚠️ הסכום חייב להיות חיובי. נסה שוב:", reply_markup=get_cancel_keyboard())
                bot.register_next_step_handler(msg, process_maaser_amount)
                return
            
            # שמירת הסכום בזיכרון זמני
            bot.temp_data = bot.temp_data if hasattr(bot, 'temp_data') else {}
            if chat_id not in bot.temp_data:
                bot.temp_data[chat_id] = {}
            bot.temp_data[chat_id]['amount'] = amount
            
            msg = bot.send_message(chat_id, "מה מקור ההכנסה למעשר?", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, process_maaser_source)
        except ValueError:
            msg = bot.send_message(chat_id, "⚠️ ערך לא תקין. הזן מספר בלבד:", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, process_maaser_amount)

    def process_maaser_source(message):
        """מעבד את מקור המעשר"""
        chat_id = message.chat.id
        
        # בדיקה אם המשתמש ביקש לבטל
        if message.text == '❌ בטל פעולה':
            bot.send_message(chat_id, "❌ הפעולה בוטלה.", reply_markup=get_main_keyboard())
            return
        
        source = message.text
        
        # שמירת המקור בזיכרון זמני
        bot.temp_data[chat_id]['source'] = source

        msg = bot.send_message(chat_id, "הזן תאריך יעד לתרומה (בפורמט DD-MM-YYYY) או רשום 'אין' אם אין תאריך יעד:", reply_markup=get_cancel_keyboard())
        bot.register_next_step_handler(msg, process_maaser_deadline)

    def process_maaser_deadline(message):
        """מעבד את תאריך היעד"""
        chat_id = message.chat.id
        
        # בדיקה אם המשתמש ביקש לבטל
        if message.text == '❌ בטל פעולה':
            bot.send_message(chat_id, "❌ הפעולה בוטלה.", reply_markup=get_main_keyboard())
            return
        
        deadline = message.text
        
        if deadline.lower() == 'אין':
            deadline = None
        else:
            if not validate_date_format(deadline, '%d-%m-%Y'):
                msg = bot.send_message(chat_id, "⚠️ פורמט תאריך לא תקין. נסה שוב (DD-MM-YYYY):", reply_markup=get_cancel_keyboard())
                bot.register_next_step_handler(msg, process_maaser_deadline)
                return
        
        # הצגת הודעת טעינה
        loading_msg = show_loading_message(bot, chat_id, "שומר מעשר", duration=2)
        
        try:
            # המתנה לסיום האנימציה
            time.sleep(2.5)
            # הוספת המעשר למסד הנתונים
            amount = bot.temp_data[chat_id]['amount']
            source = bot.temp_data[chat_id]['source']
            
            if add_maaser(message.from_user.id, amount, source, deadline):
                confirmation = f"""✅ המעשר נרשם בהצלחה!

💰 סכום: {amount} ₪
📝 מקור: {source}
"""
                if deadline:
                    confirmation += f"📅 תאריך יעד: {deadline}"
                
                bot.edit_message_text(confirmation, chat_id, loading_msg.message_id)
                time.sleep(2)
                bot.send_message(chat_id, "חזרה לתפריט הראשי:", reply_markup=get_main_keyboard())
            else:
                bot.edit_message_text("⚠️ אירעה שגיאה בשמירת המעשר.", chat_id, loading_msg.message_id)
                time.sleep(1)
                bot.send_message(chat_id, "חזרה לתפריט הראשי:", reply_markup=get_main_keyboard())
        except Exception as e:
            print(f"שגיאה בשמירת מעשר: {e}")
            send_error_message(bot, chat_id, "מסד נתונים")
            try:
                bot.delete_message(chat_id, loading_msg.message_id)
            except:
                pass
            time.sleep(1)
            bot.send_message(chat_id, "חזרה לתפריט הראשי:", reply_markup=get_main_keyboard())