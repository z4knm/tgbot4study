import sqlite3
from datetime import datetime, timedelta

# ПОЛУЧЕНИЕ СОЕДИНЕНИЯ С БД
def get_db_connection():
    print("Получение соединения с базой данных...")
    return sqlite3.connect('bot.db')

# ФУНКЦИЯ СОЗДАНИЯ ТАБЛИЦЫ БД
def create_tables():
    print("Создание таблиц в базе данных, если они не существуют...")
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
    print("Таблицы созданы или уже существуют.")

# СОХРАНЕНИЯ ФОТО В БД
def save_to_db(image_url):
    tomorrow = datetime.today().date() + timedelta(days=1)
    try:
        print("Проверка на существование URL в базе данных...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Проверка на существование URL
        cursor.execute('SELECT 1 FROM schedule_changes WHERE image_url = ?', (image_url,))
        exists = cursor.fetchone()
        
        if exists:
            print("URL уже существует в базе данных.")
            return False

        print("Изменения найдены, сохранение данных в базу...")
        cursor.execute('''
            INSERT INTO schedule_changes (image_url, date_added)
            VALUES (?, ?)
        ''', (image_url, tomorrow))
        conn.commit()
        print("Данные успешно сохранены в базу.")
        return True  # Возвращаем True при успешном выполнении

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        conn.close()
        print("Соединение с базой данных закрыто.")
    return False  # Возвращаем False в случае ошибки

# ОЧИСТКА БД ОТ СТАРЫХ ЗАПИСЕЙ
def clear_old_records():
    two_days_ago = datetime.today().date() - timedelta(days=2)
    try:
        print("Очистка старых записей из базы данных...")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM schedule_changes WHERE date_added < ?', (two_days_ago,))
        conn.commit()
        print("Старые записи успешно удалены.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        conn.close()
        print("Соединение с базой данных закрыто.")


# Создание таблиц при запуске модуля
create_tables()

# Очистка старых записей при запуске модуля
clear_old_records()