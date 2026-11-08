"""Движок игры «Твоя жизнь»: с рождения до смерти, 1 ход = 1 месяц (12 событий в году).
Чистая логика без Telegram: handle(u, data) -> (текст, кнопки)."""
import random

MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
# город: (название, множитель зарплат, множитель цен, городская зарисовка)
CITIES = {
    "msk": ("🏛 Москва", 1.3, 1.3, "В метро час пик, вас несёт толпой."),
    "spb": ("🌉 Санкт-Петербург", 1.0, 1.1, "Белые ночи: город не спит."),
    "kyiv": ("🌳 Киев", .8, .8, "На Крещатике играют уличные музыканты."),
    "minsk": ("🚇 Минск", .7, .7, "В центре открыли ярмарку."),
    "alm": ("🏔 Алматы", .7, .7, "Горы на горизонте, на площади фестиваль еды."),
    "war": ("🏰 Варшава", 1.0, 1.0, "Старый город полон туристов."),
    "ist": ("🕌 Стамбул", .8, .8, "Паром через Босфор, запах симита."),
    "ber": ("🥨 Берлин", 1.3, 1.2, "В клубах вечеринки до утра."),
    "par": ("🥐 Париж", 1.4, 1.5, "Из пекарни тянет свежими круассанами."),
    "lon": ("🎡 Лондон", 1.6, 1.6, "Моросит дождь, в пабе футбол."),
    "ny": ("🗽 Нью-Йорк", 1.9, 1.9, "Город, который никогда не спит."),
    "la": ("🌴 Лос-Анджелес", 1.7, 1.7, "На бульваре снимают кино."),
    "tok": ("🍜 Токио", 1.5, 1.5, "Неон и тишина храмов в одном квартале."),
    "seo": ("🎤 Сеул", 1.3, 1.3, "На улице идёт съёмка клипа."),
    "dub": ("🏙 Дубай", 1.8, 1.6, "Небоскрёбы и жара под сорок."),
    "syd": ("🏄 Сидней", 1.6, 1.6, "На набережной сёрферы и чайки."),
    "rio": ("💃 Рио-де-Жанейро", .7, .8, "На пляже играет самба."),
    "mum": ("🛺 Мумбаи", .5, .5, "Шумные улицы и яркие рынки."),
}
STATS = ("health", "mood", "smarts", "looks", "karma", "nic", "alc", "game", "heat", "fit", "crime")
NAMES = dict(health="❤️Здоровье", mood="😊Настроение", smarts="🧠Ум", looks="😎Внешность", karma="⭐Репутация")

# --- магазин ---
ITEMS = {  # n, цена, штук в упаковке, 18+
    "cig": ("🚬 Сигареты (пачка, 10 шт)", 6, 10, True),
    "ashka": ("💨 Ашка (одноразка)", 12, 8, True),
    "pod": ("🔋 Картридж для пода", 9, 10, True),
    "beer": ("🍺 Пиво", 3, 1, True),
    "energy": ("⚡ Энергетик", 2.5, 1, False),
}
SHOP_ONE = {  # n, цена, эффекты, мин. возраст
    "burger": ("🍔 Бургер", 6, dict(mood=3, health=-.5), 5),
    "cinema": ("🎬 Кино", 10, dict(mood=5), 5),
    "book": ("📖 Книга", 12, dict(smarts=3, mood=1), 6),
    "game": ("🎮 Новая игра", 50, dict(game=4, mood=7), 7),
    "clothes": ("👕 Одежда", 60, dict(looks=3, mood=3), 10),
    "gym": ("🏋 Абонемент в зал", 40, dict(health=4, fit=6, looks=1), 12),
    "phone": ("📱 Смартфон", 600, dict(mood=9, looks=1), 10),
    "pc": ("🖥 Игровой ПК (один раз)", 900, dict(game=8, mood=10), 10),
    "lot": ("🎟 Лотерейный билет", 5, {}, 18),
}
ITEM_USE = {"cig": "🚬 Закурить", "ashka": "💨 Затянуться ашкой", "pod": "🔋 Затянуться подом", "beer": "🍺 Выпить пива", "energy": "⚡ Выпить энергетик"}

# --- работы: имя, ступени, зарплата в месяц, мин. возраст, требования, разброс дохода ---
JOBS = {
    "courier": ("Курьер", ["Курьер", "Старший курьер", "Координатор", "Начальник доставки"], [900, 1200, 1700, 2400], 16, {}, None),
    "seller": ("Продавец", ["Продавец", "Старший продавец", "Администратор", "Директор магазина"], [950, 1300, 1900, 2800], 16, {}, None),
    "builder": ("Строитель", ["Рабочий", "Бригадир", "Прораб", "Владелец фирмы"], [1200, 1700, 2400, 3600], 18, dict(fit=40), None),
    "driver": ("Водитель", ["Водитель", "Дальнобойщик", "Диспетчер", "Хозяин автопарка"], [1100, 1600, 2300, 3300], 18, {}, None),
    "cook": ("Повар", ["Помощник повара", "Су-шеф", "Шеф-повар", "Владелец ресторана"], [1000, 1500, 2600, 5000], 18, {}, None),
    "mechanic": ("Автомеханик", ["Подмастерье", "Механик", "Мастер", "Владелец СТО"], [1100, 1700, 2500, 3800], 18, {}, None),
    "police": ("Полицейский", ["Патрульный", "Сержант", "Лейтенант", "Начальник отдела"], [1500, 2100, 3000, 4500], 20, dict(smarts=40, norec=1), None),
    "teacher": ("Учитель", ["Учитель", "Старший учитель", "Завуч", "Директор школы"], [1100, 1500, 2100, 3000], 22, dict(edu=1), None),
    "accountant": ("Бухгалтер", ["Помощник", "Бухгалтер", "Главбух", "Финансовый директор"], [1400, 2100, 3200, 5500], 22, dict(edu=1, smarts=50), None),
    "dev": ("Программист", ["Джуниор", "Мидл", "Сеньор", "Технический директор"], [2000, 4000, 7000, 12000], 18, dict(smarts=60), None),
    "doctor": ("Врач", ["Интерн", "Врач", "Заведующий отделением", "Главврач"], [1800, 3800, 6500, 11000], 24, dict(edu=1, smarts=70, health=50), None),
    "lawyer": ("Юрист", ["Помощник юриста", "Юрист", "Партнёр", "Именной партнёр"], [1800, 3600, 7000, 13000], 23, dict(edu=1, smarts=65, norec=1), None),
    "pilot": ("Пилот", ["Второй пилот", "Капитан", "Старший капитан", "Инструктор-легенда"], [3000, 6000, 9500, 13000], 22, dict(edu=1, smarts=60, health=70), None),
    "scientist": ("Учёный", ["Лаборант", "Исследователь", "Профессор", "Академик"], [1400, 2600, 4200, 6500], 22, dict(edu=1, smarts=75), None),
    "athlete": ("Спортсмен", ["Новичок", "Профи", "Звезда", "Легенда"], [1000, 3500, 9000, 25000], 17, dict(fit=70, health=60), (.7, 1.6)),
    "actor": ("Актёр", ["Статист", "Актёр", "Известный актёр", "Звезда кино"], [800, 2500, 8000, 30000], 18, dict(looks=70), (.3, 2.5)),
    "musician": ("Музыкант", ["Уличный музыкант", "Клубный артист", "Автор хитов", "Мировая звезда"], [600, 2000, 7000, 28000], 16, dict(looks=40), (.3, 2.5)),
    "streamer": ("Стример", ["Новичок", "Стример", "Топ-стример", "Звезда Twitch"], [400, 2000, 6000, 20000], 14, dict(game=40), (.2, 3)),
    "blogger": ("Блогер", ["Начинающий", "Блогер", "Инфлюенсер", "Медиа-звезда"], [400, 1800, 5500, 18000], 14, dict(looks=45), (.2, 3)),
    "biz": ("Предприниматель", ["Свой ларёк", "Малый бизнес", "Сеть магазинов", "Миллионер"], [1500, 3500, 9000, 30000], 21, dict(money=3000), (.2, 3)),
    "bandit": ("Криминальный авторитет", ["Шестёрка", "Боец", "Бригадир", "Босс"], [1500, 3000, 7000, 20000], 16, dict(crime=10), (.5, 3)),
}
PROMO = [10, 18, 30]  # месяцев опыта для повышения

