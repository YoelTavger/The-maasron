"""
מודול עזר המכיל פונקציות שימושיות לכל הפרויקט
"""

from datetime import datetime

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

def format_currency(amount):
    """
    מפרמט מספר לתצוגת מטבע
    
    Args:
        amount: סכום כספי
    
    Returns:
        str: הסכום מפורמט (לדוגמה: 100.00 ₪)
    """
    return f"{float(amount):.2f} ₪"

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