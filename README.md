# Бот-викторина

Данный репозиторий содержит ботов, с помощью которых можно проводить викторины в "Telegram" и "VKontakte".

Пример работы бота для Telegram:

![Telegram animation](https://github.com/igorzakhar/quiz-bot/blob/master/screenshots/tg_example.gif)

Пример работы бота для Вконтакте:

![VKontakte animation](https://github.com/igorzakhar/quiz-bot/blob/master/screenshots/vk_example.gif)

## Как установить

Для запуска ботов нужен предустановленный Python версии не ниже 3.7+ (на других версиях не проверялся).
Также в программе используются следующие сторонние библиотеки:
- vk-api [https://github.com/python273/vk_api](https://github.com/python273/vk_api);
- python-telegram-bot [https://github.com/python-telegram-bot/python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).
- redis-py [https://github.com/andymccurdy/redis-py](https://github.com/andymccurdy/redis-py).
- python-dotenv [https://github.com/theskumar/python-dotenv](https://github.com/theskumar/python-dotenv).

Рекомендуется устанавливать зависимости в виртуальном окружении, используя [virtualenv](https://github.com/pypa/virtualenv), [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) или [venv](https://docs.python.org/3/library/venv.html).

1. Скопируйте репозиторий в текущий каталог. Воспользуйтесь командой:
```bash
$ git clone https://github.com/igorzakhar/quiz-bot.git
```
После этого программа будет скопирована в каталог ```quiz-bot```

2. Создайте и активируйте виртуальное окружение:
```bash
$ cd quiz-bot# Переходим в каталог с программой
$ python3 -m venv my_virtual_environment # Создаем виртуальное окружение
$ source my_virtual_environment/bin/activate # Активируем виртуальное окружение
```

3. Установите сторонние библиотеки  из файла зависимостей:
```bash
$ pip install -r requirements.txt # В качестве альтернативы используйте pip3
```

# Настройка приложения
1. Создать бота в Telegram. Бот в Telegram создается при помощи другого бота под названием [BotFather](http://telegram.me/BotFather). Отправляем ему команду ```/newbot```, выбираем имя, которое будет отображаться в списке контактов, и адрес. BotFather пришлет в ответ сообщение с токеном.

2. Заведите аккаунт в [Redislabs](https://redislabs.com/) и создайте базу данных. После создания вы получите адрес базы данных вида: ```redis-13965.f18.us-east-4-9.wc1.cloud.redislabs.com```, его порт вида: ```16635```(порт указан прямо в адресе, через двоеточие) и его пароль.

3. Создайте группу (сообщество) в соц. сети "ВКонтакте".
- Получите токен группы в настройках сообщества:
![VKontakte API key](https://github.com/igorzakhar/quiz-bot/blob/master/screenshots/screenshot_from_2019-04-29_20-10-16.png)

- Так же в настройках нужно разрешить отправку сообщений:
![VKontakte send message setting](https://github.com/igorzakhar/quiz-bot/blob/master/screenshots/screenshot_from_2019-04-29_20-15-54.png)

4. Создайте ```.env``` файл c необходимыми параметрами, такими как:
```
TELEGRAM_TOKEN=
REDIS_HOST=
REDIS_PORT=
REDIS_PASSWORD=
VK_TOKEN=
```

# Добавление вопросов для бота

Для хранения вопросов используется база данных Redis, которая распологается в облаке ([Redislabs](https://redislabs.com/)). Для загрузки вопросов в Redis используйте скрипт ```redis_questions_upload.py```.

Вопросы для ботов должны размещаться в текстовых файлах с кодировкой ```KOI-8R```. Сами файлы должны находиться в каталоге ```quiz-questions```. Разделы файла (Вопросы и ответы)должны быть разделены двумя символами перевода строки ```\n\n```. Пример:
```
Вопрос 1:
Герой фантастической книги Энди Уэйра "Марсианин" - можно сказать,
современный Робинзон: оставленный на Марсе с минимумом припасов, он
должен продержаться четыре года до прибытия экспедиции. Через несколько
месяцев герой выясняет, что, по современному земному законодательству,
является колонизатором Марса, поскольку первым стал заниматься на Марсе
ТАКИМИ работами. Какими именно?

Ответ:
Сельскохозяйственными.

Вопрос 2:
Молодой джентльмен викторианской эпохи мог увидеться и перекинуться
словом с понравившейся девушкой в отсутствие свахи, тетушки, матушки или
служанки только во время прогулки по так называемой Rotten-Row
[рОттен-рОу] - посыпанной песком дорожке в Гайд-парке: девушек отпускали
без провожатого, считая, что они как бы находятся под присмотром... Кого?

Ответ:
Лошади.

```

# Запуск приложения

##### 1. Запуск бота Telegram:
```bash
$ python3 tg_quiz_bot.py
```

##### 2. Запуск бота VKontakte:
```bash
$ python3 vk_quiz_bot.py
```
