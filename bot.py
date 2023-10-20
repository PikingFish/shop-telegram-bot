import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import datetime
from random import choice, randint
from aiogram.dispatcher import FSMContext
from string import ascii_letters, digits
import stats
from configparser import ConfigParser
import markups
import state_handler
from user import User
import user as usr

conn = sqlite3.connect('data.db')
c = conn.cursor()


conf = ConfigParser()
conf.read('config.ini', encoding='utf8')


storage = MemoryStorage()
bot = Bot(token=conf['main']['token'])
dp = Dispatcher(bot, storage=storage)


def get_item_count(item_id):
    c.execute(f"SELECT * FROM item_stock WHERE item_id={item_id}")
    count = 0
    for _ in c:
        count += 1
    return count


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    conf = ConfigParser()
    conf.read('config.ini', encoding='utf8')

    user = User(message.chat.id)

    markupMain = markups.get_markup_main()
    adminPanel = types.KeyboardButton('🔴Админ панель')

    if not usr.does_user_exist(message.chat.id):
        if str(message.chat.id) == conf['main']['main_admin_id']:
            c.execute(f"INSERT INTO users VALUEs({message.chat.id}, 0, 1, 0, 0, 0, \"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\")")
            conn.commit()
            markupMain.row(adminPanel)
        else:
            c.execute(f"INSERT INTO users VALUEs({message.chat.id}, 0, 0, 0, 0, 0, \"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\")")
            conn.commit()
    else:
        if user.is_admin():
            markupMain.row(adminPanel)
        # if user_is_supplier(message.chat.id):
        #     markupMain.row(addAccount)
        if user.is_admin():
            btnSupport = types.KeyboardButton(text='☎Меню тех. поддержки')
            markupMain.row(btnSupport)

    sti = open('AnimatedSticker.tgs', 'rb')
    await bot.send_sticker(message.chat.id, sti)
    sti.close()
    await bot.send_message(message.chat.id,
                            f"Добро пожаловать в магазин аккаунтов "
                            f"{conf['shop_settings']['shop_name']}, {message.from_user.first_name}!",
                           reply_markup=markupMain)


@dp.message_handler()
async def handle_text(message):
    user = User(message.chat.id)

    conf = ConfigParser()
    conf.read('config.ini', encoding='utf8')

    if message.text == '🔴Админ панель':
        if user.is_admin():
            await bot.send_message(message.chat.id, '🔴Админ панель', reply_markup=markups.get_admin_markup())
    elif message.text == 'ℹ️FAQ':
        markupFAQ = markups.get_faq_markup()
        await bot.send_message(message.chat.id, f'➖➖➖➖➖➖➖➖➖➖\nℹ️FAQ магазина {conf["shop_settings"]["shop_name"]}'
                                                f'\n➖➖➖➖➖➖➖➖➖➖', reply_markup=markupFAQ)
    elif message.text == '📁Профиль':
        markupProfile = markups.get_markup_profile(user_id=message.chat.id)
        await bot.send_message(message.chat.id,
                               f"➖➖➖➖➖➖➖➖➖➖\n"
                               f"🧍Имя: {usr.get_user_login(message)}\n"
                               f"📝id: {message.chat.id}\n"
                               f"📈Кол-во заказов: {len(usr.get_user_orders(message.chat.id))}\n"
                               f"💸Баланс: {user.get_balance()}руб.\n"
                               f"Дата регистрации: {user.get_register_date()}"
                               f"\n➖➖➖➖➖➖➖➖➖➖",
                               reply_markup=markupProfile)

    elif message.text == '🛒Каталог':
        catMarkup = types.InlineKeyboardMarkup()
        c.execute('SELECT * FROM cats')
        for category in c:
            btnCat = types.InlineKeyboardButton(text=category[1], callback_data=f"cat{category[0]}")
            catMarkup.add(btnCat)
        await bot.send_message(message.chat.id, '➖➖➖➖➖➖➖➖➖➖\n🔴Категории\n➖➖➖➖➖➖➖➖➖➖',
                               reply_markup=catMarkup)

    else:
        await bot.send_message(message.chat.id, 'Не могу понять команду :(')


