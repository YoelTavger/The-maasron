### handlers/household_handlers.py ###

from handlers.keyboards import (
    get_main_keyboard, get_settings_keyboard, get_cancel_keyboard,
    get_household_confirmation_keyboard, get_leave_household_confirmation_keyboard,
    get_join_household_confirmation_keyboard
)
from models.users import get_user_household, register_user, remove_user_from_household
from models.households import (
    create_household, get_household_info, get_household_members,
    is_household_owner
)

def register_household_handlers(bot):
    """
    רישום הטיפולים למשקי בית
    
    Args:
        bot: מופע הבוט
    """
    
    # טיפול בהגדרות
    @bot.message_handler(func=lambda message: message.text == '⚙️ הגדרות')
    def settings_command(message):
        """טיפול בלחיצה על כפתור הגדרות"""
        chat_id = message.chat.id
        bot.send_message(chat_id, "בחר באפשרות הרצויה:", reply_markup=get_settings_keyboard())
    
    # חזרה לתפריט הראשי
    @bot.message_handler(func=lambda message: message.text == '🔙 חזרה לתפריט הראשי')
    def back_to_main_menu(message):
        """חזרה לתפריט הראשי"""
        bot.send_message(message.chat.id, "חזרה לתפריט הראשי:", reply_markup=get_main_keyboard())
    
    # טיפול בהצגת פרטי משק בית
    @bot.message_handler(func=lambda message: message.text == 'ℹ️ פרטי משק בית')
    def show_household_info_command(message):
        """טיפול בבקשה להציג פרטי משק בית"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # קבלת מזהה משק הבית של המשתמש
        household_id = get_user_household(user_id)
        
        if not household_id:
            bot.send_message(chat_id, "⚠️ אינך משויך למשק בית. לחץ על '⚙️ הגדרות' כדי ליצור או להצטרף למשק בית.", reply_markup=get_settings_keyboard())
            return
        
        # קבלת פרטי משק הבית
        household_info = get_household_info(household_id)
        
        if household_info:
            household_name = household_info['name']
            creation_date = household_info['creation_date']
            owner_id = household_info.get('owner_id')
            
            # קבלת רשימת החברים במשק הבית
            members = get_household_members(household_id)
            
            # בדיקה אם המשתמש הוא הבעלים של משק הבית
            is_owner = str(owner_id) == str(user_id) if owner_id else False
            
            info_text = f"""ℹ️ פרטי משק הבית:

🏠 שם: {household_name}
📅 תאריך יצירה: {creation_date}
👥 מספר חברים: {len(members)}
"""

            # הוספת רשימת החברים
            if members:
                info_text += "\n👨‍👩‍👧‍👦 חברי משק הבית:\n"
                for i, member in enumerate(members, 1):
                    member_name = f"{member['first_name']} {member['last_name']}".strip()
                    if not member_name:
                        member_name = member['username'] if member['username'] else f"משתמש {i}"
                    
                    if str(member['user_id']) == str(owner_id):
                        info_text += f"{i}. {member_name} 👑\n"
                    else:
                        info_text += f"{i}. {member_name}\n"
            
            if is_owner:
                info_text += f"""\n👑 אתה הבעלים של משק בית זה

קוד הצטרפות למשק הבית:
{household_id}
שתף קוד זה עם בני משפחתך כדי שיוכלו להצטרף למשק הבית שלך.
"""
            
            bot.send_message(chat_id, info_text, parse_mode="Markdown", reply_markup=get_settings_keyboard())
        else:
            bot.send_message(chat_id, "⚠️ אירעה שגיאה בטעינת פרטי משק הבית. נסה שוב מאוחר יותר.", reply_markup=get_settings_keyboard())
    
    # טיפול ביצירת משק בית
    @bot.message_handler(func=lambda message: message.text == '👨‍👩‍👧‍👦 יצירת משק בית')
    def create_household_command(message):
        """טיפול בבקשה ליצור משק בית חדש"""
        chat_id = message.chat.id
        
        # בדיקה אם המשתמש כבר שייך למשק בית
        household_id = get_user_household(message.from_user.id)
        if household_id:
            household_info = get_household_info(household_id)
            household_name = household_info['name'] if household_info else "לא ידוע"
            
            msg = f"⚠️ אתה כבר שייך למשק בית '{household_name}'.\nהאם אתה בטוח שברצונך ליצור משק בית חדש?"
            
            markup = get_household_confirmation_keyboard()
            
            bot.send_message(chat_id, msg, reply_markup=markup)
        else:
            msg = bot.send_message(chat_id, "הזן שם למשק הבית החדש:", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, process_household_name)

    def process_household_name(message):
        """מעבד את שם משק הבית החדש"""
        chat_id = message.chat.id
        
        # בדיקה אם המשתמש ביקש לבטל
        if message.text == '❌ בטל פעולה':
            bot.send_message(chat_id, "❌ הפעולה בוטלה.", reply_markup=get_settings_keyboard())
            return
        
        household_name = message.text.strip()
        
        if not household_name:
            msg = bot.send_message(chat_id, "⚠️ שם משק הבית לא יכול להיות ריק. נסה שוב:", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, process_household_name)
            return
        
        # יצירת משק בית חדש עם המשתמש הנוכחי כבעלים
        household_id = create_household(household_name, message.from_user.id)
        if household_id:
            # עדכון שיוך המשתמש למשק הבית החדש
            register_user(message.from_user, household_id)
            
            # יצירת קוד הצטרפות למשק הבית (משתמש במזהה של משק הבית)
            join_code = household_id
            
            confirmation = f"""✅ משק הבית '{household_name}' נוצר בהצלחה!

