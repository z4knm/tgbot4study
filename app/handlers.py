from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import app.keyboards as kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
	await message.answer('Привет, это главное меню!', reply_markup=kb.start)


@router.message(F.text == 'Полезные ссылки')
async def urls(message: Message):
	await message.answer('Вот полезные ссылки:', reply_markup=kb.urls)