@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery):
    conf = ConfigParser()
    conf.read('config.ini', encoding='utf8')
    chatid = callback_query.message.chat.id
    callText = callback_query.data
    user = User(chatid)

    if callText[:3] == 'cat':
        catMarkup = types.InlineKeyboardMarkup()
        c.execute(f"SELECT * FROM items WHERE cat_id={callText[3:]}")
        items = list(c)
        c.execute(f"SELECT * FROM cats WHERE id={callText[3:]}")
        for cat in c:
            pass
        for item in items:
            amount = get_item_count(item[0])
            text = f'{item[1]} - {amount}шт. - {item[2]}руб.'
            btnCat = types.InlineKeyboardButton(text=text, callback_data=f"item{item[0]}")
            catMarkup.add(btnCat)
        catMarkup.add(markups.get_cat_back())
        await bot.edit_message_text(text=f'➖➖➖➖➖➖➖➖➖\n{cat[1]}\n➖➖➖➖➖➖➖➖➖',
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=catMarkup)
    elif callText[:4] == 'item':
        c.execute(f"SELECT * FROM items WHERE id={callText[4:]}")
        for item in c:
            pass
        cat_id = item[3]
        await bot.edit_message_text(
                                    text=f'➖➖➖➖➖➖➖➖➖\n{item[1]} - {item[2]}руб.\n➖➖➖➖➖➖➖➖➖\n{item[4]}',
                                    chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=markups.get_item_markup(item[0], cat_id)
                                    )
    elif callText[:7] == 'confirm':
        c.execute(f"SELECT * FROM items WHERE id={callText[7:]}")
        for item in c:
            pass
        await bot.edit_message_text(
            text=f'Вы уверены, что хотите купить {item[1]} за {item[2]}?',
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=markups.get_confirm_buy_markup(callText[7:])
        )

    elif callText[:3] == 'buy':
        itemid = callText[3:]
        c.execute(f"SELECT * FROM items WHERE id={itemid}")
        for item in c:
            pass

        if get_item_count(itemid) > 0:
            if item[2] <= user.get_balance():

                c.execute(f"SELECT * FROM item_stock WHERE item_id={itemid}")
                unused_accounts = list(c)
                account = choice(unused_accounts)
                login = account[2]
                password = account[3]

                usr.set_user_balance(user_id=chatid, price=item[2], remove_value=True)

                if get_item_count(itemid) < 5:
                    for notif in usr.get_notif_list():
                        await bot.send_message(chat_id=notif[0],
                                               text=f'Товара {item[1]} всего {get_item_count(item[0]) - 1}шт. в наличии!')
                c.execute(f"DELETE FROM item_stock WHERE login='{login}' AND password='{password}'")

                unique_fl = True
                while unique_fl:
                    order_id = randint(1000000000, 9999999999)
                    c.execute(f"SELECT * FROM orders WHERE order_id='{order_id}'")
                    if len(list(c)) == 0:
                        unique_fl = False

                logpass = f"{login}:{password}"
                c.execute(f"INSERT INTO orders VALUES({order_id}, {chatid}, {itemid}, '{logpass}', '{str(datetime.datetime.now())[:-7]}')")

                conn.commit()
                text = f'➖➖➖➖➖➖➖➖➖\n' \
                       f'Заказ номер {order_id}\n' \
                       f'➖➖➖➖➖➖➖➖➖\n' \
                       f'Логин: {login}\n' \
                       f'Пароль: {password}\n'
                await bot.delete_message(chat_id=chatid, message_id=callback_query.message.message_id)
                await bot.send_message(
                    chat_id=chatid,
                    text=text
                )
            else:
                await bot.delete_message(chat_id=chatid, message_id=callback_query.message.message_id)
                await bot.send_message(
                    chat_id=chatid,
                    text=f'У вас недостаточно средств :(\nПерейдите в профиль, чтобы пополнить баланс!'
                )
        else:
            await bot.delete_message(chat_id=chatid, message_id=callback_query.message.message_id)
            await bot.send_message(
                chat_id=chatid,
                text=f'Товара {item[1]} нет в наличии'
            )
    elif callText == 'contacts':
        contactsMarkup = types.InlineKeyboardMarkup()
        contactsMarkup.add(markups.get_faq_back())
        text = conf['shop_settings']['shop_contacts'] + '\n\nБот сделан @w1png'
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=contactsMarkup,
        )
    elif callText == 'refund':
        refundMarkup = types.InlineKeyboardMarkup()
        refundMarkup.add(markups.get_faq_back())
        text = conf['shop_settings']['refund_policy']
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=refundMarkup,
        )
    elif callText == 'orders':
        orders = usr.get_user_orders(chatid)
        ordersMarkup = types.InlineKeyboardMarkup()
        for order in orders:
            c.execute(f"SELECT * FROM items WHERE id={order[2]}")
            for item in c:
                pass
            btn = types.InlineKeyboardButton(text=f'[{item[1]}] - {order[0]}', callback_data=f'order{order[0]}')
            ordersMarkup.add(btn)
        text = '➖➖➖➖➖➖➖➖➖\nВаши заказы\n➖➖➖➖➖➖➖➖➖'
        ordersMarkup.add(markups.get_profile_back())
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=ordersMarkup
        )

    elif callText == 'backAdmin':
        if user.is_admin():
            await bot.edit_message_text(
                text='🔴Админ панель',
                message_id=callback_query.message.message_id,
                chat_id=chatid,
                reply_markup=markups.get_admin_markup()
            )

    elif callText == 'mainSettings':
        await bot.edit_message_text(
            text='🛠Основные настройки',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_main_settings_markup()
        )

    elif callText == 'qiwiSettings':
        await bot.edit_message_text(
            text='🥝Настройки QIWI кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_qiwi_settings()
        )

    elif callText == 'qiwiOn':
        conf.set('payment_settings', 'qiwi_isactive', '1')
        with open('config.ini', 'w') as config:
            conf.write(config)
        await bot.edit_message_text(
            text='🥝Настройки QIWI кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_qiwi_settings()
        )

    elif callText == 'qiwiOff':
        conf.set('payment_settings', 'qiwi_isactive', '0')
        with open('config.ini', 'w') as config:
            conf.write(config)

        await bot.edit_message_text(
            text='🥝Настройки QIWI кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_qiwi_settings()
        )

    elif callText == 'btcSettings':
        await bot.edit_message_text(
            text='💵Настройки BTC кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_btc_settings_markup(),
        )

    elif callText == 'btcOn':
        conf.set('payment_settings', 'btc_isactive', '1')
        with open('config.ini', 'w') as config:
            conf.write(config)
        await bot.edit_message_text(
            text='💵Настройки BTC кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_btc_settings_markup(),
        )

    elif callText == 'btcOff':
        conf.set('payment_settings', 'btc_isactive', '0')
        with open('config.ini', 'w') as config:
            conf.write(config)
        await bot.edit_message_text(
            text='💵Настройки BTC кошелька',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_btc_settings_markup(),
        )

    elif callText == 'balance':
        await bot.edit_message_text(
            text='💰Пополнение баланса',
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_balance_markup()
        )

    elif callText == 'shopStats':
        await bot.edit_message_text(
            text='📈Статистика магазина',
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markups.get_stats_markup()
        )

    elif callText == 'userStats':
        await bot.edit_message_text(
            text='👥Статистика пользователей',
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markups.get_user_stats_markup()
        )

    elif callText == 'userStatsAllTime':
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_photo(
            chat_id=chatid,
            caption='Регистрации за всё время',
            photo=stats.get_chart(alltime=True),
            reply_markup=markups.get_user_stats_back(),
        )

    elif callText == 'userStatsMonth':
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_photo(
            chat_id=chatid,
            caption='Регистрации за месяц',
            photo=stats.get_chart(month=True),
            reply_markup=markups.get_user_stats_back(),
        )

    elif callText == 'userStatsWeek':
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_photo(
            chat_id=chatid,
            caption='Регистрации за неделю',
            photo=stats.get_chart(week=True),
            reply_markup=markups.get_user_stats_back(),
        )

    elif callText == 'userStatsDay':
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_photo(
            chat_id=chatid,
            caption='Регистрации за день',
            photo=stats.get_chart(day=True),
            reply_markup=markups.get_user_stats_back(),
        )

    elif callText == 'userStatsBack':
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_message(
            text='📈Статистика магазина',
            chat_id=chatid,
            reply_markup=markups.get_user_stats_markup()
        )

    elif callText == 'statsOrder':
        markup = markups.get_stats_order_markup()
        c.execute(f"SELECT * FROM cats")
        for cat in c:
            markup.add(types.InlineKeyboardButton(text=cat[1], callback_data=f"getStatsCat{cat[0]}"))
        markup.add(markups.goBackStats)
        await bot.edit_message_text(
            text='📦Статистика заказов',
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markup
        )

    elif callText[:11] == 'getStatsCat':
        markup = types.InlineKeyboardMarkup()
        catid = callText[11:]
        c.execute(f"SELECT * FROM cats WHERE id={catid}")
        for cat in c:
            pass
        c.execute(f"SELECT * FROM items WHERE cat_id={catid}")
        for item in c:
            btnItem = types.InlineKeyboardButton(text=item[1], callback_data=f'getStatsItem{item[0]}')
            markup.add(btnItem)
        markup.add(markups.goBackStats)
        await bot.edit_message_text(
            text=f'➖➖➖➖➖➖➖➖➖➖\n{cat[1]}\n➖➖➖➖➖➖➖➖➖➖',
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markup
        )

    elif callText[:12] == 'getStatsItem':
        itemid = callText[12:]
        c.execute(f"SELECT * FROM items WHERE id={itemid}")
        for item in c:
            pass
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(markups.goBackFromItem)
        if stats.get_chart_item(itemid):
            await bot.send_photo(
                chat_id=chatid,
                caption=f'Заказы на {item[1]} за всё время.',
                photo=stats.get_chart_item(itemid),
                reply_markup=markup,
            )
        else:
            await bot.send_message(
                chat_id=chatid,
                text=f'Заказов на {item[1]} нет.',
                reply_markup=markup,
            )

    elif callText == 'backFromitem':
        markup = markups.get_stats_order_markup()
        c.execute(f"SELECT * FROM cats")
        for cat in c:
            markup.add(types.InlineKeyboardButton(text=cat[1], callback_data=f"getStatsCat{cat[0]}"))
        markup.add(markups.goBackStats)
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_message(
            text='📦Статистика заказов',
            chat_id=chatid,
            reply_markup=markup
        )

    elif callText == 'StatsItem':
        await bot.edit_message_text(
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            text='💡Статистика по товару',
            reply_markup=markups.get_stats_item_markup()
        )

    elif callText == 'StatsAllTimeItem':
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(markups.goBackOrderStatsItem)
        await bot.send_photo(
            chat_id=chatid,
            caption='Заказы за всё время',
            photo=stats.get_chart_item(alltime=True),
            reply_markup=markup,
        )

    elif callText == 'StatsMonthItem':
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(markups.goBackOrderStatsItem)
        await bot.send_photo(
            chat_id=chatid,
            caption='Заказы за месяц',
            photo=stats.get_chart_item(month=True),
            reply_markup=markup,
        )

    elif callText == 'StatsWeekItem':
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(markups.goBackOrderStatsItem)
        await bot.send_photo(
            chat_id=chatid,
            caption='Заказы за неделю',
            photo=stats.get_chart_item(week=True),
            reply_markup=markup,
        )

    elif callText == 'StatsDayItem':
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(markups.goBackOrderStatsItem)
        await bot.send_photo(
            chat_id=chatid,
            caption='Заказы за день',
            photo=stats.get_chart_item(day=True),
            reply_markup=markup,
        )

    elif callText == 'goBackOrderStatsItem':
        await bot.delete_message(
            chat_id=chatid,
            message_id=callback_query.message.message_id
        )
        await bot.send_message(
            chat_id=chatid,
            text='💡Статистика по товару',
            reply_markup=markups.get_stats_item_markup()
        )

    elif callText[:9] == 'userOrder':
        orderMarkup = types.InlineKeyboardMarkup()
        order_id = callText[9:]
        orderMarkup.add(markups.get_clients_back_button())
        c.execute(f"SELECT * FROM orders WHERE order_id={order_id}")
        for order in c:
            pass
        c.execute(f"SELECT * FROM items WHERE id={order[2]}")
        for item in c:
            pass
        itemName = item[1]
        login = order[3].split(':')[0]
        password = order[3].split(':')[1]
        date = order[4]
        text = f'➖➖➖➖➖➖➖➖➖\nЗаказ номер {order_id}\n➖➖➖➖➖➖➖➖➖\n' \
               f'Товар: {itemName}\n' \
               f'Логин: {login}\n' \
               f'Пароль: {password}\n' \
               f'Дата заказа: {date}'
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=orderMarkup
        )

    elif callText[:5] == 'order':
        orderMarkup = types.InlineKeyboardMarkup()
        order_id = callText[5:]
        supportOrder = types.InlineKeyboardButton(text='📱Открыть тикет в тех. поддержку', callback_data=f'support{order_id}')
        orderMarkup.add(supportOrder)
        orderMarkup.add(markups.get_orders_back())
        c.execute(f"SELECT * FROM orders WHERE order_id={order_id}")
        for order in c:
            pass
        c.execute(f"SELECT * FROM items WHERE id={order[2]}")
        for item in c:
            pass
        itemName = item[1]
        login = order[3].split(':')[0]
        password = order[3].split(':')[1]
        date = order[4]
        text = f'➖➖➖➖➖➖➖➖➖\nЗаказ номер {order_id}\n➖➖➖➖➖➖➖➖➖\n' \
               f'Товар: {itemName}\n' \
               f'Логин: {login}\n' \
               f'Пароль: {password}\n' \
               f'Дата заказа: {date}'
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=orderMarkup
        )

    elif callText[:7] == 'support':
        pass  # TODO: сделать саппорт через state_handler

    elif callText == 'seeSupportTickets':
        pass  # TODO: сделать вывод тиктов

    elif callText == 'botSettings':
        settingsMarkup = markups.get_settings_markup()
        text = '⚙Настройки бота'
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=settingsMarkup
        )

    elif callText == 'disableNotif':
        user.disable_notif()
        markupProfile = markups.get_markup_profile(user_id=chatid)
        await bot.edit_message_text(
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markupProfile,
            text=f"➖➖➖➖➖➖➖➖➖➖\n"
                 f"🧍Имя: {usr.get_user_login(callback_query.message)}\n"
                 f"📝id: {chatid}\n"
                 f"📈Кол-во заказов: {len(usr.get_user_orders(chatid))}\n"
                 f"💸Баланс: {user.get_balance()}руб.\n"
                 f"Дата регистрации: {user.get_register_date()}"
                 f"\n➖➖➖➖➖➖➖➖➖➖",
        )

    elif callText == 'backProfile':
        markupProfile = markups.get_markup_profile(user_id=chatid)

        await bot.edit_message_text(
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markupProfile,
            text=f"➖➖➖➖➖➖➖➖➖➖\n"
                 f"🧍Имя: {usr.get_user_login(callback_query.message)}\n"
                 f"📝id: {chatid}\n"
                 f"📈Кол-во заказов: {len(usr.get_user_orders(chatid))}\n"
                 f"💸Баланс: {user.get_balance()}руб.\n"
                 f"Дата регистрации: {user.get_register_date()}"
                 f"\n➖➖➖➖➖➖➖➖➖➖",
        )

    elif callText == 'enableNotif':
        user.enable_notif()
        markupProfile = markups.get_markup_profile(user_id=chatid)
        await bot.edit_message_text(
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=markupProfile,
            text=f"➖➖➖➖➖➖➖➖➖➖\n"
                 f"🧍Имя: {usr.get_user_login(callback_query.message)}\n"
                 f"📝id: {chatid}\n"
                 f"📈Кол-во заказов: {len(usr.get_user_orders(chatid))}\n"
                 f"💸Баланс: {user.get_balance()}руб.\n"
                 f"Дата регистрации: {user.get_register_date()}"
                 f"\n➖➖➖➖➖➖➖➖➖➖",
        )

    elif callText == 'goBackFaq':
        markupFAQ = markups.get_faq_markup()
        text = f'➖➖➖➖➖➖➖➖➖➖\n' \
                f'ℹ️FAQ магазина {conf["shop_settings"]["shop_name"]}\n' \
                f'➖➖➖➖➖➖➖➖➖➖'
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markupFAQ
        )

    elif callText == 'backCat':
        catMarkup = types.InlineKeyboardMarkup()
        c.execute('SELECT * FROM cats')
        for category in c:
            btnCat = types.InlineKeyboardButton(text=category[1], callback_data=f"cat{category[0]}")
            catMarkup.add(btnCat)
        await bot.edit_message_text(
            text='➖➖➖➖➖➖➖➖➖➖\n🔴Категории\n➖➖➖➖➖➖➖➖➖➖',
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            reply_markup=catMarkup
        )

    elif callText == 'changeShopName':
        text = f"{conf['shop_settings']['shop_name']}\nВведите новое название или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_main_settings(),
        )
        await state_handler.changeShopName.name.set()

    elif callText == 'changeContacts':
        text = f"{conf['shop_settings']['shop_contacts']}\nВведите новый текст для вкладки \"Контакты\" или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_main_settings(),
        )
        await state_handler.changeShopContacts.text.set()

    elif callText == 'changeRefund':
        text = f"{conf['shop_settings']['refund_policy']}\nВведите новый текст для вкладки \"Политика возврата\" или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_main_settings(),
        )
        await state_handler.changeShopRefund.text.set()

    elif callText == 'changeQiwiNumber':
        text = f"{conf['payment_settings']['qiwi_number']}\nВведите новый номер QIWI в формате \"+70000000000\" или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_qiwi_settings(),
        )
        await state_handler.changeQiwiNumber.number.set()

    elif callText == 'changeQiwiToken':
        text = f"{conf['payment_settings']['qiwi_token']}\nВведите новый токен QIWI или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_qiwi_settings(),
        )
        await state_handler.changeQiwiToken.token.set()

    elif callText == 'changeMainBtc':
        text = f"{conf['payment_settings']['main_btc_adress']}\nВведите основной Bitcoin кошелёк или нажмите на кнопку \"Назад\""
        await bot.edit_message_text(
            text=text,
            message_id=callback_query.message.message_id,
            chat_id=chatid,
            reply_markup=markups.get_cancel_states_btc_settings(),
        )
        await state_handler.changeMainBtc.wallet.set()

    elif callText == 'clientManagement':
        await bot.edit_message_text(
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            text='🧍Управление пользователями',
            reply_markup=markups.get_client_management_markup(),
        )

    elif callText == 'seeUserPurchases':
        await bot.edit_message_text(
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            text='Введите ID пользователя или нажмите на кнопку \"Назад\"',
            reply_markup=markups.get_cancel_states_clients()
        )
        await state_handler.seeUserOrders.userid.set()

    elif callText == 'addBal':
        await bot.edit_message_text(
            chat_id=chatid,
            message_id=callback_query.message.message_id,
            text='Введите ID пользователя и баланс в формате \"id - баланс\" или нажмите на кнопку \"Назад\"',
            reply_markup=markups.get_cancel_states_clients()
        )
        await state_handler.changeUserBalance.useridAndBal.set()


