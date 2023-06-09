import asyncio
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from redis import asyncio as aioredis
from backend.logginger import write_log_files

from headers import Change_of_CEO, \
    Reorganization, Optional_equipment, \
    Prolongation, Common_headers, Insurance_case

bot = Bot(token="6134271801:AAEORCsghLeLGW-GDv0uwB8TMcnK_mMyF_M")
redis = aioredis.Redis.from_url("redis://localhost:6379/3")


# Запуск бота
async def main():
    write_log_files()  # запускает логирование в файл
    dp = Dispatcher(storage=RedisStorage(redis=redis))

    dp.include_router(Reorganization.router)
    dp.include_router(Optional_equipment.router)
    dp.include_router(Change_of_CEO.router)
    dp.include_router(Prolongation.router)
    dp.include_router(Insurance_case.router)
    dp.include_router(Common_headers.router)

    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await dp.storage.close()
    await redis.close()


if __name__ == "__main__":
    asyncio.run(main())

