import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message

			# Zdes mi podkluchaemsya k botu
bot = Bot(token='')
			# Zdes mi sozdaem obrabotchik kommand/pomoshnik
dp = Dispatcher()

			# Tut dispetcher, kotoriy mi vveli vishe doljen lovit soobsheniya
@dp.message()
			# Nizhe podskazivaem, chto eto imenno soobshenie - type iz biblioteki aiogram
async def cmd_start(message: Message):
			# Nizhe komanda, kotoraya otvechaet na eto soobshenie
	await message.answer('Privet!')

async def main():
			# Script postoyanno obrashaetsya k serveru telegram i sprashivaet o obnovlenii (prihoda soobsheniya) - v sluchae polozhitelnogo otveta obrashaetsya k dispetcheru dp
	await dp.start_polling(bot)


			# Nizhe opredelyaem tochku vhoda - kod budet vipolnyatsya tolko pri uslovii, chto kod zapushen napryamuiu, t.e ne importirovan
			# Kak ya ponyal, chto esli budem importirovat, to v zapushennom failike etot importirovanniy budet nazivatsya ne main, a nazvaniem faila -> uslovie ne budet proideno
			# Kakim-to obrazom predotvrashaet dvoinoe sozdanie bota
if __name__ == '__main__':
	try:
		asyncio.run(main())
			# Vmesto oshibki prerivaniya bota - v konsoli budet vihodit soobshenie nizhe
	except KeyboardInterrupt:
		print ('Bot off')
