import requests
import telebot
from bs4 import BeautifulSoup
from Timetable import Timetable
from Timetable import Lesson
from telebot import types
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from UserClass import User

pages = {}
time_update = 3600
time_now = datetime.now()
adminInfo = {}
teacherInfo = {}
timetablesend = []
lessonend = {}
users = {}
lessonsweek = []

token = ''


def LoadPages():
    global teachers
    global pages
    global admins
    global url
    global session
    global user_agent_val
    global adminInfo
    global teacherInfo
    global timetablesend
    global lessonend
    global lessonsweek
    delete = 0
    username = ''
    password = ''
    url = 'https://schools.by/login'
    user_agent_val = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
                     'Version/17.0 Safari/605.1.15'
    session = requests.Session()
    r = session.get(url, headers={
        'User-Agent': user_agent_val
    })
    session.headers.update({'Referer': url})
    session.headers.update({'User-Agent': user_agent_val})
    csrfmiddlewaretoken = session.cookies.get('csrftoken', domain=".schools.by")
    post_request = session.post(url, {
        'MIME Type': 'application/x-www-form-urlencoded',
        'csrfmiddlewaretoken': csrfmiddlewaretoken,
        'username': username,
        'password': password,
        '|123': '|123'
    })

    soup = BeautifulSoup(post_request.content, 'lxml')
    soupLinks = soup.find(class_='sch_menu_box').find_all('a')

    urlGymn = 'https://gymn3pinsk.schools.by'
    for links in soupLinks:
        link = links.get('href')
        alllink = f'{urlGymn}{link}'
        nameforpages = link.replace('/', '')
        page = session.get(alllink, headers={'User-Agent': user_agent_val})
        pages[nameforpages] = BeautifulSoup(page.content, 'lxml')

    admins = pages[list(pages.keys())[0]].find(class_="sch_ptbox_list").find_all(class_='sch_ptbox_item')

    for admin in admins:
        adminLink = f'{urlGymn}{admin.find(class_="photo").get("href")}'

        page = session.get(adminLink, headers={'User-Agent': user_agent_val})
        adminInfo[admin.find(class_='name').text] = BeautifulSoup(page.content, 'lxml')

    driver = webdriver.Safari()
    driver.get(urlGymn)

    for item in session.cookies:
        driver.add_cookie(
            {'httpOnly': False, 'name': item.name, 'value': item.value, 'domain': item.domain, 'path': item.path,
             'secure': item.secure})
    driver.refresh()
    driver.implicitly_wait(5)
    element = driver.find_element(By.CLASS_NAME, 'button_blue')
    element.click()
    time.sleep(1)

    timetables = pages[list(pages.keys())[4]].find(class_="sch_classes_list").find_all(class_="class")
    for timetable in timetables:
        try:
            timetablelink = f"{urlGymn}{timetable.find(class_='big').get('href')}/subgroups"

            page = session.get(timetablelink, headers={'User-Agent': user_agent_val})
            page = BeautifulSoup(page.content, 'lxml')

            dnevniklink = f"{urlGymn}" \
                          f"{page.find(class_='class_subgroups').find(class_='class_subgroup').find(class_='pupils').find(class_='user_type_1').get('href')}" \
                          f"#dnevnik"

            driver.get(dnevniklink)
            element = driver.find_element(By.CLASS_NAME, 'button_blue')
            element.click()
            driver.implicitly_wait(5)
            time.sleep(1)

            page = driver.page_source
            bs4page = BeautifulSoup(page, 'lxml')

            grade = bs4page.find(class_='grid_pst_c').find(class_='pp_line').find('a').text

            weekdays = bs4page.find(class_='db_week').find(class_='db_days clearfix').find_all(class_='db_table')
            delete += 1
            for weekday in weekdays:
                lessonsweek.clear()

                lessons = weekday.find_all(class_='lesson')

                hts = weekday.find_all(class_='ht-text-wrapper')
                print(hts)

                x = 0
                y = 0
                z = 0
                dayofweek = None
                for lesson in lessons:
                    if y == 0:
                        y += 1
                        dayofweek = lesson.text
                        lessonend[dayofweek] = None

                        continue

                    else:
                        if len(re.sub("^\s+|\n|\r|\s+$", '', lesson.text.replace(' ', ''))) > 3:
                            try:
                                lessonsweek.append(Lesson(
                                    re.sub("^\s+|\n|\r|\s+$", '', lesson.text.replace(' ', ''), flags=re.UNICODE),
                                    re.sub("^\s+|\n|\r|\s+$", '', hts[z].text)))
                                y += 1
                                z += 1
                            except:

                                lessonsweek.append(Lesson(
                                    re.sub("^\s+|\n|\r|\s+$", '', lesson.text.replace(' ', ''), flags=re.UNICODE),
                                    ' домашнего задания нет'))

                        x += 1

                        lessonend[dayofweek] = lessonsweek.copy()

            timetablesend.append(Timetable(grade, lessonend.copy()))
            try:
                timetablesend.pop(delete)
            except:
                continue
        except:
            continue