# ===================== события =====================
NODES = {}

def O(t, r="", p=None, f=None, r2="", n=None, nf=None, s=None, sf=None, need=0, **e):
    return dict(t=t, r=r, p=p, f=f or {}, r2=r2, n=n, nf=nf, s=s, sf=sf, need=need, e=e)

def E(id, text, opts, ages=(0, 120), w=1.0, st=None, start=True, cond=None):
    NODES[id] = dict(id=id, text=text, opts=opts, a=ages, w=w, st=st, start=start, cond=cond)

KID, SCH, PRI, OLD = ["kid"], ["school"], ["prison"], ["old"]
WORKING = ["work"]

# --- малыши ---
E("k_fall", "Вы учитесь ходить и шлёпаетесь на пол. Мама бежит на крик.", [
    O("Заплакать", "Вас жалеют и несут на ручках.", mood=-2),
    O("Встать и идти дальше", "Упрямство засчитано!", mood=3, fit=3)], ages=(1, 3), st=KID)
E("k_words", "Приближается первое слово.", [
    O("Сказать «мама»", "Мама счастлива до слёз.", mood=5, karma=2),
    O("Сказать «дай»", "Папа смеётся: характер виден сразу.", mood=3, smarts=1)], ages=(1, 2), st=KID)
E("k_toy", "В магазине игрушек вы замечаете огромного робота.", [
    O("Устроить истерику", "Родители сдаются и покупают.", p=.5, mood=8, f=dict(karma=-3, mood=-3), r2="Вас уводят, робот остаётся на полке."),
    O("Вежливо попросить", "Вам покупают маленькую машинку.", mood=4, smarts=1)], ages=(2, 6), st=KID)
E("k_garden", "Первый день в садике.", [
    O("Подружиться с ребятами", "У вас появляется лучший друг.", mood=5, karma=3),
    O("Спрятаться под столом", "Воспитательница еле вас достаёт.", mood=-3)], ages=(3, 6), st=KID)
E("k_sick", "Вы подхватили простуду.", [
    O("Лечь и пить чай с малиной", "Через неделю вы как огурец.", health=3, mood=-1),
    O("Сбежать во двор", "Погуляли здорово, но кашель усилился.", health=-5, mood=4)], st=KID, w=1.2)
E("k_cartoon", "Мультики идут по кругу.", [
    O("Смотреть весь день", "Глаза квадратные, зато счастье.", mood=7, smarts=-2),
    O("Рисовать красками", "Стены дома украшены шедеврами.", smarts=3, mood=2)], ages=(2, 6), st=KID)
E("k_dog", "Во дворе вы встречаете большую собаку.", [
    O("Подойти погладить", "Пёс дружелюбный. Вы в восторге!", p=.8, mood=6, f=dict(health=-5, mood=-6), r2="Пёс рявкает, и вы пугаетесь."),
    O("Спрятаться за маму", "Безопасно, но скучно.", mood=-1)], ages=(2, 6), st=KID)
E("k_grandma", "Вы в гостях у бабушки.", [
    O("Есть пирожки", "Вкуснотища! Щёчки круглеют.", mood=7, health=1),
    O("Смотреть старые фотографии", "Бабушка рассказывает семейные истории.", smarts=2, karma=2)], ages=(2, 6), st=KID)

# --- школа ---
E("s_hw", "Учитель задал большое домашнее задание.", [
    O("Сделать честно", "Рука болит, зато пятёрка.", smarts=3, mood=-2),
    O("Списать у друга", "Сдано, и никто не заметил.", p=.7, mood=3, f=dict(karma=-3, smarts=-1), r2="Учитель замечает списанное.", sf=(1, "hw_parents")),
    O("Забить", "Двойка в журнале.", smarts=-3, mood=3, s=(1, "hw_parents"))], ages=(7, 17), st=SCH, w=1.5)
E("hw_parents", "Учитель пишет родителям, что вы не делаете уроки.", [
    O("Пообещать исправиться", "Родители вздыхают и верят.", smarts=1, mood=-3),
    O("Закатить глаза", "Скандал на весь вечер.", karma=-2, mood=-4)], start=False)
E("s_bully", "Одноклассник регулярно вас задирает.", [
    O("Дать сдачи", "Он больше не лезет!", p=.5, karma=2, fit=2, mood=3, f=dict(health=-8, mood=-6), r2="Вам достаётся сильнее.", nf="s_principal"),
    O("Рассказать учителю", "Его ругают, вам легче.", karma=3, mood=-1),
    O("Терпеть", "Тяжело на душе.", mood=-8)], ages=(8, 15), st=SCH)
E("s_principal", "Вас вызывают к директору.", [
    O("Объяснить честно", "Директор слушает и понимает.", karma=2),
    O("Свалить на другого", "Сработало, но совесть грызёт.", karma=-5, mood=-2)], start=False)
E("s_crush", "Вам нравится одноклассник(-ца).", [
    O("Признаться", "Взаимно! Сердце колотится.", p=.5, mood=12, partner=1, f=dict(mood=-10), r2="Вас мягко отшивают."),
    O("Промолчать", "Любовь остаётся тайной.", mood=-3)], ages=(12, 17), st=SCH, cond=lambda u: not u["partner"])
E("s_exam", "Скоро важная контрольная.", [
    O("Зубрить всю ночь", "Мозг кипит, оценка отличная.", smarts=3, mood=-4, health=-1),
    O("Взять шпаргалку", "Прокатило!", p=.6, mood=3, f=dict(karma=-4), r2="Учитель находит шпаргалку.", nf="s_principal"),
    O("Положиться на удачу", "Как повезёт.", p=.4, smarts=1, f=dict(smarts=-2, mood=-3), r2="Тройка.")], ages=(9, 17), st=SCH, w=1.3)
