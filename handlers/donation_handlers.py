from handlers.keyboards import get_main_keyboard, get_cancel_keyboard, get_payment_method_keyboard
from models.donations import add_donation
from utils.helpers import send_error_message, prevent_duplicate_messages
import time

def register_donation_handlers(bot):
   """
   רישום הטיפולים לתרומות
   
   Args:
       bot: מופע הבוט
   """
   
   # טיפול בתרומה חדשה
   @bot.message_handler(func=lambda message: message.text == '💰 תרומה חדשה')
   def new_donation(message):
       """טיפול בבקשה להוסיף תרומה חדשה"""
       chat_id = message.chat.id
       
       if not prevent_duplicate_messages(bot, chat_id, message.text):
           return
           
       msg = bot.send_message(chat_id, "הזן את סכום התרומה:", reply_markup=get_cancel_keyboard())
       bot.register_next_step_handler(msg, process_donation_amount)

   def process_donation_amount(message):
       """מעבד את סכום התרומה"""
       chat_id = message.chat.id
       
       # בדיקה אם המשתמש ביקש לבטל
       if message.text == '❌ בטל פעולה':
           bot.send_message(chat_id, "❌ הפעולה בוטלה.", reply_markup=get_main_keyboard())
           return
       
       try:
           amount = float(message.text)
           if amount <= 0:
               msg = bot.send_message(chat_id, "⚠️ הסכום חייב להיות חיובי. נסה שוב:", reply_markup=get_cancel_keyboard())
               bot.register_next_step_handler(msg, process_donation_amount)
               return
           
           # שמירת הסכום בזיכרון זמני
           bot.temp_data = bot.temp_data if hasattr(bot, 'temp_data') else {}
           if chat_id not in bot.temp_data:
               bot.temp_data[chat_id] = {}
           bot.temp_data[chat_id]['amount'] = amount
           
           msg = bot.send_message(chat_id, "מה מטרת התרומה?", reply_markup=get_cancel_keyboard())
           bot.register_next_step_handler(msg, process_donation_purpose)
       except ValueError:
           msg = bot.send_message(chat_id, "⚠️ ערך לא תקין. הזן מספר בלבד:", reply_markup=get_cancel_keyboard())
           bot.register_next_step_handler(msg, process_donation_amount)

   def process_donation_purpose(message):
       """מעבד את מטרת התרומה"""
       chat_id = message.chat.id
       
       # בדיקה אם המשתמש ביקש לבטל
       if message.text == '❌ בטל פעולה':
           bot.send_message(chat_id, "❌ הפעולה בוטלה.", reply_markup=get_main_keyboard())
           return
       
       purpose = message.text
       
       # שמירת המטרה בזיכרון זמני
       bot.temp_data[chat_id]['purpose'] = purpose
       
       # יצירת מקלדת לבחירת אמצעי תשלום
       markup = get_payment_method_keyboard()
       
       bot.send_message(chat_id, "בחר אמצעי תשלום:", reply_markup=markup)

   # טיפול בבחירת אמצעי תשלום
   @bot.callback_query_handler(func=lambda call: call.data.startswith('method_'))
   def handle_payment_method(call):
       """מטפל בבחירת אמצעי תשלום"""
       method = call.data.replace('method_', '')
       chat_id = call.message.chat.id
       
       # בדיקה אם המשתמש ביקש לבטל
       if method == 'cancel':
           bot.send_message(chat_id, "❌ הפעולה בוטלה.", reply_markup=get_main_keyboard())
           try:
               bot.delete_message(chat_id, call.message.message_id)
           except:
               pass
           return
       
       method_names = {
           'cash': '💵 מזומן',
           'bank': '🏦 העברה בנקאית',
           'credit': '💳 אשראי',
           'other': '📱 אחר'
       }
       
       # וידוא שקיים מידע בזיכרון הזמני
       if chat_id not in bot.temp_data:
           send_error_message(bot, chat_id, "כללית")
           try:
               bot.delete_message(chat_id, call.message.message_id)
           except:
               pass
           time.sleep(1)
           bot.send_message(chat_id, "חזרה לתפריט הראשי:", reply_markup=get_main_keyboard())
           return
       
       # הוספת התרומה למסד הנתונים
       amount = bot.temp_data[chat_id].get('amount')
       purpose = bot.temp_data[chat_id].get('purpose')
       
       if amount is None or purpose is None:
           send_error_message(bot, chat_id, "כללית")
           try:
               bot.delete_message(chat_id, call.message.message_id)
           except:
               pass
           time.sleep(1)
           bot.send_message(chat_id, "חזרה לתפריט הראשי:", reply_markup=get_main_keyboard())
           return
       
       # שמירת התרומה במסד הנתונים
       try:
           # מחיקת ההודעה הקודמת עם הכפתורים
           try:
               bot.delete_message(chat_id, call.message.message_id)
           except:
               pass
           
           if add_donation(call.from_user.id, amount, purpose, method_names[method]):
               confirmation = f"""✅ התרומה נרשמה בהצלחה!

💰 סכום: {amount} ₪
🎯 מטרה: {purpose}
💳 אמצעי תשלום: {method_names[method]}
"""
               bot.send_message(chat_id, confirmation)
               time.sleep(2)
               bot.send_message(chat_id, "חזרה לתפריט הראשי:", reply_markup=get_main_keyboard())
           else:
               bot.send_message(chat_id, "⚠️ אירעה שגיאה בשמירת התרומה.")
               time.sleep(1)
               bot.send_message(chat_id, "חזרה לתפריט הראשי:", reply_markup=get_main_keyboard())
       except Exception as e:
           print(f"שגיאה בשמירת תרומה: {e}")
           bot.send_message(chat_id, "⚠️ אירעה שגיאה בשמירת התרומה.")
           time.sleep(1)
           bot.send_message(chat_id, "חזרה לתפריט הראשי:", reply_markup=get_main_keyboard())
       
       # נקיון הזיכרון הזמני
       if chat_id in bot.temp_data:
           del bot.temp_data[chat_id]