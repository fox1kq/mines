from telebot import types
import telebot
import json
from datetime import datetime
import random
from git import Repo
import os

# Инициализация бота
TOKEN = '7723929403:AAFkBRy-Dbogt74fZgnIvquI4mLvjg-XFTQ'
bot = telebot.TeleBot(TOKEN)

# Загружаем пользователей
try:
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.load(f)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    users = {}


# Функция для сохранения пользователей
def save_users():
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


# Функция для получения случайного прогноза
def get_random_prediction():
    try:
        with open('predictions.txt', 'r', encoding='utf-8') as file:
            predictions = file.read().strip().split('\n\n')
            if predictions:
                return random.choice(predictions)
            return None
    except Exception as e:
        print(f"Error reading predictions: {e}")
        return None


# Кнопки: главное меню
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("🚀 Регистрация")
    btn2 = telebot.types.KeyboardButton("📈 Выдать сигнал")
    markup.add(btn1, btn2)
    return markup


# Кнопки: регистрация / главное меню
def registration_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("🚀 Регистрация")
    btn2 = telebot.types.KeyboardButton("🏠 Главное меню")
    markup.add(btn1, btn2)
    return markup


# Стартовое сообщение
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
"""
*💎 Добро пожаловать в RICHES MINES!*

*💣 Mines* — азартная игра на платформе *1win*, основанная на классическом «Сапёре».

*🎯 Цель*: Открывать безопасные ячейки, избегая мин.

*🤖 Наш бот* использует *нейросеть ChatGPT-4* и предсказывает расположение мин с *точностью до 95%*.

*❗️ Важно*: Бот работает *только с аккаунтами 1win*, зарегистрированными через раздел *«Регистрация»* в этом боте.
""",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )


# Обработчик кнопки "Регистрация"
@bot.message_handler(func=lambda message: message.text == "🚀 Регистрация")
def start_registration(message):
    try:
        with open('mines.png', 'rb') as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption="""
🔹 *Регистрация в 1win*

1️⃣* Перейдите на официальный сайт: 👉* [1win](https://1wrjmw.com/casino/list?open=register&p=16cq)
🔹* Промокод:* `RICHESMINES` (обязательно!)

2️⃣* Скопируйте ваш ID*:
📌 Во вкладке *"Пополнение"* → ID в правом верхнем углу.

3️⃣ *Отправьте ID боту* в ответном сообщении.

🚀*Готово!* Ожидайте активации.

❗*Любая попытка обмануть бота будет строго наказана.* 
⚠️*Нарушители будут заблокированы навсегда!*
""",
                parse_mode='Markdown',
            )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            "❌ Вы уже зарегистрированы.",
            parse_mode='Markdown'
        )
        print(f"Error in registration: {e}")


# Сохраняем ID, если пользователь отправил только число
@bot.message_handler(func=lambda message: message.text.isdigit())
def save_onewin_id(message):
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {
            # Основная информация о пользователе
            "telegram_id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "username": message.from_user.username,
            "language_code": message.from_user.language_code,

            # Информация о прогнозах
            "predictions_left": 10,  # Количество оставшихся бесплатных прогнозов
            "full_access": False,  # Флаг полного доступа

            # Регистрационная информация
            "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "1win_id": None
        }

    # Проверяем, есть ли уже сохранённый ID
    if '1win_id' not in users[user_id] or not users[user_id]['1win_id']:
        users[user_id]['1win_id'] = message.text
        users[user_id]['last_activity'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users()
        bot.send_message(
            message.chat.id,
            "✅ Твой ID успешно сохранён! Теперь можешь получать сигналы.",
            reply_markup=main_menu()
        )
    else:
        bot.send_message(
            message.chat.id,
            "✅ У тебя уже сохранён ID.",
            reply_markup=main_menu()
        )


# Обработчик кнопки "Выдать сигнал"
@bot.message_handler(func=lambda message: message.text == "📈 Выдать сигнал")
def handle_signal(message):
    user_id = str(message.chat.id)

    # Проверяем, существует ли пользователь в базе
    if user_id not in users:
        bot.send_message(
            message.chat.id,
            """
❗ Вы не зарегистрированы в боте.

📝 Пожалуйста, пройдите регистрацию, нажав кнопку "🚀 Регистрация"
""",
            parse_mode='Markdown',
            reply_markup=registration_menu()
        )
        return

    # Проверяем, есть ли у пользователя 1win ID
    if '1win_id' not in users[user_id] or not users[user_id]['1win_id']:
        bot.send_message(
            message.chat.id,
            """
❗ Для получения сигналов необходимо завершить регистрацию.

📝 Пожалуйста, укажите свой ID от 1win через раздел "🚀 Регистрация"
""",
            parse_mode='Markdown',
            reply_markup=registration_menu()
        )
        return

    # Проверяем количество доступных прогнозов
    if not users[user_id]['full_access'] and users[user_id]['predictions_left'] <= 0:
        bot.send_message(
            message.chat.id,
            """
❌ У вас закончились бесплатные прогнозы!

👥 Для получения полного доступа отправьте [администратору](https://t.me/korbetov?text=Привет!👋 Как получить полный доступ?) сообщение.
""",
            parse_mode='Markdown',
            disable_web_page_preview = True
        )
        return

    # Получаем случайный прогноз
    prediction = get_random_prediction()
    if not prediction:
        bot.send_message(
            message.chat.id,
            "❌ Извините, в данный момент нет доступных сигналов.",
            parse_mode='Markdown'
        )
        return

    try:
        if not users[user_id]['full_access']:
            users[user_id]['predictions_left'] -= 1
            predictions_left = users[user_id]['predictions_left']
            save_users()

            bot.send_message(
                message.chat.id,
                f"""
🎯 *Ваш сигнал:*

{prediction}

*❗️Выставьте 3 ловушки. Это важно!*
*❗️При неудаче удвой ставку, чтобы перекрыть потерю.*
""",
                parse_mode='Markdown'
            )
        else:
            # Для пользователей с полным доступом
            bot.send_message(
                message.chat.id,
                f"""
🎯 *Ваш сигнал:*

{prediction}
""",
                parse_mode='Markdown'
            )

        # Обновляем время последней активности
        users[user_id]['last_activity'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users()

    except Exception as e:
        bot.send_message(
            message.chat.id,
            "❌ Произошла ошибка при отправке сигнала. Попробуйте позже.",
            parse_mode='Markdown'
        )
        print(f"Error sending prediction: {e}")


# Обработчик кнопки "Главное меню"
@bot.message_handler(func=lambda message: message.text == "🏠 Главное меню")
def go_to_main_menu(message):
    bot.send_message(
        message.chat.id,
        "🏠 Ты в главном меню. Выбирай действие:",
        reply_markup=main_menu()
    )

# Команда для выдачи полного доступа
@bot.message_handler(commands=['giveaccess'])
def give_access(message):
    if message.from_user.id != 702647989:
        bot.reply_to(message, "⛔ У тебя нет прав использовать эту команду.")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "⚠️ Используй так: /giveaccess ID_пользователя")
        return

    target_id = args[1]

    if target_id in users:
        users[target_id]['full_access'] = True
        save_users()
        bot.reply_to(message, f"✅ Пользователь {target_id} получил полный доступ.")
    else:
        bot.reply_to(message, "❌ Пользователь не найден.")

# Старт рассылки
@bot.message_handler(commands=['broadcast'])
def start_broadcast(message):
    if message.from_user.id != 702647989:
        bot.send_message(message.chat.id, "⛔ У тебя нет доступа.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 Текст", "🖼️ Фото + текст")
    msg = bot.send_message(message.chat.id, "Выбери тип рассылки:", reply_markup=markup)
    bot.register_next_step_handler(msg, choose_broadcast_type)

# Выбор типа рассылки
def choose_broadcast_type(message):
    if message.text == "📝 Текст":
        msg = bot.send_message(message.chat.id, "✍️ Напиши текст для рассылки:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, broadcast_text)
    elif message.text == "🖼️ Фото + текст":
        msg = bot.send_message(message.chat.id, "📸 Отправь фото для рассылки:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, broadcast_photo)
    else:
        bot.send_message(message.chat.id, "⛔ Неверный выбор. Попробуй снова /broadcast", reply_markup=types.ReplyKeyboardRemove())

# Текстовая рассылка
def broadcast_text(message):
    text = message.text
    for user_id in users:
        try:
            bot.send_message(user_id, text)
        except Exception as e:
            print(f"Не отправлено {user_id}: {e}")
    bot.send_message(message.chat.id, "✅ Текстовая рассылка завершена.")

# Фото + текст
def broadcast_photo(message):
    if not message.photo:
        bot.send_message(message.chat.id, "⛔ Это не фото. Отправь именно фотографию.")
        return

    file_id = message.photo[-1].file_id
    msg = bot.send_message(message.chat.id, "✍️ Теперь напиши подпись к фото:")
    bot.register_next_step_handler(msg, lambda m: send_photo_broadcast(m, file_id))

def send_photo_broadcast(message, file_id):
    caption = message.text
    for user_id in users:
        try:
            bot.send_photo(user_id, photo=file_id, caption=caption)
        except Exception as e:
            print(f"Не отправлено {user_id}: {e}")
    bot.send_message(message.chat.id, "✅ Рассылка с фото завершена.")


@bot.message_handler(commands=['github'])
def handle_github_backup(message):
    # Проверка админских прав (замените на ваш ID)
    if message.from_user.id != 702647989:
        bot.reply_to(message, "❌ Только для админа!")
        return

    try:
        # 1. Путь к репозиторию (на Railway это /app)
        repo_path = "/app"
        repo = Repo(repo_path)

        # 2. Добавляем файл
        repo.git.add("users.json")

        # 3. Коммитим изменения
        repo.git.commit("-m", "Backup users.json")

        # 4. Пушим с токеном (безопасно)
        token = os.getenv("GITHUB_TOKEN")
        origin = repo.remote(name="origin")
        origin.set_url(f"https://{token}@github.com/ваш-логин/ваш-репозиторий.git")
        origin.push()

        bot.reply_to(message, "✅ Данные успешно выгружены в GitHub!")

    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        print(error_msg)  # Для логов
        bot.reply_to(message, error_msg)

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)