E("s_cig", "Старшие ребята во дворе предлагают сигарету.", [
    O("Попробовать", "Кашель и головокружение, но «все так делают».", nic=10, health=-1, mood=3, karma=-1),
    O("Отказаться", "Над вами чуть смеются, но вы спокойны.", karma=2, mood=-1),
    O("Взять сигарету «на потом»", "Лежит в кармане и жжёт совесть.", inv_cig=1, karma=-1)], ages=(12, 17), st=SCH, w=1.3)
E("s_vape", "У друга одноразка (ашка) со вкусом манго.", [
    O("Затянуться", "Сладко и странно. Голова плывёт.", nic=8, mood=4, health=-1),
    O("Отказаться", "Друг пожимает плечами.", karma=1),
    O("Попросить помочь купить свою", "Друг обещает помочь в магазине.", inv_ashka=1, karma=-2, money=-12)], ages=(12, 17), st=SCH, w=1.2)
E("s_energy", "В классе ажиотаж: все пьют энергетики.", [
    O("Купить банку", "Бодрость и сердцебиение.", money=-3, mood=3, health=-1, inv_energy=1),
    O("Не надо", "Вы пьёте воду.", health=1)], ages=(11, 17), st=SCH)
E("s_party", "Вечеринка у одноклассника, на столе пиво.", [
    O("Выпить", "Весело! Утром — не очень.", mood=8, alc=6, health=-2, s=(1, "a_hangover")),
    O("Пить сок", "Вы остаётесь в своём уме.", karma=1, mood=2),
    O("Уйти домой", "Спокойный вечер.", mood=-1)], ages=(14, 17), st=SCH, w=1.2)
E("s_lan", "Друзья зовут играть в компьютерный клуб.", [
    O("Идти", "Вы рубитесь до ночи. Скилл растёт!", money=-5, game=4, mood=7, smarts=-1),
    O("Остаться делать уроки", "Скучно, зато полезно.", smarts=2)], ages=(8, 17), st=SCH)
E("s_olymp", "Вас приглашают на олимпиаду.", [
    O("Участвовать", "Вы — призёр!", p=.5, smarts=3, karma=3, mood=5, f=dict(mood=-2), r2="Не повезло, но опыт есть."),
    O("Отказаться", "Остаётесь дома.", mood=1)], ages=(9, 17), st=SCH, cond=lambda u: u["smarts"] > 50)
E("s_steal", "Друг предлагает стащить сладости из магазина.", [
    O("Стащить", "Получилось!", p=.6, mood=4, karma=-3, heat=3, f=dict(karma=-4, heat=4), r2="Вас ловит охранник.", nf="cr_police_minor"),
    O("Отказаться", "Друг называет вас трусом, но вы спокойны.", karma=2)], ages=(10, 16), st=SCH)
E("s_money", "Родители ссорятся из-за денег.", [
    O("Подработать после уроков", "Вы приносите домой немного.", money=40, mood=-2, health=-1, smarts=-1),
    O("Уйти в комнату", "Тяжёлый вечер.", mood=-6)], ages=(10, 17), st=SCH)
E("s_trip", "Школьная поездка в другой город.", [
    O("Поехать", "Незабываемо!", money=-20, mood=8, smarts=1, karma=1),
    O("Остаться", "Тишина дома.", mood=-2)], ages=(9, 17), st=SCH)
E("s_phone", "Вы мечтаете о новом смартфоне.", [
    O("Выпросить у родителей", "Родители соглашаются.", p=.5, mood=10, looks=1, f=dict(mood=-3), r2="Услышали «нет»."),
    O("Копить на карманных", "Через пару месяцев цель близка.", mood=1, smarts=1)], ages=(10, 17), st=SCH)

# --- шкала «вредных» цепочек ---
E("caught_school", "Учитель застаёт вас с поличным и ведёт к завучу.", [
    O("Признаться", "Честность чуть смягчает наказание.", karma=1, mood=-4, wipe=1, s=(1, "cs_parents")),
    O("Всё отрицать", "Улик нет — отпускают.", p=.35, mood=3, f=dict(karma=-4, mood=-3, wipe=1), r2="Вам не верят.", sf=(1, "cs_parents"))], start=False)
E("cs_parents", "Родителей вызывают в школу. Дома тяжёлый разговор.", [
    O("Выслушать и пообещать бросить", "Родители остывают.", karma=2, mood=-8, nic=-5),
    O("Огрызнуться", "Карманные деньги отобраны.", karma=-3, mood=-5, money=-20)], start=False)
E("caught_home", "Родители находят следы вредных привычек: запах, пачку или бутылки.", [
    O("Признаться", "Тяжёлый разговор. Всё выброшено.", karma=2, mood=-6, wipe=1),
    O("Свалить на друзей", "Родители не очень верят.", p=.4, karma=-1, mood=-1, f=dict(karma=-4, mood=-6, wipe=1), r2="Ложь вскрывается, всё выброшено.")], start=False)
E("shop_snitch", "Продавец звонит вашим родителям.", [
    O("Извиниться", "Вас отчитывают, но прощают.", karma=1, mood=-6, wipe=1),
    O("Сказать, что всё враньё", "Не сработало, скандал.", karma=-3, mood=-6, wipe=1)], start=False)

# --- взрослые ---
E("edu_choice", "Вам 18! Что дальше?", [
    O("🎓 Поступать в университет", "Вы поступаете! Впереди 4 года учёбы.", p="smarts", student=1, mood=6, f=dict(mood=-6), r2="Баллов не хватило."),
    O("💼 Идти работать", "Взрослая жизнь началась. Загляните в «💼 Работа».", mood=2),
    O("🏖 Взять паузу", "Год для себя.", mood=6)], start=False)
E("a_boss", "Начальник просит остаться на сверхурочные.", [
    O("Остаться", "Деньги капнули, силы уплыли.", money=150, health=-3, mood=-3, xp=1),
    O("Отказаться", "Начальник недоволен.", mood=2, karma=-2)], st=WORKING, ages=(18, 70))
E("a_raise", "Вы решаетесь попросить повышение зарплаты.", [
    O("Идти к начальнику", "Вам повышают оклад!", p=.4, money=500, xp=3, mood=8, f=dict(mood=-4), r2="Пока рано.")], st=WORKING, ages=(18, 70))
E("a_fired", "Компания сокращает штат.", [
    O("Просить оставить", "Вас оставляют.", p=.5, mood=2, f=dict(fired=1, mood=-12), r2="Вас всё равно увольняют."),
    O("Уйти и искать другое", "Свобода и неопределённость.", fired=1, mood=-4)], st=WORKING, ages=(20, 62), w=.5)
