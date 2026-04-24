import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


class BotState(StatesGroup):
    waiting_interest = State()
    waiting_name = State()
    q1 = State()
    q2 = State()
    q3 = State()


interest_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Иә, қызық")],
        [KeyboardButton(text="❌ Жоқ")],
    ],
    resize_keyboard=True,
)

q1_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="A) Иә")],
        [KeyboardButton(text="B) Жоқ")],
    ],
    resize_keyboard=True,
)

q2_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="A) 1-2 сағат")],
        [KeyboardButton(text="B) Уақытым аз")],
    ],
    resize_keyboard=True,
)

q3_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="A) Қызық")],
        [KeyboardButton(text="B) Сенімсізбін")],
    ],
    resize_keyboard=True,
)


async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(BotState.waiting_interest)

    await message.answer(
        "Сәлем 👋\n\n"
        "Мен Гүлжанның жеке көмекші ботымын.\n\n"
        "Сіз қосымша табыс табу мүмкіндігін қарастырып жүрсіз бе? 💸\n\n"
        "Қысқа тесттен өтіп, сізге ең тиімді бағытты анықтап берейін 👇",
        reply_markup=interest_kb,
    )


async def interest_handler(message: Message, state: FSMContext):
    text = message.text.strip()

    if text == "✅ Иә, қызық":
        await state.set_state(BotState.waiting_name)
        await message.answer(
            "Керемет 👍\n\n"
            "Алдымен танысып алайық 😊\n"
            "Атыңыз кім?",
            reply_markup=ReplyKeyboardRemove(),
        )

    elif text == "❌ Жоқ":
        await state.clear()
        await message.answer(
            "Жақсы, шешіміңіз өзгерсе, қайта жазыңыз 🌷\n\n"
            "Қайта бастау үшін /start жазыңыз.",
            reply_markup=ReplyKeyboardRemove(),
        )

    else:
        await message.answer(
            "Төмендегі батырмалардың бірін таңдаңыз 👇",
            reply_markup=interest_kb,
        )


async def name_handler(message: Message, state: FSMContext):
    name = message.text.strip()

    await state.update_data(name=name, score=0)
    await state.set_state(BotState.q1)

    await message.answer(
        f"{name}, қуаныштымын 🤝\n\n"
        "Енді 3 қысқа сұраққа жауап беріңіз.\n\n"
        "1-сұрақ:\n"
        "Сізге қосымша табыс керек пе?",
        reply_markup=q1_kb,
    )


async def q1_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    score = data.get("score", 0)

    if text == "A) Иә":
        score += 1
    elif text == "B) Жоқ":
        pass
    else:
        await message.answer("Төмендегі жауаптардың бірін таңдаңыз 👇", reply_markup=q1_kb)
        return

    await state.update_data(score=score)
    await state.set_state(BotState.q2)

    await message.answer(
        "2-сұрақ:\n"
        "Күніне бизнеске уақыт бөле аласыз ба?",
        reply_markup=q2_kb,
    )


async def q2_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    score = data.get("score", 0)

    if text == "A) 1-2 сағат":
        score += 1
    elif text == "B) Уақытым аз":
        pass
    else:
        await message.answer("Төмендегі жауаптардың бірін таңдаңыз 👇", reply_markup=q2_kb)
        return

    await state.update_data(score=score)
    await state.set_state(BotState.q3)

    await message.answer(
        "3-сұрақ:\n"
        "Жаңа бағыт үйренуге қалай қарайсыз?",
        reply_markup=q3_kb,
    )


async def q3_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()

    name = data.get("name", "Белгісіз")
    score = data.get("score", 0)

    if text == "A) Қызық":
        score += 1
    elif text == "B) Сенімсізбін":
        pass
    else:
        await message.answer("Төмендегі жауаптардың бірін таңдаңыз 👇", reply_markup=q3_kb)
        return

    if score >= 2:
        result = (
            "🔥 СІЗДІҢ НӘТИЖЕ:\n\n"
            "Сізге онлайн табыс бағыты өте жақсы сәйкес келеді.\n\n"
            "Сізде қызығушылық бар және бастап көруге потенциал жоғары 💸\n\n"
            "Мен сізге нақты қалай бастау керегін жеке түсіндіріп бере аламын 👇"
        )
    else:
        result = (
            "📊 СІЗДІҢ НӘТИЖЕ:\n\n"
            "Сізге әзірге көбірек ақпарат пен түсіну керек сияқты.\n\n"
            "Дұрыс бағыт таңдасаңыз, жеңіл бастауға болады 👇"
        )

    await message.answer(result, reply_markup=ReplyKeyboardRemove())

    await message.answer(
    "👇 Толық ақпарат алу үшін WhatsApp-қа жазыңыз:\n"
    "https://wa.me/77052304629\n\n"
    "Мен сізге тегін түсіндіріп берем 💬"
)

    user = message.from_user.username if message.from_user.username else "username жоқ"

    if ADMIN_ID:
        await message.bot.send_message(
            ADMIN_ID,
            "🔥 Жаңа лид!\n\n"
            f"Аты: {name}\n"
            f"Username: @{user}\n"
            f"Score: {score}/3"
        )

    await state.clear()


async def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN енгізілмеген")

    logging.basicConfig(level=logging.INFO)

    bot = Bot(TOKEN)
    dp = Dispatcher()

    dp.message.register(start_handler, CommandStart())
    dp.message.register(interest_handler, StateFilter(BotState.waiting_interest))
    dp.message.register(name_handler, StateFilter(BotState.waiting_name))
    dp.message.register(q1_handler, StateFilter(BotState.q1))
    dp.message.register(q2_handler, StateFilter(BotState.q2))
    dp.message.register(q3_handler, StateFilter(BotState.q3))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
