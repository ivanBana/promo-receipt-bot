import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- НАСТРОЙКИ ---
# Вставь сюда токен бота
BOT_TOKEN = "ТВОЙ_ТОКЕН_ЗДЕСЬ"

# Включаем логирование, чтобы видеть ошибки в консоли
logging.basicConfig(level=logging.INFO)

# --- МАШИНА СОСТОЯНИЙ (FSM) ---
# Определяем этапы анкеты
class CheckRegistration(StatesGroup):
    waiting_for_consent = State() # Согласие с правилами
    waiting_for_photo = State()   # Фото чека
    waiting_for_fio = State()     # ФИО [cite: 1]
    waiting_for_phone = State()   # Телефон [cite: 2]
    waiting_for_email = State()   # Email [cite: 2]

# --- ИНИЦИАЛИЗАЦИЯ ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- ЗАГЛУШКА ДЛЯ GOOGLE SHEETS ---
async def send_to_google_sheets(data):
    """
    Здесь будет вызов функции клиента add_row().
    Пока просто печатаем данные в консоль сервера.
    """
    print("-" * 30)
    print("📝 НОВАЯ ЗАЯВКА ДЛЯ ТАБЛИЦЫ:")
    print(f"User ID: {data['user_id']}")
    print(f"ФИО: {data['fio']}")
    print(f"Телефон: {data['phone']}")
    print(f"Email: {data['email']}")
    print(f"File ID фото: {data['photo_id']}") # 
    print("-" * 30)
    # Эмуляция задержки записи
    await asyncio.sleep(1) 
    return True

# ---ОБРАБОТЧИКИ---

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Начало диалога: Приветствие + Правила """
    await state.clear()
    
    # Кнопка согласия
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✅ Согласен с правилами")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    welcome_text = (
        "👋 Добро пожаловать в акцию «Счастливый чек М7»!\n\n"
        "📋 Правила просты: загрузите чек от 5000₽ и участвуйте в розыгрыше.\n"
        "С полными правилами можно ознакомиться тут: (ссылка)\n\n"
        "Для продолжения подтвердите согласие с обработкой данных."
    )
    await message.answer(welcome_text, reply_markup=kb)
    await state.set_state(CheckRegistration.waiting_for_consent)

@dp.message(CheckRegistration.waiting_for_consent, F.text == "✅ Согласен с правилами")
async def process_consent(message: Message, state: FSMContext):
    """Запрос фото чека """
    await message.answer(
        "Отлично! 📸\n\n"
        "Пожалуйста, отправьте **фотографию чека**.\n"
        "На фото должны быть четко видны: дата, сумма и название магазина.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(CheckRegistration.waiting_for_photo)

@dp.message(CheckRegistration.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Сохраняем ID фото и просим ФИО"""
    # Берем самое большое фото (последнее в списке)
    photo_id = message.photo[-1].file_id
    
    # Сохраняем во временную память 
    await state.update_data(photo_id=photo_id)
    
    await message.answer("Фото принято! 👍\n\nТеперь напишите ваше **ФИО** (как в паспорте).")
    await state.set_state(CheckRegistration.waiting_for_fio)

@dp.message(CheckRegistration.waiting_for_fio)
async def process_fio(message: Message, state: FSMContext):
    """Сохраняем ФИО и просим Телефон"""
    await state.update_data(fio=message.text)
    
    await message.answer("Принято. Укажите ваш **номер телефона** для связи.")
    await state.set_state(CheckRegistration.waiting_for_phone)

@dp.message(CheckRegistration.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Сохраняем Телефон и просим Email"""
    await state.update_data(phone=message.text)
    
    await message.answer("И последнее: ваш **Email** (для отправки электронного купона).")
    await state.set_state(CheckRegistration.waiting_for_email)

@dp.message(CheckRegistration.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    """Финал: Сохраняем всё и отправляем в 'Google Sheets'"""
    # Собираем все накопленные данные
    user_data = await state.get_data()
    final_data = {
        "user_id": message.from_user.id,
        "fio": user_data['fio'],
        "phone": user_data['phone'],
        "email": message.text,
        "photo_id": user_data['photo_id']
    }
    
    msg = await message.answer("⏳ Обрабатываю данные...")
    
    # Заглушка (сюда вставляется функция клиента)
    try:
        await send_to_google_sheets(final_data)
        
        # Ответ пользователю 
        await msg.edit_text(
            "✅ **Ваша заявка принята!**\n\n"
            "Чек отправлен на проверку модератору.\n"
            "Как только мы проверим сумму, вам придет уведомление с купоном.\n\n"
            "Проверить статус можно командой: /status"
        )
    except Exception as e:
        logging.error(f"Ошибка записи: {e}")
        await msg.edit_text("Произошла ошибка при сохранении. Попробуйте позже.")
    
    await state.clear()

# --- ЗАПУСК ---
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
