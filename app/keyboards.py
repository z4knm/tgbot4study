from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton 

start = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Замены на завтра')],
									[KeyboardButton(text='Время звонков')],
									[KeyboardButton(text='Расписание')],
									[KeyboardButton(text='Полезные ссылки')]],
									input_field_placeholder='Выберите пункт меню...')

urls = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Официальный Сайт', url='https://pgups-karelia.ru')],
											[InlineKeyboardButton(text='Группа ВКонтакте', url='https://vk.com/pf_pgups')],
											[InlineKeyboardButton(text='Moodle', url='http://212.109.2.247/login/index.php')]
											])