@dp.message_handler(state=state_handler.changeUserBalance.useridAndBal)
async def changeUserBalance(message: types.Message, state: FSMContext):
    try:
        userid = message.text.split(' - ')[0]
        balance = message.text.split(' - ')[1]
        c.execute(f"UPDATE users SET balance={balance} WHERE user_id={userid}")
        conn.commit()
        await bot.send_message(
            chat_id=message.chat.id,
            text='🧍Управление пользователями',
            reply_markup=markups.get_client_management_markup(),
        )
        await bot.send_message(
            chat_id=message.chat.id,
            text=f'Баланс пользователя с ID {userid} был обновлен до {balance} руб.'
        )
    except:
        await bot.send_message(
            chat_id=message.chat.id,
            text='🧍Управление пользователями',
            reply_markup=markups.get_client_management_markup(),
        )
        await bot.send_message(
            chat_id=message.chat.id,
            text=f'Ошибка'
        )
    await state.finish()


@dp.message_handler(state=state_handler.seeUserOrders.userid)
async def seeUserOrders(message: types.Message, state: FSMContext):
    orders = usr.get_user_orders(message.text)
    if not orders:
        await bot.send_message(
            chat_id=message.chat.id,
            text='🧍Управление пользователями',
            reply_markup=markups.get_client_management_markup(),
        )
        await bot.send_message(
            chat_id=message.chat.id,
            text=f'У пользователя с ID {message.text} нет заказов'
        )
    else:
        ordersMarkup = types.InlineKeyboardMarkup()
        for order in orders:
            c.execute(f"SELECT * FROM items WHERE id={order[2]}")
            for item in c:
                pass
            btn = types.InlineKeyboardButton(text=f'[{item[1]}] - {order[0]}', callback_data=f'userOrder{order[0]}')
            ordersMarkup.add(btn)
        text = f'➖➖➖➖➖➖➖➖➖\nЗаказы пользователя {message.text}\n➖➖➖➖➖➖➖➖➖'
        ordersMarkup.add(markups.get_clients_back_button())
        await bot.send_message(
            text=text,
            chat_id=message.chat.id,
            reply_markup=ordersMarkup
        )
    await state.finish()