E("a_bar", "Друзья зовут в бар.", [
    O("Пойти", "Вечер удался. Утром — туман.", money=-40, mood=8, alc=4, health=-1, s=(1, "a_hangover")),
    O("Остаться дома", "Тишина и сериал.", mood=1)], ages=(18, 70), w=1.3)
E("a_hangover", "Утро после вечеринки. Голова раскалывается.", [
    O("Лежать весь день", "К вечеру отпускает.", health=-1, mood=-3),
    O("Идти по делам", "Тяжело, но вы держитесь.", health=-3, karma=1)], start=False)
E("a_blackout", "Провал в памяти: утром нет телефона и денег.", [
    O("Заблокировать карты", "Урок усвоен.", money=-120, mood=-8, alc=-5)], start=False)
E("a_date", "Вы знакомитесь с интересным человеком.", [
    O("Пригласить на свидание", "Искра пробегает!", p=.6, money=-30, mood=10, partner=1, f=dict(mood=-5, money=-30), r2="Свидание не клеится."),
    O("Пройти мимо", "Может, в другой раз.", mood=-1)], ages=(16, 60), cond=lambda u: not u["partner"])
E("a_marry", "Партнёр намекает на свадьбу.", [
    O("Сделать предложение (кольцо)", "Она/он говорит «да»!", need=2000, money=-2000, married=1, mood=15),
    O("Пока рано", "Разговор откладывается.", mood=-2)], ages=(20, 60), cond=lambda u: u["partner"] and not u["married"])
E("a_kid", "В семье ждут пополнение!", [
    O("Радоваться", "Появляется малыш!", kids=1, mood=12, money=-300),
    O("Пока не готовы", "Решаете подождать.", mood=-1)], ages=(21, 45), cond=lambda u: u["married"] and u["kids"] < 3)
E("a_sick", "Вы заболели.", [
    O("Лечиться дома", "Через неделю лучше.", health=-2, mood=-2),
    O("К врачу", "Назначают лечение.", money=-80, health=3)], ages=(18, 120), w=1.2)
E("a_scam", "Звонок «из банка»: просят назвать код из смс.", [
    O("Положить трубку", "Мошенники остаются ни с чем.", mood=1, karma=1),
    O("Поверить", "Деньги со счёта пропадают.", money=-600, mood=-8)], ages=(18, 120))
E("a_leak", "Ваши данные утекли в сеть: звонят незнакомцы.", [
    O("Сменить номер и пароли", "Хлопотно, но спокойно.", money=-30, mood=-2),
    O("Забить", "Кто-то оформляет на вас кредит.", p=.5, mood=0, f=dict(money=-300, mood=-6), r2="Кредит на вас оформили.")], ages=(16, 120), w=.8)
E("a_crypto", "Друг зовёт вложиться в «верную» крипту.", [
    O("Вложить $500", "Токен взлетает!", need=500, p=.4, money=1500, f=dict(money=-500, mood=-6), r2="Токен рухнул."),
    O("Не вкладываться", "Спокойный сон дороже.", mood=1)], ages=(18, 80), w=.8)
E("a_street", "Незнакомец предлагает «лёгкий» заработок без вопросов.", [
    O("Согласиться", "Деньги быстрые.", p=.6, money=400, heat=10, karma=-5, f=dict(heat=10, karma=-5), r2="Это ловушка: приезжает полиция.", nf="cr_police"),
    O("Отказаться", "Вы идёте своей дорогой.", karma=1)], ages=(16, 55), w=.8)
E("a_vacation", "Скопились силы на отпуск.", [
    O("Заграничный отпуск", "Море и новые впечатления.", need=1200, money=-1200, mood=15, health=5),
    O("Отдохнуть дома", "Диван и сериалы.", mood=4, health=2)], ages=(20, 75), cond=lambda u: u["money"] > 500)
E("a_midlife", "Кризис среднего возраста.", [
    O("Купить мотоцикл", "Ветер в лицо!", need=3000, money=-3000, mood=12),
    O("Сменить работу", "Вы бросаете прежнее.", fired=1, mood=4),
    O("Терпеть", "Скучно, но стабильно.", mood=-4)], ages=(40, 55), w=.8)
E("a_cancer", "Врач находит подозрительное пятно на снимке.", [
    O("Лечение", "Врачи борются за вас.", need=3000, p=.65, money=-3000, health=-10, f=dict(money=-3000, health=-35), r2="Лечение почти не помогает."),
    O("Бросить курить, лечиться дома", "Организм сопротивляется.", health=-20, mood=-8, quit=1)], ages=(35, 120), w=.6, cond=lambda u: u["smoke_m"] >= 96)
E("a_pet", "Вам предлагают взять щенка.", [
    O("Забрать", "В доме появляется друг!", mood=9, money=-80, fit=2),
    O("Отказаться", "Слишком много хлопот.", mood=-1)], ages=(8, 80))
E("a_gift", "У близкого человека день рождения.", [
    O("Подарок со смыслом", "Он тронут до слёз.", money=-50, karma=3, mood=3),
    O("Просто открытка", "Дёшево, но от души.", karma=1)], ages=(12, 100))
E("city", "Прогулка по городу. {c}", [
    O("Поучаствовать", "Настроение растёт.", money=-15, mood=5, karma=1),
    O("Пройти мимо", "Всё как обычно.")], ages=(8, 100), w=1.1)
E("a_old1", "Давление шалит, голова кружится.", [
    O("К врачу", "Назначают лекарства.", money=-100, health=4),
    O("Потерпеть", "Сегодня лучше.", health=-4)], ages=(63, 120), st=OLD)
E("a_old2", "К вам приехали внуки и родные.", [
    O("Устроить большой обед", "Шумно и тепло.", money=-80, mood=12),
    O("Посидеть на веранде", "Тихая радость.", mood=5)], ages=(63, 120), st=OLD)
E("a_old3", "Старые друзья зовут на встречу выпускников.", [
    O("Пойти", "Столько воспоминаний!", mood=10, money=-30),
    O("Не ходить", "Остаётесь дома.", mood=-3)], ages=(60, 120), st=OLD)

# --- полиция и тюрьма ---
E("cr_police", "Вас задерживают. Полиция допрашивает вас.", [
    O("Нанять адвоката", "Адвокат помогает: дело смягчено.", need=800, p=.7, money=-800, heat=-10, n="court_light", f=dict(money=-800), r2="Адвокат не справился.", nf="court_hard"),
    O("Дать взятку", "Дело «теряется».", need=500, p=.4, money=-500, karma=-4, f=dict(money=-500, karma=-4), r2="Взятку не берут и добавляют статью.", nf="court_hard"),
    O("Признать вину", "Суд учтёт раскаяние.", karma=3, n="court_light")], start=False)
E("court_light", "Суд: штраф и условный срок.", [
    O("Принять", "Вы отделались легко.", money=-400, record=1, mood=-8, heat=-15)], start=False)
E("court_hard", "Суд: реальный срок 8 месяцев.", [
    O("Принять приговор", "Дверь закрывается.", prison=8, record=1, mood=-15, heat=-20)], start=False)
