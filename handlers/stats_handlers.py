from handlers.keyboards import get_main_keyboard, get_stats_detail_keyboard
from models.stats import get_stats
from models.users import get_user_household
from utils.helpers import format_currency

def register_stats_handlers(bot):
    """
    רישום הטיפולים לסטטיסטיקות
    
    Args:
        bot: מופע הבוט
    """
    
    # טיפול בהצגת סטטוס אישי
    @bot.message_handler(func=lambda message: message.text == '📊 הצג סטטוס אישי')
    def show_personal_status(message):
        """טיפול בבקשה להציג סטטוס אישי"""
        show_status(message, bot, household=False)

    # טיפול בהצגת סטטוס משפחתי
    @bot.message_handler(func=lambda message: message.text == '👨‍👩‍👧‍👦 הצג סטטוס משפחתי')
    def show_household_status(message):
        """טיפול בבקשה להציג סטטוס משפחתי"""
        household_id = get_user_household(message.from_user.id)
        
        if not household_id:
            bot.send_message(message.chat.id, "⚠️ אינך משויך למשק בית. לחץ על '⚙️ הגדרות' כדי ליצור או להצטרף למשק בית.", reply_markup=get_main_keyboard())
            return
        
        show_status(message, bot, household=True)

    # פונקציה להצגת סטטוס
    def show_status(message, bot, household=False):
        """טיפול בבקשה להציג סטטוס"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        user_stats = get_stats(user_id, household=household)
        
        if user_stats:
            # יצירת מקלדת עם כפתורים לצפייה בפרטים נוספים
            markup = get_stats_detail_keyboard(household)
            
            status_title = "👨‍👩‍👧‍👦 סטטוס מעשרות משפחתי:" if household else "📊 סטטוס מעשרות אישי:"
            status_text = f"""{status_title}

💼 סה"כ מעשרות: {format_currency(user_stats['total_maaser'])}
✅ סה"כ תרומות שבוצעו: {format_currency(user_stats['total_donated'])}
🔄 יתרת חובות מעשר: {format_currency(user_stats['balance'])}

לחץ על הכפתורים למטה לפרטים נוספים.
"""
            bot.send_message(chat_id, status_text, reply_markup=markup)
        else:
            bot.send_message(chat_id, "⚠️ אירעה שגיאה בטעינת הנתונים. נסה שוב מאוחר יותר.", reply_markup=get_main_keyboard())

    # טיפול בבקשות לפרטים נוספים
    @bot.callback_query_handler(func=lambda call: call.data.startswith('details_'))
    def handle_details_request(call):
        """מטפל בבקשות לפרטים נוספים"""
        parts = call.data.split('_')
        detail_type = parts[1]
        household = len(parts) > 2 and parts[2] == 'household'
        
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        
        user_stats = get_stats(user_id, household=household)
        
        if user_stats:
            if detail_type == 'maasrot':
                details = "📋 פירוט מעשרות:\n\n"
                
                if user_stats['maasrot']:
                    for i, maaser in enumerate(user_stats['maasrot'], 1):
                        details += f"{i}. 💰 {format_currency(maaser['amount'])} - {maaser['source']}\n"
                        details += f"   📅 תאריך: {maaser['date']}\n"
                        if maaser['deadline']:
                            details += f"   🔔 יעד: {maaser['deadline']}\n"
                        details += "\n"
                else:
                    details += "🔍 אין מעשרות רשומים."
                
                bot.send_message(chat_id, details)
            
            elif detail_type == 'donations':
                details = "🧾 פירוט תרומות שבוצעו:\n\n"
                
                if user_stats['donations']:
                    for i, donation in enumerate(user_stats['donations'], 1):
                        details += f"{i}. 💸 {format_currency(donation['amount'])} - {donation['purpose']}\n"
                        details += f"   📅 תאריך: {donation['date']}\n"
                        details += f"   💳 אמצעי: {donation['method']}\n"
                        details += "\n"
                else:
                    details += "🔍 אין תרומות רשומות."
                
                bot.send_message(chat_id, details)
        else:
            bot.send_message(chat_id, "⚠️ אירעה שגיאה בטעינת הנתונים. נסה שוב מאוחר יותר.")