LoadPages()

bot = telebot.TeleBot(token, parse_mode=None)


@bot.message_handler(commands=['start', 'help', "Меню", "menu", "Menu", "Start", 'Help'])
def SendWelcome(message):
    global users
    global time_now

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    global admins_btn, feedback_btn, timetables_btn, hometask_btn
    try:
        users[message.chat.id].user_menu = 'menu'
        users[message.chat.id].grade_choosen = None
        users[message.chat.id].isokey = None


    except:
        users[message.chat.id] = User()
        users[message.chat.id].user_menu = 'menu'
        if message.chat.id == 479845437:
            users[message.chat.id].grade = '11-го "Б"'
        elif users[message.chat.id] == 763247529:
            users[message.chat.id].grade = '11-го "Б"'

    admins_btn = types.KeyboardButton("Администрация")

    feedback_btn = types.KeyboardButton("Контактная информация")
    timetables_btn = types.KeyboardButton('Расписание')
    hometask_btn = types.KeyboardButton('Домашнее задание')
    markup.add(admins_btn, feedback_btn, timetables_btn, hometask_btn)

    bot.send_message(message.chat.id, text=f'Здравствуйте, {message.chat.first_name}! Что вы хотите сделать?',
                     reply_markup=markup)

    tdelta = datetime.now() - time_now
    if time_update < tdelta.seconds:
        LoadPages()
        time_now = datetime.now()


@bot.message_handler(content_types=['text'])
def Buttons(message):
    global adminInfo, isokey
    global url
    global session
    global user_agent_val

    if users[message.chat.id].user_menu == "menu":
        if message.text == admins_btn.text:
            Administrations(message)
            users[message.chat.id].user_menu = "admin"
        elif message.text == feedback_btn.text:
            Feedback(message)
        elif message.text == timetables_btn.text:
            users[message.chat.id].ishometask = False
            Timetables(message)
        elif message.text == hometask_btn.text:
            if users[message.chat.id].grade is not None:
                users[message.chat.id].ishometask = True
                Timetables(message)
            else:
                bot.send_message(message.chat.id, text='Вы не авторизованы')
        else:
            bot.send_message(message.chat.id, text="Я таких команд не знаю")
    elif message.text == "Назад":
        SendWelcome(message)
    elif users[message.chat.id].user_menu == 'admin':
        x = 0
        for name in adminInfo:
            if name == message.text:

                info = adminInfo[message.text].find(class_='grid_st_c').find_all(class_='pp_line')
                try:
                    x = 0
                    msg = adminInfo[message.text].find(class_='title_box').find('h1').text + ': ' \
                          + adminInfo[message.text].find(class_='pp_line').find('b').find(class_='ttc').text \
                          + ' ' + adminInfo[message.text].find(class_='pp_line').find('b').find('a').text + "\n"
                    for information in info:
                        if x != 0:
                            msg = msg + re.sub("^\s+|\n|\r|\s+$", '', information.find(class_='label').text) + ' ' \
                                  + re.sub("^\s+|\n|\r|\s+$", '', information.find(class_='cnt').text) + '\n'
                        x = 1
                    bot.send_message(message.chat.id, msg)
                    prqwr = re.sub("^\s+|\n|\r|\s+$", '',
                                   adminInfo[message.text].find(class_='grid_st_c').find(class_='label').text)
                except:
                    x = 0
                    msg = adminInfo[message.text].find(class_='title_box').find('h1').text + ': ' \
                          + adminInfo[message.text].find(class_='pp_line').find('b').text \
                          + ' ' + adminInfo[message.text].find(class_='pp_line').find(class_='clr-gray').text + "\n"
                    for information in info:
                        if x > 1:
                            msg = msg + re.sub("^\s+|\n|\r|\s+$", '', information.find(class_='label').text) + ' ' \
                                  + re.sub("^\s+|\n|\r|\s+$", '', information.find(class_='cnt').text) + '\n'
                        x += 1
                    bot.send_message(message.chat.id, msg)
    elif users[message.chat.id].user_menu == 'timetable':
        if not users[message.chat.id].ishometask:
            if users[message.chat.id].isokey:
                Timetables(message)

            else:

                aaa = 0

                users[message.chat.id].grade_choosen = message.text
                for x in timetablesend:
                    print(x)
                    aaa += 1

                    if users[message.chat.id].grade_choosen == x.grade:
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        btn1 = types.KeyboardButton('Назад')
                        z = 0
                        for dayofweek in x.lessons:
                            btn = dayofweek
                            markup.add(btn)

                        markup.add(btn1)
                        msg = bot.send_message(message.chat.id, text='Выберите день недели на который нужно расписание',
                                               reply_markup=markup)
                        bot.register_next_step_handler(msg, wait)
                        users[message.chat.id].isokey = True
                        break
                    else:

                        continue

                if not users[message.chat.id].isokey:
                    bot.send_message(message.chat.id, text='Нет такого класса')
                    users[message.chat.id].grade_choosen = message.text = None
        elif users[message.chat.id].ishometask:
            if users[message.chat.id].isokey:
                Timetables(message)
            else:

                for x in timetablesend:

                    if users[message.chat.id].grade == x.grade:
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        btn1 = types.KeyboardButton('Назад')
                        for dayofweek in x.lessons:
                            btn = dayofweek
                            markup.add(btn)

                        markup.add(btn1)
                        msg = bot.send_message(message.chat.id, text='Выберите день недели на который нужно домашнее '
                                                                     'задание',
                                               reply_markup=markup)
                        bot.register_next_step_handler(msg, wait)
                        users[message.chat.id].isokey = True
                        break
                    else:

                        continue
            if not users[message.chat.id].isokey:
                bot.send_message(message.chat.id, text='Нет такого класса')