E("cr_police_minor", "Вас приводят в отделение и звонят родителям.", [
    O("Извиниться", "Родители забирают вас, дома — разговор.", karma=1, mood=-6, record=1),
    O("Молчать", "Вас отпускают, но на учёт ставят.", karma=-2, mood=-4, record=1)], start=False)
E("p_fight", "В камере назревает конфликт.", [
    O("Постоять за себя", "Вас теперь уважают.", health=-6, karma=1),
    O("Уйти от драки", "Вы терпите унижение.", mood=-4)], st=PRI, ages=(16, 120))
E("p_read", "В тюремной библиотеке пыльные книги.", [
    O("Читать", "Время летит быстрее.", smarts=3, mood=2),
    O("Валяться на нарах", "Тоска.", mood=-4)], st=PRI, ages=(16, 120))
E("p_gym", "Во дворе тюрьмы есть турник.", [
    O("Заниматься", "Вы в отличной форме.", fit=5, health=2, looks=1),
    O("Играть в карты", "Время идёт.", mood=1, karma=-1)], st=PRI, ages=(16, 120))

# ===================== вспомогательное =====================
def clamp(v):
    return max(0.0, min(100.0, v))

def cmult(u): return CITIES[u["city"]][2]
def pmult(u): return CITIES[u["city"]][1]
def price(u, base): return max(1, round(base * cmult(u)))

def status(u):
    if u["prison"] > 0: return "prison"
    a = u["age"]
    if a < 7: return "kid"
    if a < 18: return "school"
    if u["stud"] > 0: return "student"
    if u["job"]: return "work"
    if a >= 63: return "old"
    return "free"

def status_label(u):
    s = status(u)
    if s == "work": return "💼 " + JOBS[u["job"]][1][u["lvl"]]
    return {"prison": "⛓ В тюрьме", "kid": "👶 Ребёнок", "school": "🎒 Школьник", "student": "🎓 Студент", "free": "🔎 Без работы", "old": "🧓 Пенсионер"}[s]

def new_game(city, name):
    wealth = random.choices([0, 1, 2], [.4, .45, .15])[0]
    return dict(name=name, city=city, age=0, month=random.randrange(12), health=random.randint(60, 95), mood=70.0,
                smarts=random.randint(25, 90), looks=random.randint(25, 90), karma=50.0, nic=0.0, alc=0.0, game=0.0, heat=0.0, fit=30.0, crime=0.0,
                money=0, wealth=wealth, job=None, lvl=0, xp=0, stud=0, edu=False, partner=False, married=False, kids=0, record=0, prison=0,
                inv={}, sched=[], recent=[], ev=None, acted=False, used_nic=False, used_alc=False, cans=0, drunk=0, smoke_m=0, pc=False,
                total=0, over=None)

def apply(u, eff):
    cm = cmult(u)
    for k, v in eff.items():
        if k == "money": u["money"] += round(v * cm)
        elif k in STATS: u[k] = clamp(u[k] + v)
        elif k.startswith("inv_"): u["inv"][k[4:]] = u["inv"].get(k[4:], 0) + v
        elif k == "wipe":
            for i in ("cig", "ashka", "pod", "beer"): u["inv"][i] = 0
        elif k == "fired": u["job"] = None; u["lvl"] = 0; u["xp"] = 0
        elif k == "prison": u["prison"] = v; u["job"] = None; u["lvl"] = 0; u["xp"] = 0; u["stud"] = 0
        elif k == "student": u["stud"] = 48
        elif k == "quit": u["nic"] = 0
        elif k in ("partner", "married"): u[k] = True
        elif k in ("kids", "record"): u[k] += v
        elif k == "xp": u["xp"] += v

def check_over(u):
    if u["over"]: return True
    if u["health"] <= 0:
        u["over"] = "💀 Здоровье не выдержало."
    return bool(u["over"])

def resolve(u, opt, auto=False):
    cm = cmult(u)
    if opt["need"] and u["money"] < opt["need"] * cm and not auto: return None
    p = opt["p"]
    if p == "smarts": p = max(.1, min(.95, .25 + u["smarts"] / 130))
    ok = p is None or random.random() < p
    apply(u, opt["e"] if ok else opt["f"])
    txt = opt["r"] if ok else (opt["r2"] or "Не вышло.")
    n = opt["n"] if ok else opt["nf"]
    s = opt["s"] if ok else opt["sf"]
    if s and not auto: u["sched"].append([s[0], s[1]])
    return txt, (None if auto else n)

def birthday(u):
    notes = ["🎂 Вам исполнилось %d." % u["age"]]
    a = u["age"]
    if a == 7: notes.append("🏫 Вы идёте в школу!")
    if a == 18:
        u["sched"].append([0, "edu_choice"])
    if a == 63 and u["job"]:
        notes.append("🎉 Вы выходите на пенсию."); u["job"] = None; u["lvl"] = 0
    p = 0
    if a >= 60: p = (a - 58) ** 2 / 6000
    if u["health"] < 30: p += (30 - u["health"]) / 400
    if a >= 100 or random.random() < p:
        u["over"] = "🕯 Жизнь подошла к концу."
    return notes

def tick(u):
    notes = []
    for x in u["sched"]: x[0] -= 1
    u["month"] += 1
    if u["month"] >= 12:
        u["month"] = 0; u["age"] += 1
        notes += birthday(u)
    u["total"] += 1
    st = status(u)
    pm, cm = pmult(u), cmult(u)
    inc = exp = 0
    if st != "prison":
        if u["job"]:
            j = JOBS[u["job"]]
            pay = j[2][u["lvl"]] * pm
            if j[5]: pay *= random.uniform(*j[5])
            inc += pay
            u["xp"] += 1
            if u["lvl"] < 3 and u["xp"] >= PROMO[u["lvl"]] and u["karma"] >= 15:
                u["lvl"] += 1; u["xp"] = 0
                notes.append("🎉 Повышение! Теперь вы — %s." % j[1][u["lvl"]])
            if u["job"] == "bandit":
                u["heat"] = clamp(u["heat"] + 3); u["karma"] = clamp(u["karma"] - 1)
                if random.random() < .05: u["sched"].append([0, "cr_police"])
        if u["age"] >= 63 and not u["job"]: inc += 500 * pm
        if 10 <= u["age"] < 18: inc += [15, 40, 100][u["wealth"]] * cm
        if u["stud"] > 0:
            inc += 150 * cm + [50, 150, 400][u["wealth"]] * cm
        if u["age"] >= 18:
            exp += 600 * cm * (0.5 if u["stud"] > 0 else 1) + u["kids"] * 200 * cm
        u["money"] += round(inc - exp)
        if round(inc) or round(exp):
            notes.append("💰 Доход +$%d, расходы −$%d." % (inc, exp))
        if u["money"] < 0:
            u["money"] = round(u["money"] * 1.015); u["mood"] = clamp(u["mood"] - 2)
            notes.append("📉 Вы в долгах.")
    else:
        u["prison"] -= 1
        if u["prison"] <= 0: notes.append("🔓 Вы освобождены!")
    if u["stud"] > 0:
        u["stud"] -= 1
        if u["stud"] == 0:
            u["edu"] = True; notes.append("🎓 Вы окончили университет!")
    # здоровье и привычки
    a = u["age"]
    u["health"] = clamp(u["health"] - (0.1 if a < 40 else 0.3 if a < 60 else 0.7))
    if u["used_nic"]:
        u["smoke_m"] += 1; u["health"] = clamp(u["health"] - 0.3)
    elif u["nic"] >= 15:
        u["mood"] = clamp(u["mood"] - u["nic"] / 10)
        u["nic"] = max(0, u["nic"] - 2.5)
        notes.append("🚬 Тянет закурить — настроение падает.")
    if u["used_alc"]: u["health"] = clamp(u["health"] - 0.3)
    else:
        if u["alc"] >= 40:
            u["mood"] = clamp(u["mood"] - 4); notes.append("🍺 Хочется выпить.")
        u["alc"] = max(0, u["alc"] - 3)
    if u["cans"] >= 4: u["health"] = clamp(u["health"] - 3)
    u["heat"] = max(0, u["heat"] - 1.5)
    u["used_nic"] = u["used_alc"] = u["acted"] = False
    u["cans"] = u["drunk"] = 0
    check_over(u)
    return notes

