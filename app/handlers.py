import requests
import aiohttp
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

import app.keyboards as kb

router = Router()


class GroupDetect(StatesGroup):
    gname = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
	await message.answer('Привет, это главное меню!', reply_markup=kb.start)


@router.message(F.text == 'Полезные ссылки')
async def urls(message: Message):
	await message.answer('Вот полезные ссылки:', reply_markup=kb.urls)

@router.message(F.text == 'Прочие графики')
async def urls(message: Message):
	await message.answer('Вот разные имеющиеся графики:', reply_markup=kb.grphs)

# ----------------------------------------- Функции по прочим графикам

# -------- Расписание учебных недель
@router.callback_query(F.data == 'uchned')
async def raspuchned(callback: CallbackQuery):
    await callback.answer('Выбрано расписание учебных недель')
    uchned_name = 'расписание учебных недель'
    await callback.message.answer('Расписание учебных недель:')
    purl = 'https://pgups-karelia.ru/edu-process/87081/'

    pdf_links = await parse_website(purl, uchned_name)
    # ПРИДУМАТЬ КАК ОТПРАВЛЯТЬ ЦЕЛЬНЫЕ ССЫЛКИ С ПРОБЕЛАМИ, А ПОТОМ НА ОСНОВАНИИ ЭТОГО ДОПИЛИТЬ 2 НИЖНИЕ ФУНКЦИИ
    if pdf_links:
        for link in pdf_links:
            encoded_link = quote(link)
            await callback.message.answer(encoded_link)
    else:
        await callback.message.answer("Что-то пошло не так.")


# -------- График проведения консультаций 
@router.callback_query(F.data == 'grkon')
async def raspgrkon(callback: CallbackQuery):
    await callback.answer('Выбран график проведения консультаций')
    grkon_name = 'график проведения консультаций'
    await callback.message.answer('График проведения консультаций:')
    purl = 'https://pgups-karelia.ru/edu-process/87081/'

    pdf_links = await parse_website(purl, grkon_name)

    if pdf_links:
        for link in pdf_links:
            await callback.message.answer(link)
    else:
        await callback.message.answer("Что-то пошло не так.")

# -------- Расписание ПРОМЕЖУТОЧНОЙ АТТЕСТАЦИИ через состояние GroupDetect
@router.callback_query(F.data == 'rprat')
async def rasprprat(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GroupDetect.gname)
    purl = 'https://pgups-karelia.ru/edu-process/session-ochno-spo/'
    await state.update_data(purl=purl)
    await callback.message.answer('Введите вашу группу через дефис:')


# ------------------------------------------ Функция ПАРСИНГА {url} на наличие {слова} по выбранному тегу

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
                if parent_a_tag and parent_a_tag['href'].endswith('.pdf'):
                    pdf_links.append(parent_a_tag['href'])
    
    return pdf_links

# ------------------------------------------ Функция выдачи ОСНОВНОГО РАСПИСАНИЯ через состояние GroupDetect по тегу <strong>

@router.message(F.text == 'Расписание')
async def rasping(message: Message, state: FSMContext):
    await state.set_state(GroupDetect.gname)
    purl = 'https://pgups-karelia.ru/edu-process/87081/'
    await state.update_data(purl=purl)
    await message.answer('Введите вашу группу через дефис:')

# ------------------------------------------ Состояние GroupDetect по парсингу {url} на наличие заголовка группы по выбранному тегу

@router.message(GroupDetect.gname)
async def group_name(message: Message, state: FSMContext):
    await state.update_data(gname=message.text)
    gdata = await state.get_data()
    gp_name = gdata["gname"]
    purl = gdata["purl"]
    await message.answer(f'Расписание для группы: {gdata["gname"]}')

    pdf_links = await parse_website(purl, gp_name)

    if pdf_links:
        for link in pdf_links:
            await message.answer(link)
    else:
        await message.answer("PDF документы не найдены или не содержат указанное название группы.")

    await state.clear()

# ------------------------------------------ Функция выдачи расписания ЗВОНКОВ

@router.message(F.text == 'Время звонков')
async def rasptime(message: Message):
    await message.answer('Вывожу расписание звонков:')
    purl = 'https://pgups-karelia.ru/edu-process/87081/'
