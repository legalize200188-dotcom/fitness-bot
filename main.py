import asyncio
import json
import os
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

PROFILE = {
    "age": 38,
    "height": 167,
    "weight": 61.6,
    "target": 55.0,
    "kcal": 1520,
    "protein": 120,
    "fat": 48,
    "carbs": 145,
}

DATA_FILE = "user_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"weight_log": [], "workout_log": [], "food_log": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


user_data = load_data()


class Form(StatesGroup):
    waiting_food = State()


def kb(rows):
    b = ReplyKeyboardBuilder()
    for row in rows:
        b.row(*[KeyboardButton(text=x) for x in row])
    return b.as_markup(resize_keyboard=True)


MAIN = kb([["Тренировка", "Питание"], ["Прогресс", "Профиль"], ["Вода", "План на неделю"]])
WKB = kb([["День 1", "День 2"], ["День 3", "День 4"], ["Назад"]])
NKB = kb([["Меню на день", "Записать еду"], ["Белковые идеи", "Назад"]])

W1 = "День 1: ноги + ягодицы + кор, 70-85 мин\n1. Приседания 4x8-10\n2. Румынская тяга 3x10-12\n3. Выпады назад 3x10\n4. Ягодичный мост 4x12-15\n5. Разгибание ног 3x12-15\n6. Сгибание ног 3x12-15\n7. Планка 3x40-60 сек\n8. Скручивания 3x15-20"
W2 = "День 2: верх, 65-80 мин\n1. Тяга верхнего блока 4x10-12\n2. Жим гантелей лежа 3x10-12\n3. Тяга гантели 3x10-12\n4. Жим сидя 3x10-12\n5. Разведения 3x12-15\n6. Бицепс 3x12\n7. Трицепс 3x12-15\n8. Гиперэкстензия 3x15"
W3 = "День 3: ноги + кардио, 75-90 мин\n1. Жим ногами 4x12-15\n2. Болгарские выпады 3x10-12\n3. Мост на одной ноге 3x12\n4. Goblet 3x12\n5. Отведение ноги 3x15\n6. Икры 4x15-20\n7. Кардио 15-20 мин"
W4 = "День 4: full body, 70-85 мин\n1. Румынская тяга 3x8-10\n2. Жим гантелей 3x10\n3. Тяга или гравитрон 3x8-12\n4. Выпады 3x10\n5. Отжимания 3xmax\n6. Планка 3x30-40 сек\n7. Фермерская прогулка 3x30-40 м"

WORKOUTS = {"День 1": W1, "День 2": W2, "День 3": W3, "День 4": W4}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def start(message: types.Message):
    p = PROFILE
    await message.answer(
        "Привет! Я твой бот по тренировкам и питанию.\nЦель: "
        + str(p["weight"])
        + " -> "
        + str(p["target"])
        + " кг\nКалории: "
        + str(p["kcal"])
        + "\nБелок: "
        + str(p["protein"])
        + " г",
        reply_markup=MAIN,
    )


@dp.message(F.text == "Назад")
async def back(message: types.Message):
    await message.answer("Главное меню", reply_markup=MAIN)


@dp.message(F.text == "Профиль")
async def profile(message: types.Message):
    p = PROFILE
    await message.answer(
        "Женщина, 38 лет, 167 см\nВес "
        + str(p["weight"])
        + " кг, цель "
        + str(p["target"])
        + " кг\nЗал 4 раза в неделю\nВысокобелковое питание\n"
        + str(p["kcal"])
        + " ккал, белок "
        + str(p["protein"])
        + " г",
        reply_markup=MAIN,
    )


@dp.message(F.text == "Тренировка")
async def wmenu(message: types.Message):
    await message.answer("Выбери день", reply_markup=WKB)


@dp.message(F.text.in_(list(WORKOUTS.keys())))
async def wshow(message: types.Message):
    await message.answer(WORKOUTS[message.text] + "\n\nПосле тренировки напиши: готово", reply_markup=WKB)


@dp.message(F.text == "План на неделю")
async def week(message: types.Message):
    await message.answer("Пн День 1\nВт День 2\nСр отдых\nЧт День 3\nПт День 4\nСб-Вс отдых", reply_markup=MAIN)


@dp.message(F.text == "Питание")
async def nutr(message: types.Message):
    await message.answer("Раздел питания", reply_markup=NKB)


@dp.message(F.text == "Меню на день")
async def menu(message: types.Message):
    await message.answer(
        "Ориентир 1520 ккал\nЗавтрак: овсянка 40г + протеин + ягоды\nПерекус: творог 150г\nОбед: грудка 150г + крупа 60г + салат\nПерекус: протеин или тунец\nУжин: рыба + овощи",
        reply_markup=NKB,
    )


@dp.message(F.text == "Белковые идеи")
async def ideas(message: types.Message):
    await message.answer("Курица, творог, яичные белки, тунец, протеин, йогурт, креветки, нежирная говядина", reply_markup=NKB)


@dp.message(F.text == "Прогресс")
async def progress(message: types.Message):
    weights = user_data.get("weight_log", [])
    workouts = user_data.get("workout_log", [])
    text = "Прогресс\n"
    if weights:
        for e in weights[-7:]:
            text += e["date"] + ": " + str(e["weight"]) + " кг\n"
    else:
        text += "Напиши: вес 60.8\n"
    text += "Тренировок: " + str(len(workouts))
    await message.answer(text, reply_markup=MAIN)


@dp.message(F.text == "Вода")
async def water(message: types.Message):
    await message.answer("Вода 2.3-2.8 л в день", reply_markup=MAIN)


@dp.message(F.text.regexp(r"(?i)вес\s+(\d+[.,]?\d*)"))
async def log_weight(message: types.Message):
    m = re.search(r"(\d+[.,]?\d*)", message.text)
    weight = float(m.group(1).replace(",", "."))
    user_data.setdefault("weight_log", []).append({"date": datetime.now().strftime("%d.%m.%Y"), "weight": weight})
    save_data(user_data)
    await message.answer("Вес " + str(weight) + " кг записан", reply_markup=MAIN)


@dp.message(F.text.regexp(r"(?i)готово|сделала"))
async def log_workout(message: types.Message):
    user_data.setdefault("workout_log", []).append({"date": datetime.now().strftime("%d.%m.%Y %H:%M")})
    save_data(user_data)
    await message.answer("Тренировка записана", reply_markup=MAIN)


@dp.message(F.text == "Записать еду")
async def food_start(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_food)
    await message.answer("Напиши, что съела")


@dp.message(Form.waiting_food)
async def food_save(message: types.Message, state: FSMContext):
    user_data.setdefault("food_log", []).append({"date": datetime.now().strftime("%d.%m.%Y %H:%M"), "text": message.text})
    save_data(user_data)
    await state.clear()
    await message.answer("Записала", reply_markup=NKB)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
