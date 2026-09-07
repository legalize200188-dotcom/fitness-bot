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
    raise ValueError("Не установлен BOT_TOKEN")

PROFILE = {
    "gender": "Ж",
    "age": 38,
    "height": 167,
    "weight": 61.6,
    "target_weight": 55.0,
    "experience": "1 месяц",
    "training_days": 4,
    "diet_type": "высокобелковое",
    "calories": 1520,
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


def main_kb():
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text="Тренировка"), KeyboardButton(text="Питание"))
    b.row(KeyboardButton(text="Прогресс"), KeyboardButton(text="Профиль"))
    b.row(KeyboardButton(text="Вода"), KeyboardButton(text="План на неделю"))
    return b.as_markup(resize_keyboard=True)


def workout_kb():
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text="День 1"), KeyboardButton(text="День 2"))
    b.row(KeyboardButton(text="День 3"), KeyboardButton(text="День 4"))
    b.row(KeyboardButton(text="Назад"))
    return b.as_markup(resize_keyboard=True)


def nutrition_kb():
    b = ReplyKeyboardBuilder()
    b.row(KeyboardButton(text="Меню на день"), KeyboardButton(text="Записать еду"))
    b.row(KeyboardButton(text="Белковые идеи"), KeyboardButton(text="Назад"))
    return b.as_markup(resize_keyboard=True)


WORKOUTS = {
    "День 1": (
        "День 1: Ноги + ягодицы + кор\n"
        "70-85 мин\n\n"
        "1. Приседания (штанга/гоблет) — 4x8-10\n"
        "2. Румынская тяга с гантелями — 3x10-12\n"
        "3. Выпады назад с гантелями — 3x10 на ногу\n"
        "4. Ягодичный мост / хип-траст — 4x12-15\n"
        "5. Разгибание ног — 3x12-15\n"
        "6. Сгибание ног лежа — 3x12-15\n"
        "7. Планка — 3x40-60 сек\n"
        "8. Скручивания — 3x15-20\n\n"
        "Отдых 90-120 сек. Последние подходы почти до отказа."
    ),
    "День 2": (
        "День 2: Верх тела\n"
        "65-80 мин\n\n"
        "1. Тяга верхнего блока — 4x10-12\n"
        "2. Жим гантелей лежа — 3x10-12\n"
        "3. Тяга гантели в наклоне — 3x10-12 на руку\n"
        "4. Жим гантелей сидя — 3x10-12\n"
        "5. Разведение в стороны — 3x12-15\n"
        "6. Бицепс с гантелями — 3x12\n"
        "7. Трицепс на блоке — 3x12-15\n"
        "8. Гиперэкстензия легкая — 3x15\n\n"
        "Техника важнее веса. В конце можно 5-7 мин кардио."