def pick_event(u):
    due = [x for x in u["sched"] if x[0] <= 0]
    if due:
        u["sched"].remove(due[0]); return due[0][1]
    st, a = status(u), u["age"]
    pool, ws = [], []
    for n in NODES.values():
        if not n["start"] or not (n["a"][0] <= a <= n["a"][1]) or n["id"] in u["recent"]: continue
        if st == "prison":
            if not n["st"] or "prison" not in n["st"]: continue
        elif n["st"] and st not in n["st"]: continue
        if n["cond"] and not n["cond"](u): continue
        pool.append(n["id"]); ws.append(n["w"])
    if not pool: return None
    nid = random.choices(pool, ws)[0]
    u["recent"] = (u["recent"] + [nid])[-6:]
    return nid

# ===================== экраны =====================
def bar(v): return str(int(round(v)))

def card(u):
    c = CITIES[u["city"]]
    t = "📅 %s, %d лет · %s\n%s · %s\n💰 $%d\n" % (MONTHS[u["month"]], u["age"], u["name"], c[0], status_label(u), u["money"])
    t += "❤️%s 😊%s 🧠%s 😎%s ⭐%s" % tuple(bar(u[k]) for k in ("health", "mood", "smarts", "looks", "karma"))
    if u["nic"] >= 5 or u["alc"] >= 5:
        t += "\n🚬%s 🍺%s" % (bar(u["nic"]), bar(u["alc"]))
    return t

def hub_rows(u):
    st, a = status(u), u["age"]
    rows = [[("▶️ Следующий месяц", "next")]]
    if st == "prison":
        rows.append([("📊 Профиль", "prof")]); return rows
    if a < 7:
        rows.append([("⏩ Пропустить год", "skip")]); return rows
    r = [("🏪 Магазин", "shop")]
    if a >= 10: r.append(("🎒 Вещи", "use"))
    rows.append(r)
    r = [("🎯 Действия", "act")]
    if a >= 14: r.append(("💼 Работа", "job"))
    rows.append(r)
    rows.append([("📊 Профиль", "prof")])
    return rows

def hub(u, prefix=""):
    if u["over"]: return over_screen(u)
    return (prefix + "\n\n" if prefix else "") + card(u), hub_rows(u)

def over_screen(u):
    j = JOBS[u["job"]][1][u["lvl"]] if u["job"] else "без работы"
    score = int(u["money"] / 100 + u["health"] + u["mood"] + u["smarts"] + u["karma"] + u["lvl"] * 40 + u["kids"] * 30 - u["record"] * 20)
    t = "%s\n\n%s прожил(а) %d лет в городе %s.\nИтог: %s, 💰$%d, детей: %d, судимостей: %d.\n🏆 Очки: %d" % (
        u["over"], u["name"], u["age"], CITIES[u["city"]][0], j, u["money"], u["kids"], u["record"], score)
    return t, [[("🔄 Новая жизнь", "again")]]

def event_screen(u, prefix=""):
    node = NODES[u["ev"]]; cm = cmult(u)
    text = node["text"].replace("{c}", CITIES[u["city"]][3])
    rows = []
    for i, o in enumerate(node["opts"]):
        lab = o["t"] + (" (💰%d)" % round(o["need"] * cm) if o["need"] else "")
        rows.append([(lab, "ch:%d" % i)])
    return prefix + card(u) + "\n\n❓ " + text, rows

def intro(u):
    w = ["небогатой", "обычной", "состоятельной"][u["wealth"]]
    t = "👶 %s родился(-ась) в городе %s в %s семье.\nУ вас впереди целая жизнь: детство, школа, выбор профессии, друзья, соблазны и риски. Каждый ход — месяц, год — 12 событий." % (u["name"], CITIES[u["city"]][0], w)
    return t + "\n\n" + card(u), [[("▶️ Начать жизнь", "next")]]

def city_menu():
    keys = list(CITIES)
    rows = [[(CITIES[k][0], "city:" + k) for k in keys[i:i + 2]] for i in range(0, len(keys), 2)]
    return "🎮 Твоя жизнь. Ты рождаешься заново. Выбери город рождения:", rows

# ===================== действия =====================
ACTS = {
    "game": ("🎮 Играть в игры", 5), "study": ("📚 Учиться", 6), "sport": ("🏋 Заняться спортом", 6),
    "rest": ("🛌 Отдохнуть", 3), "party": ("🎉 Тусовка (−$30)", 15), "date": ("❤️ Свидание", 15),
    "side": ("🛠 Подработка", 14), "crime": ("🕶 Криминал", 10)}
CRIMES = {
    "shop": ("🛍 Украсть в магазине", 10, .65, (20, 90), 4, 4),
    "phone": ("📱 Вырвать телефон", 14, .5, (150, 500), 10, 8),
    "data": ("💾 Взломать и продать чужие данные", 15, .4, (500, 3000), 12, 6),
    "scam": ("☎️ Обмануть людей по телефону", 16, .55, (300, 1500), 9, 6),
    "rob": ("🏦 Ограбить кассу", 18, .3, (3000, 12000), 25, 15)}

def act_menu(u, prefix=""):
    st = status(u); rows = []
    for k, (lab, mn) in ACTS.items():
        if u["age"] < mn: continue
        if st == "prison" and k not in ("study", "sport", "rest"): continue
        rows.append([(lab, "do:" + k)])
    rows.append([("⬅️ Назад", "menu")])
    return prefix + "🎯 Чем займётесь в этом месяце? (одно дело за месяц)", rows