def wait(message):
    Timetables(message)


@bot.message_handler()
def Administrations(message):
    global admins
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Назад')
    markup.add(btn1)

    for admin in admins:
        bot.send_message(message.chat.id, text=f'{admin.find(class_="name").text}: {admin.find(class_="info").text}',
                         reply_markup=markup)
        markup.add(types.KeyboardButton(admin.find(class_="name").text))


@bot.message_handler()
def Feedback(message):
    feedback = pages[list(pages.keys())[8]].find(class_="sch_main_info island").text
    feedback = '\n'.join(el.strip() for el in feedback.split('\n') if el.strip()).replace("Редактировать информацию",
                                                                                          '')
    bot.send_message(message.chat.id, text=feedback)
    users[message.chat.id].user_menu = 'menu'


@bot.message_handler()
def Timetables(message):
    if users[message.chat.id].user_menu == 'timetable':
        if not users[message.chat.id].ishometask:
            try:
                for x in timetablesend:
                    if users[message.chat.id].grade_choosen == x.grade:
                        bot.send_message(message.chat.id, text=f'{x.GetTimetable(message.text)}')
                        break


            except:
                bot.send_message(message.chat.id, text='Неверный день недели')
        elif users[message.chat.id].ishometask:
            for x in timetablesend:
                if users[message.chat.id].grade == x.grade:
                    try:
                        bot.send_message(message.chat.id, text=f'{x.GetHomework(message.text)}')
                        break
                    except:
                        bot.send_message(message.chat.id, text='Неверный день недели')

    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Назад')
        markup.add(btn1)
        if not users[message.chat.id].ishometask:
            for x in timetablesend:
                grade = x.grade

                markup.add(types.KeyboardButton(grade))

            bot.send_message(message.chat.id, text='Выберите рассписание какого класса вас интересует',
                             reply_markup=markup)

            users[message.chat.id].user_menu = "timetable"
        if users[message.chat.id].ishometask:
            btn = types.KeyboardButton('Продолжить')
            markup.add(btn)
            bot.send_message(message.chat.id, text=f'Домашнее задание для "{users[message.chat.id].grade}"',
                             reply_markup=markup)
            users[message.chat.id].user_menu = "timetable"


bot.infinity_polling()