👑 אתה הבעלים של משק בית זה.

הנה קוד ההצטרפות למשק הבית שלך:
{join_code}

שתף קוד זה עם בני משפחתך כדי שיוכלו להצטרף למשק הבית שלך.
"""
            bot.send_message(chat_id, confirmation, parse_mode="Markdown", reply_markup=get_settings_keyboard())
        else:
            bot.send_message(chat_id, "⚠️ אירעה שגיאה ביצירת משק הבית. נסה שוב מאוחר יותר.", reply_markup=get_settings_keyboard())

    # טיפול ביציאה ממשק בית
    @bot.message_handler(func=lambda message: message.text == '🚪 יציאה ממשק בית')
    def leave_household_command(message):
        """טיפול בבקשה לצאת ממשק בית"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # בדיקה אם המשתמש שייך למשק בית
        household_id = get_user_household(user_id)
        if not household_id:
            bot.send_message(chat_id, "⚠️ אינך משויך למשק בית.", reply_markup=get_settings_keyboard())
            return
        
        # בדיקה אם המשתמש הוא הבעלים של משק הבית
        if is_household_owner(user_id, household_id):
            msg = "⚠️ אתה הבעלים של משק הבית הזה. אם תצא, משק הבית יישאר ללא בעלים.\nהאם אתה בטוח שברצונך לצאת ממשק הבית?"
        else:
            household_info = get_household_info(household_id)
            household_name = household_info['name'] if household_info else "לא ידוע"
            msg = f"⚠️ האם אתה בטוח שברצונך לצאת ממשק הבית '{household_name}'?"
        
        markup = get_leave_household_confirmation_keyboard()
        
        bot.send_message(chat_id, msg, reply_markup=markup)

    # טיפול בהצטרפות למשק בית
    @bot.message_handler(func=lambda message: message.text == '➕ הצטרפות למשק בית')
    def join_household_command(message):
        """טיפול בבקשה להצטרף למשק בית קיים"""
        chat_id = message.chat.id
        
        # בדיקה אם המשתמש כבר שייך למשק בית
        household_id = get_user_household(message.from_user.id)
        if household_id:
            household_info = get_household_info(household_id)
            household_name = household_info['name'] if household_info else "לא ידוע"
            
            msg = f"⚠️ אתה כבר שייך למשק בית '{household_name}'.\nהאם אתה בטוח שברצונך לעזוב ולהצטרף למשק בית אחר?"
            
            markup = get_join_household_confirmation_keyboard()
            
            bot.send_message(chat_id, msg, reply_markup=markup)
        else:
            msg = bot.send_message(chat_id, "הזן את קוד ההצטרפות למשק הבית:", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, process_join_code)

    def process_join_code(message):
        """מעבד את קוד ההצטרפות למשק בית"""
        chat_id = message.chat.id
        
        # בדיקה אם המשתמש ביקש לבטל
        if message.text == '❌ בטל פעולה':
            bot.send_message(chat_id, "❌ הפעולה בוטלה.", reply_markup=get_settings_keyboard())
            return
        
        join_code = message.text.strip()
        
        # בדיקה אם קוד ההצטרפות תקין (קיים משק בית עם המזהה הזה)
        household_info = get_household_info(join_code)
        
        if household_info:
            # עדכון שיוך המשתמש למשק הבית
            register_user(message.from_user, join_code)
            
            confirmation = f"""✅ הצטרפת בהצלחה למשק הבית '{household_info['name']}'!

כעת תוכל לצפות בסטטוס המשפחתי ולנהל את המעשרות והתרומות במשותף.
"""
            bot.send_message(chat_id, confirmation, reply_markup=get_settings_keyboard())
        else:
            bot.send_message(chat_id, "⚠️ קוד ההצטרפות אינו תקין. נסה שוב או פנה למנהל משק הבית.", reply_markup=get_settings_keyboard())

    # טיפול באישור פעולות משק בית
    @bot.callback_query_handler(func=lambda call: call.data in [
        "confirm_new_household", "cancel_new_household",
        "confirm_leave_household", "cancel_leave_household",
        "confirm_join_household", "cancel_join_household"
    ])
    def handle_household_confirmations(call):
        """מטפל באישור פעולות משק בית"""
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        data = call.data
        
        if data == "confirm_new_household":
            msg = bot.send_message(chat_id, "הזן שם למשק הבית החדש:", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, process_household_name)
        
        elif data == "cancel_new_household":
            bot.send_message(chat_id, "❌ הפעולה בוטלה. נשארת במשק הבית הנוכחי.", reply_markup=get_settings_keyboard())
        
        elif data == "confirm_leave_household":
            if remove_user_from_household(user_id):
                bot.send_message(chat_id, "✅ יצאת בהצלחה ממשק הבית.", reply_markup=get_settings_keyboard())
            else:
                bot.send_message(chat_id, "⚠️ אירעה שגיאה ביציאה ממשק הבית. נסה שוב מאוחר יותר.", reply_markup=get_settings_keyboard())
        
        elif data == "cancel_leave_household":
            bot.send_message(chat_id, "❌ הפעולה בוטלה. נשארת במשק הבית הנוכחי.", reply_markup=get_settings_keyboard())
        
        elif data == "confirm_join_household":
            msg = bot.send_message(chat_id, "הזן את קוד ההצטרפות למשק הבית:", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, process_join_code)
        
        elif data == "cancel_join_household":
            bot.send_message(chat_id, "❌ הפעולה בוטלה. נשארת במשק הבית הנוכחי.", reply_markup=get_settings_keyboard())
        
        # מחיקת ההודעה הקודמת עם הכפתורים
        bot.delete_message(chat_id, call.message.message_id)