def do_act(u, k):
    if u["acted"]: return hub(u, "⏳ В этом месяце вы уже занимались делами. Жмите «Следующий месяц».")
    cm, pm = cmult(u), pmult(u)
    if k == "crime":
        rows = [[(v[0], "cr:" + c)] for c, v in CRIMES.items() if u["age"] >= v[1]]
        return "🕶 Криминал — риск арестом. Розыск: %d/100. Выбирайте осторожно." % u["heat"], rows + [[("⬅️ Назад", "act")]]
    u["acted"] = True
    msg = ""
    if k == "game":
        apply(u, dict(mood=7, game=3, smarts=-.5)); msg = "Вы весь вечер в игре. Скилл растёт!"
        if u["game"] >= 60 and random.random() < .25:
            g = random.randint(100, 400); u["money"] += g; msg += " 🏆 Выиграли онлайн-турнир: +$%d." % g
    elif k == "study": apply(u, dict(smarts=3, mood=-2)); msg = "Вы учитесь. Знания копятся."
    elif k == "sport": apply(u, dict(fit=3, health=2, looks=1, mood=1)); msg = "Тренировка бодрит."
    elif k == "rest": apply(u, dict(health=4, mood=5)); msg = "Вы просто отдыхаете."
    elif k == "party":
        if u["money"] < 30 * cm: u["acted"] = False; return hub(u, "Не хватает денег на тусовку.")
        apply(u, dict(money=-30, mood=9, health=-1)); msg = "Тусовка удалась!"
        if not u["partner"] and random.random() < .15: u["partner"] = True; msg += " ❤️ Вы познакомились с кем-то особенным."
    elif k == "date":
        if not u["partner"]:
            if random.random() < .4 + u["looks"] / 300:
                u["partner"] = True; apply(u, dict(mood=10, money=-20)); msg = "❤️ Свидание удалось — вы вместе!"
            else: apply(u, dict(mood=-5)); msg = "Свидание не сложилось."
        else: apply(u, dict(mood=8, money=-30)); msg = "Романтичный вечер с партнёром."
    elif k == "side":
        g = round(random.randint(80, 250) * pm); u["money"] += g; apply(u, dict(health=-1.5, mood=-1)); msg = "Подработка принесла $%d." % g
    return hub(u, "➡️ " + msg)

def do_crime(u, c):
    if u["acted"]: return hub(u, "⏳ В этом месяце вы уже занимались делами.")
    n, mn, p, rew, heat, kar = CRIMES[c]
    u["acted"] = True
    p = max(.1, min(.9, p - u["heat"] / 300 + u["crime"] / 250))
    if random.random() < p:
        g = round(random.randint(*rew) * pmult(u)); u["money"] += g
        apply(u, dict(heat=heat, karma=-kar, crime=2, mood=2))
        return hub(u, "➡️ Удалось! +$%d. Но розыск растёт." % g)
    apply(u, dict(heat=heat, karma=-kar, mood=-4))
    u["ev"] = "cr_police_minor" if u["age"] < 18 else "cr_police"
    return event_screen(u, "🚨 Вас поймали!\n\n")

# --- магазин ---
def shop(u, prefix=""):
    a = u["age"]; rows = []
    for k, (n, base, qty, adult) in ITEMS.items():
        if a < 10: continue
        rows.append([("%s%s — $%d" % ("🔞 " if adult else "", n, price(u, base)), "buy:" + k)])
    for k, (n, base, eff, mn) in SHOP_ONE.items():
        if a >= mn: rows.append([("%s — $%d" % (n, price(u, base)), "buy:" + k)])
    rows.append([("⬅️ Назад", "menu")])
    return prefix + "🏪 Магазин. В кармане 💰$%d" % u["money"], rows

def buy(u, key, mode=None):
    cm = cmult(u)
    if key in SHOP_ONE:
        n, base, eff, mn = SHOP_ONE[key]; pr = price(u, base)
        if u["money"] < pr: return shop(u, "Не хватает денег.\n")
        if key == "pc" and u["pc"]: return shop(u, "ПК у вас уже есть.\n")
        u["money"] -= pr
        if key == "pc": u["pc"] = True
        if key == "lot":
            r = random.random()
            if r < .02: g = pr * 200; u["money"] += g; return shop(u, "🎰 ДЖЕКПОТ! +$%d\n" % g)
            if r < .17: g = pr * 3; u["money"] += g; return shop(u, "Выигрыш $%d!\n" % g)
            return shop(u, "Билет пустой.\n")
        raw = {k: v for k, v in eff.items()}
        for k2, v in raw.items():
            if k2 in STATS: u[k2] = clamp(u[k2] + v)
        return shop(u, "Куплено: %s.\n" % n)
    n, base, qty, adult = ITEMS[key]; pr = price(u, base)
    if adult and u["age"] < 18 and mode is None:
        return "🔞 Продавец смотрит на вас с подозрением. Как будете брать?", [
            [("🍀 Попробовать самому (шанс)", "bys:" + key)],
            [("🧑 Попросить старшего (×1.6 цена)", "byo:" + key)], [("⬅️ Назад", "shop")]]
    if mode == "o": pr = round(pr * 1.6)
    if u["money"] < pr: return shop(u, "Не хватает денег.\n")
    if mode == "s":
        p = max(.05, min(.6, .1 + .05 * (u["age"] - 10) + (u["looks"] - 50) / 300))
        if random.random() >= p:
            if random.random() < .3:
                u["ev"] = "shop_snitch"; return event_screen(u, "🚫 Продавец отказывает.\n\n")
            return shop(u, "🚫 Продавец требует паспорт и отказывает.\n")
    u["money"] -= pr; u["inv"][key] = u["inv"].get(key, 0) + qty
    return shop(u, "Куплено: %s.\n" % n)

def use_menu(u, prefix=""):
    rows = [[("%s (%d)" % (ITEM_USE[k], v), "use:" + k)] for k, v in u["inv"].items() if v > 0 and k in ITEM_USE]
    rows.append([("⬅️ Назад", "menu")])
    t = "🎒 Что используем?" if len(rows) > 1 else "🎒 Пока ничего нет. Загляните в магазин."
    return prefix + t, rows

PLACES = {"t": ("🚽 В туалете школы", .35), "g": ("🌳 За гаражами / во дворе", .2), "h": ("🏠 Дома тайком", .15), "o": ("🌳 На улице", 0), "d": ("🏠 Дома", 0)}

def use_item(u, k):
    if u["inv"].get(k, 0) <= 0: return use_menu(u, "Этого нет.\n")
    if k == "energy": return do_use(u, k, "o")
    if u["age"] < 18:
        keys = ["t", "g", "h"] if (k != "beer" and status(u) == "school") else ["g", "h"]
        return "Где будете?", [[(PLACES[x][0], "pl:%s:%s" % (k, x))] for x in keys] + [[("⬅️ Назад", "use")]]
    return "Где будете?", [[(PLACES[x][0], "pl:%s:%s" % (k, x))] for x in ("o", "d")] + [[("⬅️ Назад", "use")]]

