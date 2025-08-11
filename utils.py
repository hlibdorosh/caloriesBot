import re
from datetime import date
from db import SessionLocal, Parameters, DailyLog


def calculate_daily_calories(weight, height, age, sex, goal):
    if not all([weight, height, age, sex, goal]):
        return None  # если чего-то нет — не считаем

    sex = sex.lower()
    goal = goal.lower()

    if sex == "мужской":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * 1.55

    if goal == "похудение":
        tdee -= 500
    elif goal == "набор":
        tdee += 500

    return round(tdee)




def extract_calories(gpt_response: str) -> int:
    """
    Извлекает количество калорий из строки ответа GPT.
    Пример: "Белки: 24 г\nЖиры: 12 г\nУглеводы: 32 г\nКалории: 540 ккал"
    """
    match = re.search(r"Калории:\s*(\d+)", gpt_response, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0  # если ничего не найдено


def add_calories_with_rollover(telegram_id: int, add_kcal: int):
    session = SessionLocal()
    try:
        user = session.query(Parameters).filter_by(telegram_id=telegram_id).first()
        if not user:
            # если параметров нет — создаём «пустого» пользователя
            user = Parameters(telegram_id=telegram_id, consumed_today=0)
            session.add(user)
            session.flush()

        today = date.today()

        # Если это первый приём вообще
        if not user.last_meal_date:
            user.last_meal_date = today

        # Если день сменился — архивируем вчерашнее
        if user.last_meal_date != today:
            # гарантируем запись за вчера
            yday = user.last_meal_date
            ylog = session.query(DailyLog).filter_by(telegram_id=telegram_id, date=yday).first()
            if not ylog:
                ylog = DailyLog(
                    telegram_id=telegram_id,
                    date=yday,
                    advised_calories=user.daily_calories or 0,
                    consumed_calories=user.consumed_today or 0,
                )
                session.add(ylog)
            else:
                # если запись есть — обновим (на случай повторного запуска)
                ylog.advised_calories = user.daily_calories or 0
                ylog.consumed_calories = user.consumed_today or 0

            # обнуляем «сегодня»
            user.consumed_today = 0
            user.last_meal_date = today

        # Теперь добавляем калории к «сегодня»
        user.consumed_today = (user.consumed_today or 0) + max(0, int(add_kcal))

        # актуализируем запись за сегодня в DailyLog
        tlog = session.query(DailyLog).filter_by(telegram_id=telegram_id, date=today).first()
        if not tlog:
            tlog = DailyLog(
                telegram_id=telegram_id,
                date=today,
                advised_calories=user.daily_calories or 0,
                consumed_calories=user.consumed_today or 0,
            )
            session.add(tlog)
        else:
            tlog.advised_calories = user.daily_calories or 0
            tlog.consumed_calories = user.consumed_today or 0

        session.commit()
    finally:
        session.close()
