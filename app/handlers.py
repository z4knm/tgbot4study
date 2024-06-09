import pytesseract
import requests
import aiohttp
import sqlite3
from PIL import Image
from io import BytesIO
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink
from bs4 import BeautifulSoup


from datetime import datetime, timedelta

from app.bd import save_to_db, get_db_connection

import app.keyboards as kb

router = Router()

# СОСТОЯНИЕ ДЛЯ ВЫБОРА ГРУППЫ
class GroupDetect(StatesGroup):
    gname = State()

# ВЫЗОВ ОПРЕДЕЛЁННЫХ КЛАВИАТУР
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Здравствуйте! Вы пользуетесь Telegram-ботом, предназначенным для упрощения сбора информации об учебном процессе. Ниже представлена клавиатура с имеющимся функционалом.', reply_markup=kb.start)


@router.message(F.text == 'Полезные ссылки')
async def urls(message: Message):
	await message.answer('Вот полезные ссылки:', reply_markup=kb.urls)

@router.message(F.text == 'Прочие графики')
async def urls(message: Message):
	await message.answer('Вот разные имеющиеся графики:', reply_markup=kb.grphs)

# --- ФУНКЦИИ КЛАВИАТУРЫ ПРОЧИХ ГРАФИКОВ ---
# РАСПИСАНИЕ УЧЕБНЫХ НЕДЕЛЬ
@router.callback_query(F.data == 'uchned')
async def raspuchned(callback: CallbackQuery):
    await callback.answer('Выбрано расписание учебных недель')
    uchned_name = 'расписание учебных недель'
    await callback.message.answer('Вывожу ниже:')
    purl = 'https://pgups-karelia.ru/edu-process/87081/'

    pdf_links = await parse_website(purl, uchned_name)
    if pdf_links:
        for link in pdf_links:
            html_link = f'<a href="{link}">РАСПИСАНИЕ УЧЕБНЫХ НЕДЕЛЬ</a>'
            await callback.message.answer(html_link, parse_mode='HTML')
    else:
        await callback.message.answer("Что-то пошло не так.")

# ГРАФИК ПРОВЕДЕНИЯ КОНСУЛЬТАЦИЙ
@router.callback_query(F.data == 'grkon')
async def raspgrkon(callback: CallbackQuery):
    await callback.answer('Выбран график проведения консультаций')
    grkon_name = 'график проведения консультаций'
    await callback.message.answer('Вывожу ниже:')
    purl = 'https://pgups-karelia.ru/edu-process/87081/'

    pdf_links = await parse_website(purl, grkon_name)

    if pdf_links:
        for link in pdf_links:
            html_link = f'<a href="{link}">ГРАФИК ПРОВЕДЕНИЯ КОНСУЛЬТАЦИЙ</a>'
            await callback.message.answer(html_link, parse_mode='HTML')
    else:
        await callback.message.answer("Что-то пошло не так.")

# РАСПИСАНИЕ ПРОМЕЖУТОЧНОЙ АТТЕСТАЦИИ по состоянию GROUPDETECT
@router.callback_query(F.data == 'rprat')
async def rasprprat(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GroupDetect.gname)
    purl = 'https://pgups-karelia.ru/edu-process/session-ochno-spo/'
    await state.update_data(purl=purl)
    await callback.message.answer('Введите вашу группу:')
    await callback.message.answer('Пожалуйста, используйте кириллицу и поставьте дефис перед номером (Например, БП-101)')


# --- ФУНКЦИЯ ПАРСИНГА по URL на ТЕКСТ по тегам <b> и <strong> ---
async def parse_website(url, srch_wrd):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    soup = BeautifulSoup(html, 'html.parser')
    tagbook = ['strong', 'b']
    pdf_links = []

    for tag in tagbook:
        for elem_tag in soup.find_all(tag):
            if srch_wrd.lower() in elem_tag.get_text().lower():
                parent_a_tag = elem_tag.find_parent('a', href=True)
                if parent_a_tag and parent_a_tag['href']:
                    pdf_links.append(parent_a_tag['href'])
    
    return pdf_links

