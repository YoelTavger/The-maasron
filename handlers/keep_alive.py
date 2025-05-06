import time
import threading
import requests

def setup_keep_alive(app_url=None):
    """
    הגדרת מנגנון שמונע מהשרת להירדם על ידי ביצוע פינג כל 10 דקות.
    
    פרמטרים:
    app_url (str): כתובת URL של האפליקציה (אופציונלי). אם לא מסופק, יבוצע רק לוג.
    """
    
    def keep_alive_job():
        while True:
            try:
                print("[Keep-Alive] מבצע פעולת שמירה על עירנות...")
                
                if app_url:
                    # שליחת בקשת HTTP פשוטה לשרת שלך
                    response = requests.get(app_url)
                    print(f"[Keep-Alive] סטטוס תגובה: {response.status_code}")
                else:
                    # אם לא סופקה כתובת URL, פשוט רושמים לוג
                    print("[Keep-Alive] הפעלת פעולת ping (ללא URL)")
                
            except Exception as e:
                print(f"[Keep-Alive] שגיאה בביצוע פעולת שמירה על עירנות: {str(e)}")
            
            # המתנה של 10 דקות (600 שניות)
            time.sleep(840)
    
    # יצירת thread נפרד שירוץ ברקע
    keep_alive_thread = threading.Thread(target=keep_alive_job, daemon=True)
    keep_alive_thread.start()
    print("[Keep-Alive] מנגנון שמירה על עירנות הופעל בהצלחה")

# אם תרצה להריץ את הקובץ הזה לבדיקה בנפרד, תוכל להשתמש בבלוק הבא:
if __name__ == "__main__":
    print("הפעלת בדיקה עצמאית של מנגנון שמירה על עירנות")
    setup_keep_alive("https://test-app.onrender.com")  # שנה ל-URL שלך לבדיקה
    
    # לשמור את התוכנית רצה כדי שה-thread יוכל להמשיך לפעול
    try:
        while True:
            time.sleep(60)
            print("תוכנית בדיקה עדיין רצה...")
    except KeyboardInterrupt:
        print("בדיקה הופסקה")