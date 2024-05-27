import requests
import aiohttp
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bs4 import BeautifulSoup

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

# ----------------------------------------- Функция парсинга оф. сайта на странице с расписаниями

async def parse_website():
    url = 'https://pgups-karelia.ru/edu-process/87081/'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)

    pdf_links = [link['href'] for link in links if link['href'].endswith('.pdf')]
    
    return pdf_links

# -------------------------------------------

@router.message(F.text == 'Расписание')
async def rasping(message: Message, state: FSMContext):
    await state.set_state(GroupDetect.gname)
    await message.answer('Введите вашу группу через дефис:')

@router.message(GroupDetect.gname)
async def group_name(message: Message, state: FSMContext):
    await state.update_data(gname=message.text)
    gdata = await state.get_data()
    gp_name = gdata["gname"]
    await message.answer(f'Расписание для группы: {gdata["gname"]}')

    pdf_links = await parse_website()
    found_links = [link for link in pdf_links if gp_name.lower() in link.lower()]

    if found_links:
        for link in found_links:
            await message.answer(link)
    else:
        await message.answer("PDF документы не найдены или не содержат указанное название группы.")

    await state.clear()