# ОСНОВНОЕ РАСПИСАНИЕ по GROUPDETECT
@router.message(F.text == 'Расписание')
async def rasping(message: Message, state: FSMContext):
    await state.set_state(GroupDetect.gname)
    purl = 'https://pgups-karelia.ru/edu-process/87081/'
    await state.update_data(purl=purl)
    await message.answer('Введите вашу группу:')
    await message.answer('Пожалуйста, используйте кириллицу и поставьте дефис перед номером (Например, БП-101)')

# --- ФУНКЦИЯ СОСТОЯНИЯ GROUPDETECT ---
@router.message(GroupDetect.gname)
async def group_name(message: Message, state: FSMContext):
    await state.update_data(gname=message.text)
    gdata = await state.get_data()
    gp_name = gdata["gname"]
    purl = gdata["purl"]
    await message.answer(f'Вывожу расписание для группы: {gdata["gname"]}')

    pdf_links = await parse_website(purl, gp_name)

    if pdf_links:
        for link in pdf_links:
            html_link = f'<a href="{link}">ПОСМОТРЕТЬ РАСПИСАНИЕ</a>'
            await message.answer(html_link, parse_mode='HTML')
    else:
        await message.answer("PDF документы не найдены или не содержат указанное название группы.")

    await state.clear()

# РАСПИСАНИЕ ЗВОНКОВ
@router.message(F.text == 'Время звонков')
async def rasptime(message: Message):
    await message.answer('Вывожу ниже:')
    raspt_name = 'Расписание звонков'
    purl = 'https://pgups-karelia.ru/edu-process/87081/'

    pdf_links = await parse_website(purl, raspt_name)

    if pdf_links:
        for link in pdf_links:
            html_link = f'<a href="{link}">РАСПИСАНИЕ ЗВОНКОВ</a>'
            await message.answer(html_link, parse_mode='HTML')
    else:
        await message.answer("Что-то пошло не так.")


# --- ИЗМЕНЕНИЯ НА ЗАВТРАШНИЙ ДЕНЬ ---
# ПОЛУЧЕНИЕ ВСЕХ ПОСТОВ ГРУППЫ по её URL и VK API
def get_vk_posts(group_id, access_token):
    url = f"https://api.vk.com/method/wall.get?owner_id={group_id}&access_token={access_token}&v=5.131"
    response = requests.get(url)
    data = response.json()
    return data['response']['items']

# РАСПОЗНАВАНИЕ ТЕКСТА ФОТО через TESSERACT OCR
def ocr_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(img, lang='rus')
    return text

# ОСНОВНАЯ ФУНКЦИЯ ПОЛУЧЕНИЯ ЗАМЕН НА ЗАВТРА
@router.message(F.text == 'Замены на завтра')
async def send_schedule_changes(message: Message):
    await message.answer("Запрос может занять какое-то время, пожалуйста, подождите...")
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    tomorrow = datetime.today().date() + timedelta(days=1)
    posts = get_vk_posts(group_id='pf_pgups', access_token='f97e0458f97e0458f97e0458cafa668675ff97ef97e04589f2278f838cdffcc34f27000')
    results = []
    for post in posts:
        checkphotopost = False
        for attachment in post.get('attachments', []):
            if attachment['type'] == 'photo':
                photo_url = attachment['photo']['sizes'][-1]['url']
                text = ocr_image(photo_url)
                if f"Изменения в расписании на {tomorrow.strftime('%d')}.{tomorrow.strftime('%m')}.{tomorrow.strftime('%Y')}" in text:
                    checkphotopost = True
        if checkphotopost == True:
            for attachment in post.get('attachments', []):
                if attachment['type'] == 'photo':
                    photo_url = attachment['photo']['sizes'][-1]['url']
                    save_to_db(photo_url)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT image_url FROM schedule_changes WHERE date_added = ?
        ''', (tomorrow,))
        results = cursor.fetchall()
        if results:
            for result in results:
                await message.answer_photo(result[0])
        else:
            await message.reply("Нет изменений в расписании на завтра.")
    except sqlite3.Error as e:
        await message.reply(f"Database error: {e}")
    finally:
        conn.close()