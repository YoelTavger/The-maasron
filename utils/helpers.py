"""
מודול עזר המכיל פונקציות שימושיות לכל הפרויקט
"""

from datetime import datetime
import time

def validate_date_format(date_str, format_str='%d-%m-%Y'):
    """
    בודק אם מחרוזת התאריך תואמת את הפורמט הנדרש
    
    Args:
        date_str: מחרוזת התאריך לבדיקה
        format_str: פורמט התאריך הרצוי
    
    Returns:
        bool: האם התאריך תקין
    """
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False

def format_currency(amount, currency='ILS'):
    """
    מפרמט מספר לתצוגת מטבע
    
    Args:
        amount: סכום כספי
        currency: סוג המטבע ('ILS' לשקל, 'USD' לדולר)
    
    Returns:
        str: הסכום מפורמט (לדוגמה: 100.00 ₪ או $100.00)
    """
    if currency == 'USD':
        return f"${float(amount):.2f}"
    else:  # ברירת מחדל לשקל
        return f"{float(amount):.2f} ₪"

def format_date(date_str):
    """
    מפרמט תאריך לתצוגה בפורמט DD-MM-YYYY ללא שעה
    
    Args:
        date_str: מחרוזת תאריך במבנה YYYY-MM-DD HH:MM
        
    Returns:
        str: תאריך מפורמט DD-MM-YYYY
    """
    try:
        # ניסיון לפרסר תאריך עם שעה
        if ' ' in date_str:
            date_obj = datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d')
        else:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d-%m-%Y')
    except ValueError:
        # אם יש בעיה בפרסור, נחזיר את התאריך כמו שהוא
        return date_str

def get_current_datetime_str():
    """
    מחזיר את התאריך והשעה הנוכחיים כמחרוזת מפורמטת
    
    Returns:
        str: תאריך ושעה במבנה Y-m-d H:M
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M')

def is_positive_number(text):
    """
    בודק אם המחרוזת היא מספר חיובי
    
    Args:
        text: מחרוזת לבדיקה
        
    Returns:
        bool: האם המחרוזת היא מספר חיובי
    """
    try:
        value = float(text)
        return value > 0
    except ValueError:
        return False

def truncate_text(text, max_length=50):
    """
    מקצר טקסט ארוך יותר מאורך מקסימלי
    
    Args:
        text: הטקסט לקיצור
        max_length: אורך מקסימלי
        
    Returns:
        str: הטקסט מקוצר עם "..." אם ארוך מדי
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def sanitize_text(text):
    """
    מסנן תווים בעייתיים מטקסט (למניעת SQL injection והזרקת HTML)
    
    Args:
        text: הטקסט לסינון
        
    Returns:
        str: הטקסט לאחר סינון
    """
    if not text:
        return ""
    
    # הסרת תווים בעייתיים
    blacklist = ['<', '>', ';', '--', '/*', '*/', '@@', '@', '=', '+', "'", '"', '\\']
    result = text
    for char in blacklist:
        result = result.replace(char, '')
    
    return result

def send_error_message(bot, chat_id, error_type="כללית"):
    """
    שולח הודעת שגיאה ידידותית למשתמש
    
    Args:
        bot: מופע הבוט
        chat_id: מזהה הצ'אט
        error_type: סוג השגיאה (כללית, רשת, מסד נתונים)
    """
    error_messages = {
        "כללית": "⚠️ אירעה שגיאה לא צפויה. אנא נסה שוב בעוד כמה רגעים.",
        "רשת": "🌐 בעיית תקשורת. אנא בדוק את החיבור לאינטרנט ונסה שוב.",
        "מסד נתונים": "💾 בעיה בגישה לנתונים. אנא נסה שוב מאוחר יותר.",
        "הרשאות": "🔒 אין לך הרשאה לבצע פעולה זו.",
        "נתונים": "📊 לא נמצאו נתונים להצגה."
    }
    
    message = error_messages.get(error_type, error_messages["כללית"])
    bot.send_message(chat_id, message)

def prevent_duplicate_messages(bot, chat_id, message_text, timeout=2):
    """
    מונע שליחת הודעות כפולות באותו צ'אט
    
    Args:
        bot: מופע הבוט
        chat_id: מזהה הצ'אט
        message_text: תוכן ההודעה
        timeout: זמן המתנה בשניות לפני אפשרות שליחת הודעה דומה
        
    Returns:
        bool: האם ההודעה נשלחה (True) או נחסמה (False)
    """
    # אתחול המערך אם לא קיים
    if not hasattr(bot, 'last_messages'):
        bot.last_messages = {}
    
    current_time = time.time()
    chat_key = str(chat_id)
    
    # בדיקה אם יש הודעה קודמת דומה
    if chat_key in bot.last_messages:
        last_message, last_time = bot.last_messages[chat_key]
        
        # אם ההודעה זהה והזמן קצר מדי - נחסום
        if last_message == message_text and (current_time - last_time) < timeout:
            return False
    
    # שמירת ההודעה הנוכחית
    bot.last_messages[chat_key] = (message_text, current_time)
    return True