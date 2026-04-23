import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

class TestState(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()

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
    await state.update_data(score=0)
    await state.set_state(TestState.q1)

    await message.answer(
        "Сәлем 👋\n\n"
        "Қысқа тесттен өтіп, сізге қай бағыт қолайлы екенін анықтайық.\n\n"
        "1-сұрақ:\n"
        "Сізге қосымша табыс керек пе?",
        reply_markup=q1_kb
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
        await message.answer(f"Сіз басқан жауап: {text}")
        await message.answer("Төмендегі жауаптардың бірін таңдаңыз 👇", reply_markup=q1_kb)
        return

    await state.update_data(score=score)
    await state.set_state(TestState.q2)

    await message.answer(
        "2-сұрақ:\n"
        "Күніне бизнеске уақыт бөле аласыз ба?",
        reply_markup=q2_kb
    )

async def q2_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    score = data.get("score", 0)

    if text == "A) 1-2 сағат":
        score += 1
    elif text != "B) Уақытым аз":
        await message.answer("Төмендегі жауаптардың бірін таңдаңыз 👇", reply_markup=q2_kb)
        return

    await state.update_data(score=score)
    await state.set_state(TestState.q3)

    await message.answer(
        "3-сұрақ:\n"
        "Жаңа бағыт үйренуге қалай қарайсыз?",
        reply_markup=q3_kb
    )

async def q3_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    score = data.get("score", 0)

    if text == "A) Қызық":
        score += 1
    elif text != "B) Сенімсізбін":
        await message.answer("Төмендегі жауаптардың бірін таңдаңыз 👇", reply_markup=q3_kb)
        return

    # НӘТИЖЕ
    if score >= 2:
        result = (
            "🔥 СІЗДІҢ НӘТИЖЕ:\n\n"
            "Сізге онлайн табыс бағыты өте жақсы сәйкес келеді.\n\n"
            "Қазір бастасаңыз, 7-14 күн ішінде алғашқы нәтижелер көруге болады 💸\n\n"
            "Мен сізге нақты қалай бастау керегін жеке түсіндіріп бере аламын 👇"
        )
    else:
        result = (
            "📊 СІЗДІҢ НӘТИЖЕ:\n\n"
            "Сізде потенциал бар, бірақ бағытты дұрыс таңдау маңызды.\n\n"
            "Мен сізге ең жеңіл бастау жолын көрсетіп бере аламын 👇"
        )

    await message.answer(result)

    # CTA (жаздыру)
    await message.answer(
        "👇 Толық ақпарат алу үшін жазыңыз:\n"
        "@guljan_username\n\n"
        "Мен сізге тегін жоспар жасап берем 💬"
    )

    # URGENCY
    await message.answer(
        "⚠️ Қазір тек 10 адамға ғана жеке көмектесіп жатырмын.\n"
        "Егер қызық болса — кеш болмай тұрғанда жазыңыз 👇\n\n"
        "@guljan_username"
    )

    # ЛИД САҒАН КЕЛЕДІ
    user = message.from_user.username if message.from_user.username else "жоқ"

    if ADMIN_ID:
        await message.bot.send_message(
            ADMIN_ID,
            f"🔥 Жаңа лид!\n\nUser: @{user}\nScore: {score}/3"
        )

    await state.clear())

async def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN енгізілмеген")

    logging.basicConfig(level=logging.INFO)

    bot = Bot(TOKEN)
    dp = Dispatcher()

    dp.message.register(start_handler, CommandStart())
    dp.message.register(q1_handler, StateFilter(TestState.q1))
    dp.message.register(q2_handler, StateFilter(TestState.q2))
    dp.message.register(q3_handler, StateFilter(TestState.q3))

    await dp.start_polling(bot)
    
    await message.bot.send_message(
        ADMIN_ID,
        f"Жаңа лид:\n@{user}\nScore: {score}"
)    

if __name__ == "__main__":
    asyncio.run(main())