def do_use(u, k, place):
    u["inv"][k] -= 1
    msg = ""
    if k in ("cig", "ashka", "pod"):
        apply(u, dict(nic={"cig": 8, "ashka": 5, "pod": 6}[k], mood=4, health=-.6)); u["used_nic"] = True
        msg = "Вы затягиваетесь. Голова слегка плывёт, на душе спокойнее."
    elif k == "beer":
        apply(u, dict(alc=7, mood=6, health=-1.2)); u["used_alc"] = True; u["drunk"] += 1; msg = "Холодное пиво, на душе легче."
    elif k == "energy":
        apply(u, dict(mood=3, health=-1)); u["cans"] += 1; msg = "Бодрость и лёгкое сердцебиение."
        if u["cans"] >= 4: apply(u, dict(health=-6)); msg += " Но сердце колотится, как бешеное: хватит!"
    if k == "beer" and u["drunk"] >= 4:
        u["drunk"] = 0; u["ev"] = "a_blackout"; return event_screen(u, "➡️ Вы перебрали...\n\n")
    if random.random() < PLACES[place][1]:
        u["ev"] = "caught_school" if place == "t" else "caught_home"
        return event_screen(u, "➡️ %s\n😱 Но вас замечают!\n\n" % msg)
    return use_menu(u, "➡️ %s\n" % msg)

# --- работа ---
def job_menu(u, prefix=""):
    rows = []
    if u["job"]:
        rows.append([("🚪 Уволиться", "quit")])
    for k, j in JOBS.items():
        if u["age"] >= j[3]:
            rows.append([("%s — $%d/мес" % (j[0], round(j[2][0] * pmult(u))), "ap:" + k)])
    rows.append([("⬅️ Назад", "menu")])
    cur = "Сейчас: %s (опыт %d мес)" % (JOBS[u["job"]][1][u["lvl"]], u["xp"]) if u["job"] else "Сейчас вы без работы."
    return prefix + "💼 " + cur + "\nВыберите, куда устроиться:", rows

def apply_job(u, k):
    j = JOBS[k]; req = j[4]; why = []
    if req.get("edu") and not u["edu"]: why.append("нужен диплом")
    if req.get("norec") and u["record"]: why.append("нужна чистая репутация (есть судимость)")
    for key, label in (("smarts", "ум"), ("looks", "внешность"), ("fit", "форма"), ("health", "здоровье"), ("game", "игровой скилл"), ("crime", "опыт в криминале")):
        if req.get(key) and u[key] < req[key]: why.append("%s %d+" % (label, req[key]))
    if req.get("money") and u["money"] < req["money"] * cmult(u): why.append("стартовый капитал $%d" % (req["money"] * cmult(u)))
    if k == "athlete" and u["age"] > 33: why.append("слишком поздно для спорта")
    if why: return job_menu(u, "❌ Не подходите: " + ", ".join(why) + ".\n\n")
    p = max(.2, min(.9, .35 + u["smarts"] / 250 + u["karma"] / 400 - u["record"] * .1))
    if random.random() < p:
        u["job"] = k; u["lvl"] = 0; u["xp"] = 0
        return hub(u, "✅ Вас берут: %s!" % j[0])
    return job_menu(u, "😕 В этот раз отказали. Попробуйте ещё.\n\n")

def profile(u):
    c = CITIES[u["city"]]
    t = ["📊 %s, %d лет, %s" % (u["name"], u["age"], c[0]), card(u), "",
         "🧠 Ум %d · 😎 Внешность %d · 💪 Форма %d" % (u["smarts"], u["looks"], u["fit"]),
         "🎮 Игровой скилл %d · 🕶 Розыск %d" % (u["game"], u["heat"]),
         "❤️ Партнёр: %s · 💍 Брак: %s · 👶 Детей: %d" % ("да" if u["partner"] else "нет", "да" if u["married"] else "нет", u["kids"]),
         "🎓 Диплом: %s · ⚖️ Судимостей: %d" % ("есть" if u["edu"] else "нет", u["record"]),
         "🎒 " + (", ".join("%s×%d" % (ITEMS[k][0].split(' ')[0], v) for k, v in u["inv"].items() if v > 0 and k in ITEMS) or "пусто")]
    return "\n".join(t), [[("⬅️ Назад", "menu")]]

def skip_year(u):
    lines = []
    for _ in range(12):
        notes = tick(u)
        if u["over"]: break
        nid = pick_event(u)
        if nid and NODES[nid]["opts"]:
            r = resolve(u, random.choice(NODES[nid]["opts"]), auto=True)
            if r and r[0]: lines.append(r[0])
        if u["age"] >= 7: break
    show = random.sample(lines, min(3, len(lines)))
    return hub(u, "⏩ Год пролетает.\n" + "\n".join("• " + x for x in show))

# ===================== главный обработчик =====================
def handle(u, data):
    if u["over"]: return over_screen(u)
    if u["ev"] and data != "next" and not data.startswith("ch:"):
        return event_screen(u, "Сначала выберите вариант.\n\n")
    if data == "next":
        if u["ev"]: return event_screen(u)
        notes = tick(u)
        if u["over"]: return over_screen(u)
        nid = pick_event(u)
        pre = "\n".join(notes) + ("\n\n" if notes else "")
        if nid:
            u["ev"] = nid; return event_screen(u, pre)
        return hub(u, pre + "Тихий месяц.")
    if data.startswith("ch:"):
        if not u["ev"]: return hub(u)
        opt = NODES[u["ev"]]["opts"][int(data[3:])]
        r = resolve(u, opt)
        if r is None: return event_screen(u, "⚠️ Не хватает денег на этот вариант.\n\n")
        txt, nxt = r
        u["ev"] = None
        if check_over(u): return over_screen(u)
        if nxt:
            u["ev"] = nxt; return event_screen(u, "➡️ %s\n\n" % txt)
        return hub(u, "➡️ " + txt)
    if data == "menu": return hub(u)
    if data == "skip": return skip_year(u)
    if data == "prof": return profile(u)
    if data == "shop": return shop(u)
    if data.startswith("buy:"): return buy(u, data[4:])
    if data.startswith("bys:"): return buy(u, data[4:], "s")
    if data.startswith("byo:"): return buy(u, data[4:], "o")
    if data == "use": return use_menu(u)
    if data.startswith("use:"): return use_item(u, data[4:])
    if data.startswith("pl:"):
        _, k, pl = data.split(":"); return do_use(u, k, pl)
    if data == "act": return act_menu(u)
    if data.startswith("do:"): return do_act(u, data[3:])
    if data.startswith("cr:"): return do_crime(u, data[3:])
    if data == "job": return job_menu(u)
    if data.startswith("ap:"): return apply_job(u, data[3:])
    if data == "quit":
        u["job"] = None; u["lvl"] = 0; u["xp"] = 0; return hub(u, "Вы уволились.")
    return hub(u)
