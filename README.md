# Email Tg Bot
Telegram-бот для отправки одиночных и массовых рассылок. При дальнейшей разработке может сэкономить время пользователя при рассылке сообщений десяткам и сотням людей одновременно. Так же была придумана система авторизации пользователя.

## Используемые технологии
+ Python
+ SQL (sqlite3)
+ Используемые библиотеки Python:
  + random
  + smtplib
  + time
  + email.mime.text
  + telebot

## Проблемы с которыми пришлось столкнуться
Сложные:
+ Необходимы знания в асинхронном программировании для возможности использования бота несколькими пользователями одновременно

Средние:
+ Необходимо было сохранять данные полученные от пользователя в отдельном месте. Изучив sqlite3 и внедрив его я смог избавиться от этой проблемы.

Легкие:
+ Дублирование сообщений при быстром клике на кнопку

## Дальнейшее возможное развитие проекта
1) Создать возможность загружать текстовые файлы с email адресами и отправлять на все указанные email определенное сообщение
2) Добавить подтверждение аккаунта через код, отправленный на электронную почту пользователя


## Поддержка
Если у вас возникли сложности или вопросы по использованию пакета, создайте [обсуждение](https://github.com/FedorSmorodskii/Email_Tg_Bot/issues) в данном репозитории или напишите на электронную почту fedorsmorodskii@gmail.com