import logging
import requests

from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

import matplotlib.pyplot as plt

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

reply_keyboard = [['USD'],
                  ['EUR'],
                  ['RUB'],
                  ['CNY'],
                  ['CHF'],
                  ['JPY'],
                  ['SEK'],
                  ['CAD'],
                  ['AUD']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

currencies = []
date_for_old_currency = ''
dates_for_graph_currency = []


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот, отслеживающий курсы валют, таких как российский рубль, "
        "доллар США, евро, юань, иена, шведская крона, швейцарский франк, канадский доллар, "
        "австралийский доллар. Введите команду /help, чтобы посмотреть все возможные команды, предоставляемые ботом",
    )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("""Команды:
/start - начало работы бота
/help - показывает список всех команд
/currency - предлагает пользователю посмотреть нынешние курсы валют, которых пользователь выбирает сам
/stop_currency - прекращает работу команды /currency
/old_currency (date) - предлагает пользователю посмотреть старые курсы валют, которые были в указанной дате
/stop_old_currency - прекращает работу команды old_currency
/graph_currency (start_date, end_date) - отправляет график изменения курса выбранных валют
/stop_graph_currency - прекращает работу команды /graph_currency
/info - предлагает пользователю просмотреть подробную информацию про ту или иную валюту
/stop_info - прекращает работу команды /info""")


async def currency(update, context):
    """Дает возможность выбора пары валюты для того, чтобы узнать курс валют"""
    await update.message.reply_text(
        "Выберите валюту, взятую за единицу",
        reply_markup=markup
    )
    return 1


async def rate1(update, context):
    """Дает возможность выбрать валюты"""
    global currencies
    cur = update.message.text
    currencies.append(cur)
    await update.message.reply_text(
        "Выберите вторую валюту",
        reply_markup=markup
    )
    return 2


