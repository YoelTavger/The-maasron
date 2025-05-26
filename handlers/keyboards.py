from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_cancel_keyboard():
    """
    יוצר מקלדת עם כפתור ביטול
    
    Returns:
        ReplyKeyboardMarkup: מקלדת עם כפתור ביטול
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = KeyboardButton('❌ בטל פעולה')
    markup.add(btn1)
    return markup

def get_main_keyboard():
    """
    יוצר מקלדת ראשית עם כפתורים
    
    Returns:
        ReplyKeyboardMarkup: מקלדת ראשית
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton('💰 תרומה חדשה')
    btn2 = KeyboardButton('💼 מעשר חדש')
    btn3 = KeyboardButton('📊 הצג סטטוס אישי')
    btn4 = KeyboardButton('👨‍👩‍👧‍👦 הצג סטטוס משפחתי')
    btn5 = KeyboardButton('⚙️ הגדרות')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    return markup

def get_settings_keyboard():
    """
    יוצר מקלדת הגדרות מורחבת
    
    Returns:
        ReplyKeyboardMarkup: מקלדת הגדרות
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = KeyboardButton('👨‍👩‍👧‍👦 יצירת משק בית')
    btn2 = KeyboardButton('➕ הצטרפות למשק בית')
    btn3 = KeyboardButton('🚪 יציאה ממשק בית')
    btn4 = KeyboardButton('ℹ️ פרטי משק בית')
    btn5 = KeyboardButton('👤 שינוי שם')
    btn6 = KeyboardButton('💱 שינוי מטבע')
    btn7 = KeyboardButton('🔙 חזרה לתפריט הראשי')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7)
    return markup

def get_currency_keyboard():
    """
    יוצר מקלדת לבחירת מטבע
    
    Returns:
        InlineKeyboardMarkup: מקלדת בחירת מטבע
    """
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("₪ שקל ישראלי", callback_data="currency_ILS"),
        InlineKeyboardButton("$ דולר אמריקאי", callback_data="currency_USD")
    )
    markup.row(
        InlineKeyboardButton("❌ ביטול", callback_data="currency_cancel")
    )
    return markup

def get_payment_method_keyboard():
    """
    יוצר מקלדת לבחירת אמצעי תשלום
    
    Returns:
        InlineKeyboardMarkup: מקלדת בחירת אמצעי תשלום
    """
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("💵 מזומן", callback_data="method_cash"),
        InlineKeyboardButton("🏦 העברה בנקאית", callback_data="method_bank")
    )
    markup.row(
        InlineKeyboardButton("💳 אשראי", callback_data="method_credit"),
        InlineKeyboardButton("📱 אחר", callback_data="method_other")
    )
    markup.row(
        InlineKeyboardButton("❌ ביטול", callback_data="method_cancel")
    )
    return markup

def get_stats_detail_keyboard(household=False):
    """
    יוצר מקלדת לפרטי סטטיסטיקות
    
    Args:
        household: האם מדובר בסטטוס משק בית
        
    Returns:
        InlineKeyboardMarkup: מקלדת פרטי סטטיסטיקות
    """
    markup = InlineKeyboardMarkup()
    household_suffix = '_household' if household else ''
    markup.row(
        InlineKeyboardButton("📝 פרטי מעשרות", callback_data=f"details_maasrot{household_suffix}"),
        InlineKeyboardButton("💰 פרטי תרומות", callback_data=f"details_donations{household_suffix}")
    )
    return markup

def get_household_confirmation_keyboard():
    """
    יוצר מקלדת אישור ליצירת משק בית חדש
    
    Returns:
        InlineKeyboardMarkup: מקלדת אישור
    """
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ כן, ליצור משק בית חדש", callback_data="confirm_new_household"),
        InlineKeyboardButton("❌ לא, להישאר במשק הבית הנוכחי", callback_data="cancel_new_household")
    )
    return markup

def get_leave_household_confirmation_keyboard():
    """
    יוצר מקלדת אישור ליציאה ממשק בית
    
    Returns:
        InlineKeyboardMarkup: מקלדת אישור
    """
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ כן, לצאת ממשק הבית", callback_data="confirm_leave_household"),
        InlineKeyboardButton("❌ לא, להישאר במשק הבית", callback_data="cancel_leave_household")
    )
    return markup

def get_join_household_confirmation_keyboard():
    """
    יוצר מקלדת אישור להצטרפות למשק בית אחר
    
    Returns:
        InlineKeyboardMarkup: מקלדת אישור
    """
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ כן, להצטרף למשק בית אחר", callback_data="confirm_join_household"),
        InlineKeyboardButton("❌ לא, להישאר במשק הבית הנוכחי", callback_data="cancel_join_household")
    )
    return markup