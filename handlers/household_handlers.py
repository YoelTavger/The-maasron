from handlers.keyboards import (
    get_main_keyboard, get_settings_keyboard, get_cancel_keyboard,
    get_household_confirmation_keyboard, get_leave_household_confirmation_keyboard,
    get_join_household_confirmation_keyboard, get_currency_keyboard
)
from models.users import (
    get_user_household, register_user, remove_user_from_household,
    get_user_info, update_user_name, update_user_currency, get_user_currency
)
from models.households import (
    create_household, get_household_info, get_household_members,
    is_household_owner
)
from utils.helpers import send_error_message, prevent_duplicate_messages
import time

def register_household_handlers(bot):
    """
    רישום הטיפולים למשקי בית והגדרות
    
    Args:
        bot: מופע הבוט
    """
    
    # טיפול בהגדרות
    @bot.message_handler(func=lambda message: message.text == '⚙️ הגדרות')
    def settings_command(message):
        """טיפול בלחיצה על כפתור הגדרות"""
        chat_id = message.chat.id
        
        if not prevent_duplicate_messages(bot, chat_id, message.text):
            return
            
        bot.send_message(chat_id, "בחר באפשרות הרצויה:", reply_markup=get_settings_keyboard())
    
    # חזרה לתפריט הראשי
    @bot.message_handler(func=lambda message: message.text == '🔙 חזרה לתפריט הראשי')
    def back_to_main_menu(message):
        """חזרה לתפריט הראשי"""
        chat_id = message.chat.id
        
        if not prevent_duplicate_messages(bot, chat_id, message.text):
            return
            
        bot.send_message(chat_id, "חזרה לתפריט הראשי:", reply_markup=get_main_keyboard())
    
    # טיפול בשינוי שם
    @bot.message_handler(func=lambda message: message.text == '👤 שינוי שם')
    def change_name_command(message):
        """טיפול בבקשה לשינוי שם"""
        chat_id = message.chat.id
        
        if not prevent_duplicate_messages(bot, chat_id, message.text):
            return
        
        # הצגת השם הנוכחי
        user_info = get_user_info(message.from_user.id)
        current_name = ""
        if user_info:
            if user_info['first_name']:
                current_name = user_info['first_name']
                if user_info['last_name']:
                    current_name += f" {user_info['last_name']}"
        
        msg_text = f"השם הנוכחי שלך: {current_name if current_name else 'לא הוגדר'}\n\nהזן את השם החדש שלך:"
        msg = bot.send_message(chat_id, msg_text, reply_markup=get_cancel_keyboard())
        bot.register_next_step_handler(msg, process_new_name)

    def process_new_name(message):
        """מעבד את השם החדש"""
        chat_id = message.chat.id
        
        # בדיקה אם המשתמש ביקש לבטל
        if message.text == '❌ בטל פעולה':
            bot.send_message(chat_id, "❌ הפעולה בוטלה.", reply_markup=get_settings_keyboard())
            return
        
        new_name = message.text.strip()
        
        if not new_name:
            msg = bot.send_message(chat_id, "⚠️ השם לא יכול להיות ריק. נסה שוב:", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, process_new_name)
            return
        
        # פיצול לשם פרטי ומשפחה
        name_parts = new_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else None
        
        if update_user_name(message.from_user.id, first_name, last_name):
            bot.send_message(chat_id, f"✅ השם שונה בהצלחה ל: {new_name}", reply_markup=get_settings_keyboard())
        else:
            send_error_message(bot, chat_id, "כללית")
            bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())
    
    # טיפול בשינוי מטבע
    @bot.message_handler(func=lambda message: message.text == '💱 שינוי מטבע')
    def change_currency_command(message):
        """טיפול בבקשה לשינוי מטבע"""
        chat_id = message.chat.id
        
        if not prevent_duplicate_messages(bot, chat_id, message.text):
            return
        
        current_currency = get_user_currency(message.from_user.id)
        currency_name = "שקל ישראלי" if current_currency == 'ILS' else "דולר אמריקאי"
        
        markup = get_currency_keyboard()
        bot.send_message(
            chat_id, 
            f"המטבע הנוכחי שלך: {currency_name}\n\nאנא בחר מטבע חדש:", 
            reply_markup=markup
        )

    # טיפול בבחירת מטבע
    @bot.callback_query_handler(func=lambda call: call.data.startswith('currency_'))
    def handle_currency_choice(call):
        """מטפל בבחירת מטבע"""
        currency = call.data.replace('currency_', '')
        chat_id = call.message.chat.id
        
        if currency == 'cancel':
            bot.send_message(chat_id, "❌ הפעולה בוטלה.", reply_markup=get_settings_keyboard())
            bot.delete_message(chat_id, call.message.message_id)
            return
        
        if update_user_currency(call.from_user.id, currency):
            currency_name = "שקל ישראלי" if currency == 'ILS' else "דולר אמריקאי"
            bot.send_message(chat_id, f"✅ המטבע שונה בהצלחה ל: {currency_name}", reply_markup=get_settings_keyboard())
        else:
            send_error_message(bot, chat_id, "כללית")
            bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())
        
        bot.delete_message(chat_id, call.message.message_id)
    
    # טיפול בהצגת פרטי משק בית
    @bot.message_handler(func=lambda message: message.text == 'ℹ️ פרטי משק בית')
    def show_household_info_command(message):
        """טיפול בבקשה להציג פרטי משק בית"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        if not prevent_duplicate_messages(bot, chat_id, message.text):
            return
        
        # הצגת הודעת טעינה
        loading_msg = show_loading_message(bot, chat_id, "טוען פרטי משק בית", duration=2)
        
        try:
            # המתנה לסיום האנימציה
            time.sleep(2.5)
            # קבלת מזהה משק הבית של המשתמש
            household_id = get_user_household(user_id)
            
            if not household_id:
                bot.edit_message_text(
                    "⚠️ אינך משויך למשק בית. לחץ על '⚙️ הגדרות' כדי ליצור או להצטרף למשק בית.", 
                    chat_id, 
                    loading_msg.message_id,
                    reply_markup=None
                )
                time.sleep(1)
                bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())
                return
            
            share_text = f"הצטרף למשק הבית שלנו בבוט מעשרות! קוד ההצטרפות: `{household_id}`"
            share_url = f"https://t.me/share/url?url={share_text}"
            
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
`{household_id}`
[שתף]({share_url}) קוד זה עם בני משפחתך כדי שיוכלו להצטרף למשק הבית שלך.
"""
                
                bot.send_message(chat_id, info_text, parse_mode="Markdown", reply_markup=get_settings_keyboard())
            else:
                bot.send_message(chat_id, "⚠️ אירעה שגיאה בטעינת פרטי משק הבית.", reply_markup=get_settings_keyboard())
        except Exception as e:
            print(f"שגיאה בהצגת פרטי משק בית: {e}")
            bot.send_message(chat_id, "⚠️ אירעה שגיאה בטעינת הנתונים.", reply_markup=get_settings_keyboard())
    
    # טיפול ביצירת משק בית
    @bot.message_handler(func=lambda message: message.text == '👨‍👩‍👧‍👦 יצירת משק בית')
    def create_household_command(message):
        """טיפול בבקשה ליצור משק בית חדש"""
        chat_id = message.chat.id
        
        if not prevent_duplicate_messages(bot, chat_id, message.text):
            return
        
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
        
        # הצגת הודעת טעינה
        loading_msg = show_loading_message(bot, chat_id, "יוצר משק בית", duration=2)
        
        try:
            # המתנה לסיום האנימציה
            time.sleep(2.5)
            # יצירת משק בית חדש עם המשתמש הנוכחי כבעלים
            household_id = create_household(household_name, message.from_user.id)
            if household_id:
                # עדכון שיוך המשתמש למשק הבית החדש
                register_user(message.from_user, household_id)
                
                # יצירת קוד הצטרפות למשק הבית (משתמש במזהה של משק הבית)
                join_code = household_id
                share_text = f"הצטרף למשק הבית - '{household_name}' בבוט מעשרות! קוד ההצטרפות: `{join_code}`"
                share_url = f"https://t.me/share/url?url={share_text}"
                
                confirmation = f"""✅ משק הבית '{household_name}' נוצר בהצלחה!

👑 אתה הבעלים של משק בית זה.

הנה קוד ההצטרפות למשק הבית שלך:
`{join_code}`

[שתף]({share_url}) קוד זה עם בני משפחתך כדי שיוכלו להצטרף למשק הבית שלך.
"""
                bot.edit_message_text(confirmation, chat_id, loading_msg.message_id, parse_mode="Markdown")
                time.sleep(2)
                bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())
            else:
                bot.edit_message_text("⚠️ אירעה שגיאה ביצירת משק הבית.", chat_id, loading_msg.message_id)
                time.sleep(1)
                bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())
        except Exception as e:
            print(f"שגיאה ביצירת משק בית: {e}")
            bot.edit_message_text("⚠️ אירעה שגיאה ביצירת משק הבית.", chat_id, loading_msg.message_id)
            time.sleep(1)
            bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())

    # טיפול ביציאה ממשק בית
    @bot.message_handler(func=lambda message: message.text == '🚪 יציאה ממשק בית')
    def leave_household_command(message):
        """טיפול בבקשה לצאת ממשק בית"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        if not prevent_duplicate_messages(bot, chat_id, message.text):
            return
        
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
        
        if not prevent_duplicate_messages(bot, chat_id, message.text):
            return
        
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
        
        # הצגת הודעת טעינה
        loading_msg = show_loading_message(bot, chat_id, "מתחבר למשק בית", duration=2)
        
        try:
            # המתנה לסיום האנימציה
            time.sleep(2.5)
            # בדיקה אם קוד ההצטרפות תקין (קיים משק בית עם המזהה הזה)
            household_info = get_household_info(join_code)
            
            if household_info:
                # עדכון שיוך המשתמש למשק הבית
                register_user(message.from_user, join_code)
                
                confirmation = f"""✅ הצטרפת בהצלחה למשק הבית '{household_info['name']}'!

