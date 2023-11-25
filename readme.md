# Навигация

- [Навигация](#навигация)
- [Зачем нужен этот бот?](#зачем-нужен-этот-бот)
- [Установка](#установка)
     - [Python](#python)
     - [Установка необходимых Python-пакетов](#установка-необходимых-python-пакетов)
     - [Запуск установщика](#запуск-установщика)
     - [Запуск бота](#запуск-бота)
          - [Запуск с помощью скрипта](#запуск-с-помощью-скрипта)
               - [Linux](#linux)
               - [Macos](#macos)
          - [Запуск вручную](#запуск-вручную)
- [Режим отладки](#режим-отладки)

# Зачем нужен этот бот?

Зачастую люди, желающие открыть маленький интернет-бизнес, делают это с помощью профиля в социальных сетях, что требует вручную обрабатывать каждую заявку. Этот бот позволит каждому быстро открыть автоматизированный магазин на базе телеграм бота, что значительно уменьшит время обработки заказов.

![overview](DOCS/bot_overview.gif)

# Установка

## Python

Для работы бота необходимо установить [Python версии 3.10 и выше](https://www.python.org/downloads/).

## Установка необходимых Python-пакетов

    python3 -m pip install -r requirements.txt

## Запуск установщика

Перед запуском установщика требуется [создать токен](https://youtu.be/fyISLEvzIec) для телеграм бота и [получить ваш ID](https://badcode.ru/kak-v-telegram-uznat-svoi-id/).

Установщик запускается с помощью команды: 

    python3 installer.py

## Запуск бота

### Запуск с помощью скрипта

#### Linux/MacOS

    $ chmod +x start.sh
    $ ./start.sh

#### Windows

    $ start.cmd

### Запуск вручную

    python3 main.py

# Режим отладки

Режим отладки можно активировать во вкладке "Основные настройки". 
После активации в терминале начнут отображаться все сообщения и вызовы в формате:

    DEBUG: <MESSAGE/CALL> [<user_id>] <Сообщение/вызов>

*Пример: `DEBUG CALL [462741] admin_itemManagement`*



# Поддержать проект

Monero: 43fxouHQFZ5guiyYSUWh6eL1ZQ7pDtVV8D1kKUzp4aYwQBgLjyY8q7KjeEbDvvTYCDPFEdDxz9duBdRrZPnjiSMwVGV4jZj 

Bitcoin: bc1qnzft2cfty0hqptxjx9ajk4m2q9x3a30gvpylh2


