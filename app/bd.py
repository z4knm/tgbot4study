import sqlite3
from datetime import datetime, timedelta

# ПОЛУЧЕНИЕ СОЕДИНЕНИЯ С БД
def get_db_connection():
    return sqlite3.connect('bot.db')

# ФУНКЦИЯ СОЗДАНИЯ ТАБЛИЦЫ БД
def create_tables():
    print("[bot4study] Создание таблиц в базе данных, если они не существуют...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule_changes (
            id INTEGER PRIMARY KEY,
            image_url TEXT,
            date_added DATE
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_date_added
        ON schedule_changes (date_added)
    ''')
    conn.commit()
    conn.close()
    print("[bot4study] Таблицы созданы или уже существуют.")

# СОХРАНЕНИЯ ФОТО В БД
def save_to_db(image_url):
    tomorrow = datetime.today().date() + timedelta(days=1)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Проверка на существование URL
        cursor.execute('SELECT 1 FROM schedule_changes WHERE image_url = ?', (image_url,))
        exists = cursor.fetchone()
        
        if exists:
            return False

        print("[bot4study] Изменения найдены, сохранение данных в базу...")
        cursor.execute('''
            INSERT INTO schedule_changes (image_url, date_added)
            VALUES (?, ?)
        ''', (image_url, tomorrow))
        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        conn.close()
    return False

# ОЧИСТКА БД ОТ СТАРЫХ ЗАПИСЕЙ
def clear_old_records():
    two_days_ago = datetime.today().date() - timedelta(days=2)
    try:
        print("[bot4study] Очистка старых записей из базы данных...")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM schedule_changes WHERE date_added < ?', (two_days_ago,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        conn.close()


# Создание таблиц при запуске модуля
create_tables()

# Очистка старых записей при запуске модуля
clear_old_records()