כעת תוכל לצפות בסטטוס המשפחתי ולנהל את המעשרות והתרומות במשותף.
"""
                bot.edit_message_text(confirmation, chat_id, loading_msg.message_id)
                time.sleep(2)
                bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())
            else:
                bot.edit_message_text("⚠️ קוד ההצטרפות אינו תקין.", chat_id, loading_msg.message_id)
                time.sleep(1)
                bot.send_message(chat_id, "נסה שוב או פנה למנהל משק הבית.\nחזרה להגדרות:", reply_markup=get_settings_keyboard())
        except Exception as e:
            print(f"שגיאה בהצטרפות למשק בית: {e}")
            bot.edit_message_text("⚠️ אירעה שגיאה בהצטרפות למשק הבית.", chat_id, loading_msg.message_id)
            time.sleep(1)
            bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())

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
            # הצגת הודעת טעינה
            loading_msg = show_loading_message(bot, chat_id, "יוצא ממשק בית", duration=2)
            
            try:
                # המתנה לסיום האנימציה
                time.sleep(2.5)
                if remove_user_from_household(user_id):
                    bot.edit_message_text("✅ יצאת בהצלחה ממשק הבית.", chat_id, loading_msg.message_id)
                    time.sleep(1)
                    bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())
                else:
                    bot.edit_message_text("⚠️ אירעה שגיאה ביציאה ממשק הבית.", chat_id, loading_msg.message_id)
                    time.sleep(1)
                    bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())
            except Exception as e:
                print(f"שגיאה ביציאה ממשק בית: {e}")
                bot.edit_message_text("⚠️ אירעה שגיאה ביציאה ממשק הבית.", chat_id, loading_msg.message_id)
                time.sleep(1)
                bot.send_message(chat_id, "חזרה להגדרות:", reply_markup=get_settings_keyboard())
        
        elif data == "cancel_leave_household":
            bot.send_message(chat_id, "❌ הפעולה בוטלה. נשארת במשק הבית הנוכחי.", reply_markup=get_settings_keyboard())
        
        elif data == "confirm_join_household":
            msg = bot.send_message(chat_id, "הזן את קוד ההצטרפות למשק הבית:", reply_markup=get_cancel_keyboard())
            bot.register_next_step_handler(msg, process_join_code)
        
        elif data == "cancel_join_household":
            bot.send_message(chat_id, "❌ הפעולה בוטלה. נשארת במשק הבית הנוכחי.", reply_markup=get_settings_keyboard())
        
        # מחיקת ההודעה הקודמת עם הכפתורים
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass