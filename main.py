from telebot import types

import telebot
import json
from datetime import datetime
import random

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
    if message.from_user.id != 702647989:  # Замените на ваш ID
        bot.send_message(message.chat.id, "⛔ У вас нет прав на эту команду")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton("📝 Текст")
    btn2 = types.KeyboardButton("🖼️ Фото + текст")
    btn3 = types.KeyboardButton("❌ Отмена")
    markup.add(btn1, btn2, btn3)

    msg = bot.send_message(
        message.chat.id,
        "Выберите тип рассылки:",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_broadcast_type)


def process_broadcast_type(message):
    try:
        if message.text == "❌ Отмена":
            bot.send_message(
                message.chat.id,
                "Рассылка отменена",
                reply_markup=main_menu()
            )
            return

        elif message.text == "📝 Текст":
            msg = bot.send_message(
                message.chat.id,
                "Введите текст для рассылки:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(msg, send_text_broadcast)

        elif message.text == "🖼️ Фото + текст":
            msg = bot.send_message(
                message.chat.id,
                "Отправьте фото для рассылки:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(msg, process_photo_for_broadcast)

        else:
            bot.send_message(
                message.chat.id,
                "Неверный выбор. Попробуйте снова /broadcast",
                reply_markup=main_menu()
            )
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")
        print(f"Broadcast error: {e}")


def process_photo_for_broadcast(message):
    try:
        if not message.photo:
            bot.send_message(
                message.chat.id,
                "Это не фото. Отправьте изображение.",
                reply_markup=main_menu()
            )
            return

        # Сохраняем file_id последнего (самого большого) фото
        file_id = message.photo[-1].file_id

        msg = bot.send_message(
            message.chat.id,
            "Теперь введите текст подписи к фото:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(msg, lambda m: send_photo_broadcast(m, file_id))

    except Exception as e:
        bot.reply_to(message, f"Ошибка обработки фото: {str(e)}")
        print(f"Photo process error: {e}")


def send_text_broadcast(message):
    try:
        text = message.text
        success = 0
        errors = 0

        for user_id in users:
            try:
                bot.send_message(user_id, text)
                success += 1
            except Exception as e:
                errors += 1
                print(f"Не отправлено {user_id}: {e}")

        report = (
            f"📊 Отчёт о рассылке:\n"
            f"✅ Успешно: {success}\n"
            f"❌ Ошибок: {errors}\n"
            f"📝 Текст: {text[:100]}..."
        )
        bot.send_message(
            message.chat.id,
            report,
            reply_markup=main_menu()
        )
    except Exception as e:
        bot.reply_to(message, f"Ошибка рассылки: {str(e)}")
        print(f"Text broadcast error: {e}")


def send_photo_broadcast(message, file_id):
    try:
        caption = message.text
        success = 0
        errors = 0

        for user_id in users:
            try:
                bot.send_photo(
                    user_id,
                    photo=file_id,
                    caption=caption
                )
                success += 1
            except Exception as e:
                errors += 1
                print(f"Не отправлено {user_id}: {e}")

        report = (
            f"📊 Отчёт о рассылке:\n"
            f"✅ Успешно: {success}\n"
            f"❌ Ошибок: {errors}\n"
            f"📸 Фото + текст: {caption[:100]}..."
        )
        bot.send_message(
            message.chat.id,
            report,
            reply_markup=main_menu()
        )
    except Exception as e:
        bot.reply_to(message, f"Ошибка рассылки: {str(e)}")
        print(f"Photo broadcast error: {e}")


def push_to_github():
    try:
        repo = Repo("/app")  # Или укажите полный путь к папке с репозиторием
        repo.git.add("users.json")
        repo.git.commit("-m", "Manual update users.json")
        origin = repo.remote(name="origin")
        origin.push()
        return True
    except Exception as e:
        print(f"Git push error: {e}")
        return False

    # Добавьте эту команду для админов


@bot.message_handler(commands=['gitpush'])
def handle_gitpush(message):
    if message.from_user.id != 702647989:  # Ваш ID
        bot.reply_to(message, "⛔ У вас нет прав на эту команду")
        return

    bot.reply_to(message, "🔄 Начинаю выгрузку users.json в GitHub...")

    try:
        # Убедимся, что файл существует
        if not os.path.exists("/app/users.json"):
            raise FileNotFoundError("Файл users.json не найден")

        # Устанавливаем Git конфигурацию
        subprocess.run(["git", "config", "--global", "user.name", os.getenv('GIT_USERNAME', 'github-actions')],
                       check=True)
        subprocess.run(["git", "config", "--global", "user.email", os.getenv('GIT_EMAIL', 'actions@github.com')],
                       check=True)

        # Добавляем изменения
        subprocess.run(["git", "add", "users.json"], check=True)

        # Коммитим
        subprocess.run(["git", "commit", "-m", "Auto-update users.json"], check=True)

        # Пушим с использованием токена
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN не установлен")

        repo_url = f"https://{github_token}@github.com/ваш-username/ваш-репозиторий.git"
        subprocess.run(["git", "push", repo_url, "HEAD:main"], check=True)

        bot.reply_to(message, "✅ Файл успешно выгружен в GitHub!")

    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        print(error_msg)
        bot.reply_to(message, error_msg)

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)