@dp.message_handler(state=state_handler.changeMainBtc.wallet)
async def changeQiwiToken(message: types.Message, state: FSMContext):
    conf.set('payment_settings', 'main_btc_adress', message.text)
    with open('config.ini', 'w') as config:
        conf.write(config)
    await bot.send_message(
        text='💵Настройки BTC кошелька',
        chat_id=message.chat.id,
        reply_markup=markups.get_btc_settings_markup()
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Основной Bitcoin кошелёк был изменен на \"{message.text}\"",
    )
    await state.finish()


@dp.message_handler(state=state_handler.changeQiwiToken.token)
async def changeQiwiToken(message: types.Message, state: FSMContext):
    conf.set('payment_settings', 'qiwi_token', message.text)
    with open('config.ini', 'w') as config:
        conf.write(config)
    await bot.send_message(
        text='🥝Настройки QIWI кошелька',
        chat_id=message.chat.id,
        reply_markup=markups.get_qiwi_settings()
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Токен QIWI был изменен на \"{message.text}\"",
    )
    await state.finish()


@dp.message_handler(state=state_handler.changeQiwiNumber.number)
async def changeQiwiNumber(message: types.Message, state: FSMContext):
    conf.set('payment_settings', 'qiwi_number', message.text)
    with open('config.ini', 'w') as config:
        conf.write(config)
    await bot.send_message(
        text='🥝Настройки QIWI кошелька',
        chat_id=message.chat.id,
        reply_markup=markups.get_qiwi_settings()
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Номер QIWI был изменен на \"{message.text}\"",
    )
    await state.finish()