async def rate2(update, context):
    """Отправляет курс выбранных валют"""
    global currencies
    cur = update.message.text
    currencies.append(cur)
    url = f"https://api.apilayer.com/currency_data/live?source={currencies[0]}&currencies={','.join(currencies)}"
    payload = {}
    headers = {
        "apikey": api
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response:
        json_form = response.json()
        await update.message.reply_text(f"""1 {currencies[0]} = {json_form["quotes"][''.join(currencies)]} {currencies[1]}. 
        \n \n Если вы хотите узнать курсы других валют, воспользуйтесь командой /currency""",
                                        reply_markup=ReplyKeyboardRemove())
        currencies.clear()
        return ConversationHandler.END


async def stop_currency(update, context):
    """Останавливает работу функции /currency"""
    await update.message.reply_text("""Если вы хотите узнать курсы других валют, воспользуйтесь командой /currency""",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def old_currency(update, context):
    """Дает возможность выбора пары валюты для того, чтобы узнать курс валют в прошлом"""
    await update.message.reply_text(
        "Введите дату в формате YYYY-MM-DD"
    )
    return 1


async def date(update, context):
    """Дает возможность ввести дату, если пользователь хочет узнать курсы валют в прошлом"""
    global date_for_old_currency
    date_for_old_currency = update.message.text
    await update.message.reply_text(
        "Выберите валюту, взятую за единицу",
        reply_markup=markup
    )
    return 2


async def old_rate1(update, context):
    """Дает возможность выбрать валюты"""
    global currencies
    cur = update.message.text
    currencies.append(cur)
    await update.message.reply_text(
        "Выберите вторую валюту",
        reply_markup=markup
    )
    return 3


async def old_rate2(update, context):
    """Отправляет курс выбранных валют в прошлом"""
    global currencies
    cur = update.message.text
    currencies.append(cur)
    url = f"https://api.apilayer.com/currency_data/historical?date={date_for_old_currency}&source={currencies[0]}&" \
          f"currencies={','.join(currencies)}"
    payload = {}
    headers = {
        "apikey": api
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response:
        json_form = response.json()
        await update.message.reply_text(f"""1 {currencies[0]} = {json_form["quotes"][''.join(currencies)]} {currencies[1]}. 
        \n \n Если вы хотите узнать курсы других валют в прошлом, воспользуйтесь командой /old_currency""",
                                        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


async def stop_old_currency(update, context):
    """Останавливает работу функции /old_currency"""
    await update.message.reply_text("""Если вы хотите узнать курсы других валют в прошлом, воспользуйтесь командой /old_currency""",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def graph_currency(update, context):
    """Дает возможность выбора пары валюты для того, чтобы узнать курс валют в прошлом"""
    await update.message.reply_text(
        "Введите дату начала в формате YYYY-MM-DD"
    )
    return 1


async def date1(update, context):
    """Дает возможность ввести дату, если пользователь хочет узнать курсы валют в прошлом"""
    global dates_for_graph_currency
    dates_for_graph_currency.append(update.message.text)
    await update.message.reply_text(
        "Введите дату окончания в формате YYYY-MM-DD"
    )
    return 2


async def date2(update, context):
    """Дает возможность ввести дату, если пользователь хочет узнать курсы валют в прошлом"""
    global dates_for_graph_currency
    dates_for_graph_currency.append(update.message.text)
    await update.message.reply_text(
        "Выберите валюту, взятую за единицу",
        reply_markup=markup
    )
    return 3


async def graph_rate1(update, context):
    """Дает возможность выбрать валюты"""
    global currencies
    cur = update.message.text
    currencies.append(cur)
    await update.message.reply_text(
        "Выберите вторую валюту",
        reply_markup=markup
    )
    return 4


async def graph_rate2(update, context):
    """Отправляет курс выбранных валют в прошлом"""
    global currencies
    cur = update.message.text
    currencies.append(cur)
    url = f"https://api.apilayer.com/currency_data/timeframe?start_date={dates_for_graph_currency[0]}&" \
          f"end_date={dates_for_graph_currency[1]}&source={currencies[0]}&currencies={','.join(currencies)}"
    payload = {}
    headers = {
        "apikey": api
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response:
        json_form = response.json()
        x = [i + 1 for i in range(len(json_form['quotes'].values()))]
        y = [i[''.join(currencies)] for i in json_form["quotes"].values()]
        fig, ax = plt.subplots()
        ax.plot(x, y)
        fig.savefig('./graphs/graph.png')
        await context.bot.send_photo(chat_id=update.message.chat_id, photo=open('./graphs/graph.png', 'rb'))
        await update.message.reply_text(f"""Если вы хотите проанализировать курсы других валют, воспользуйтесь командой /graph_currency""",
                                        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


async def stop_graph_currency(update, context):
    """Останавливает работу функции /old_currency"""
    await update.message.reply_text("""Если вы хотите проанализировать курсы других валют, воспользуйтесь командой /graph_currency""",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def info(update, context):
    """Дает возможность выбора валюты для того, чтобы узнать про валюту"""
    await update.message.reply_text(
        "Выберите валюту, про которую вы хотите получить информацию",
        reply_markup=markup
    )
    return 1


async def currency_info(update, context):
    """Отправляет информацию про выбранную валюту"""
    cur = update.message.text
    f = open(f"./info/{cur.lower()}.txt", encoding="utf8").read()
    await update.message.reply_text(f"{f} \n \n Мы надеемся, что вы получили ту информацию, что вы хотели. "
                                    f"Чтобы посмотреть информацию по другой валюте, введите еще раз команду /info",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def stop_info(update, context):
    """Останавливает работу функции /info"""
    await update.message.reply_text("Мы надеемся, что вы получили ту информацию, что вы хотели. "
                                    "Чтобы посмотреть информацию по другой валюте, введите еще раз команду /info",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler_for_currency = ConversationHandler(
        entry_points=[CommandHandler('currency', currency)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, rate1)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, rate2)]
        },

        fallbacks=[CommandHandler('stop_currency', stop_currency)]
    )

    conv_handler_for_old_currency = ConversationHandler(
        entry_points=[CommandHandler('old_currency', old_currency)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, old_rate1)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, old_rate2)],
        },

        fallbacks=[CommandHandler('stop_old_currency', stop_old_currency)]
    )

    conv_handler_for_graph_currency = ConversationHandler(
        entry_points=[CommandHandler('graph_currency', graph_currency)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, date1)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, date2)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, graph_rate1)],
            4: [MessageHandler(filters.TEXT & ~filters.COMMAND, graph_rate2)]
        },

        fallbacks=[CommandHandler('stop_graph_currency', stop_graph_currency)]
    )

    conv_handler_for_info = ConversationHandler(
        entry_points=[CommandHandler('info', info)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, currency_info)]
        },

        fallbacks=[CommandHandler('stop_info', stop_info)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler_for_currency)
    application.add_handler(conv_handler_for_old_currency)
    application.add_handler(conv_handler_for_graph_currency)
    application.add_handler(conv_handler_for_info)

    application.run_polling()


if __name__ == '__main__':
    main()