@dp.message_handler(state=state_handler.changeShopRefund.text)
async def changeShopRefund(message: types.Message, state: FSMContext):
    conf.set('shop_settings', 'refund_policy', message.text)
    with open('config.ini', 'w') as config:
        conf.write(config)
    await bot.send_message(
        text='🛠Основные настройки',
        chat_id=message.chat.id,
        reply_markup=markups.get_main_settings_markup()
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Текст для вкладки \"Политика возврата\" был изменен на \"{message.text}\"",
    )
    await state.finish()


@dp.message_handler(state=state_handler.changeShopContacts.text)
async def changeShopContacts(message: types.Message, state: FSMContext):
    conf.set('shop_settings', 'shop_contacts', message.text)
    with open('config.ini', 'w') as config:
        conf.write(config)
    await bot.send_message(
        text='🛠Основные настройки',
        chat_id=message.chat.id,
        reply_markup=markups.get_main_settings_markup()
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Текст для вкладки \"Контакты\" был изменен на \"{message.text}\"",
    )
    await state.finish()


@dp.message_handler(state=state_handler.changeShopName.name)
async def changeShopName(message: types.Message, state: FSMContext):
    conf.set('shop_settings', 'shop_name', message.text)
    with open('config.ini', 'w') as config:
        conf.write(config)
    await bot.send_message(
        text='🛠Основные настройки',
        chat_id=message.chat.id,
        reply_markup=markups.get_main_settings_markup()
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Название магазина было изменено на \"{message.text}\"",
    )
    await state.finish()


@dp.callback_query_handler(state='*')
async def cancelState(callback_query: types.CallbackQuery, state: FSMContext):
    chatid = callback_query.message.chat.id
    user = User(chatid)
    call = callback_query.data
    if call == 'cancelStateMainSettings':
        if user.is_admin():
            await bot.edit_message_text(
                text='🛠Основные настройки',
                message_id=callback_query.message.message_id,
                chat_id=chatid,
                reply_markup=markups.get_main_settings_markup()
            )

    elif call == 'cancelStateQiwiSettings':
        if user.is_admin():
            await bot.edit_message_text(
                text='🥝Настройки QIWI кошелька',
                message_id=callback_query.message.message_id,
                chat_id=chatid,
                reply_markup=markups.get_qiwi_settings()
            )

    elif call == 'cancelStateBTCSettings':
        if user.is_admin():
            await bot.edit_message_text(
                text='💵Настройки BTC кошелька',
                message_id=callback_query.message.message_id,
                chat_id=chatid,
                reply_markup=markups.get_btc_settings_markup()
            )

    elif call == 'cancelStateClients':
        if user.is_admin():
            await bot.edit_message_text(
                chat_id=chatid,
                message_id=callback_query.message.message_id,
                text='🧍Управление пользователями',
                reply_markup=markups.get_client_management_markup(),
            )

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

