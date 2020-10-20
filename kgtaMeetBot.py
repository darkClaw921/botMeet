import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

# VK API import
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api import VkUpload 

# OS import
import time
from threading import Thread
import threading

# Help files import
# import setings
import test 

# VK setings
vk_session = vk_api.VkApi(token = 'f35057fbf248d8041736e783c23d38ebf2de5e1fe1c403e64817c348e207cfdd397d6979c4688a945cc8f')
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

print('Создание таблицы ...')
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] # что то для чего-то нужно Костыль
# creds = ServiceAccountCredentials.from_json_keyfile_name('/home/igorgerasimovsid/ViktorinaProfkom-50c0fbdcd821.json', scope)
creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/igorgerasimov/Desktop/Python/KGTA/meetBot/ViktorinaProfkom-50c0fbdcd821.json', scope) # Секретынй файл json для доступа к API
client = gspread.authorize(creds)
sheet = client.open('RegisterForMeet').sheet1 # Имя таблицы

def createCell(countCell):
    sheet.update_cell(1, 1, "id пользователя")
    sheet.update_cell(1, 2, "Имя ")
    sheet.update_cell(1, 3, "Фамилия")
    sheet.update_cell(1, 4, "Куда")
    indexCell = 4

    for numberQues in range(countCell):
        indexCell += 1
        sheet.update_cell(1, indexCell, f"Вопрос {numberQues+1}") 

questionsData = { # Вопрос : ответ
    "На какую встречу хотите записаться? " : "1",
    "Ваше ФИО " : '2',
    'Группа': '3'
}

typeQuestions = { # вопрос : тип вопроса
    "На какую встречу хотите записаться? " : ['Фото','Видео','Дизайн','Ораторство'],
    "Ваше ФИО " : [''],
    'Группа': ['']

}

createCell(len(questionsData))

print("Таблица создана")

usersId = [] # список людей которые уже учавствуют или уже прошли тест
usersId.append(0) # добавляем фантомного пльзователя 
start = False
rowQuestion = 4


countRegisterUser = sheet.get("A2")
countRegisterUser = countRegisterUser[0]
countRegisterUser = countRegisterUser[0]
print(countRegisterUser)
columCell = int(countRegisterUser)

def keyboardCreater(ButtonText1, ButtonText2, ButtonText3, ButtonText4): 
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(ButtonText1)
    keyboard.add_line()
    keyboard.add_button(ButtonText2)
    keyboard.add_line()
    keyboard.add_button(ButtonText3)
    keyboard.add_line()
    keyboard.add_button(ButtonText4)

    keyboard = keyboard.get_keyboard()

    return keyboard

def printQuestion(random_id, user_id):
    global columCell, questionsData,rowQuestion, countRegisterUser
    
    countRegisterUser = sheet.get("A2")
    countRegisterUser = countRegisterUser[0]
    countRegisterUser = countRegisterUser[0]
    print(countRegisterUser)
    columCell = int(countRegisterUser)

    columCell += 1
    sheet.update_cell(2, 1, int(countRegisterUser) + 1)
    privateColumCell = columCell
    privateRowCell = rowQuestion 

    firstConnection(user_id, privateColumCell)

    privateUserInfo = vk.users.get(user_ids = user_id)
    privateUserInfo = privateUserInfo[0]
    print(privateUserInfo["id"])
    
    for question in questionsData:

        typeQuest = len(typeQuestions[question])

        photo = None
        keyboard = None

        print(typeQuest)
        if typeQuest == 1:
            if typeQuestions[question] != [''] :
                photo = typeQuestions[question].pop(0)
            else:
                print('Просто ответ')
        
        elif typeQuest == 5:
            photo = typeQuestions[question].pop(0)
            keyboard = keyboardCreater(*typeQuestions[question])
        
        elif typeQuest == 4:
            print(typeQuestions[question])
            keyboard = keyboardCreater(*typeQuestions[question])
            
        vk.messages.send(
                    user_id=user_id,
                    random_id=random_id,
                    attachment = photo,
                    message = question,
                    keyboard = keyboard
                )

        getMessege(questionsData[question], user_id)

        otvet = vk.messages.getHistory(user_id = user_id, count = 1)
            # распарсили ответ
        otvet = otvet['items']
        otvet = otvet[0]
        otvet = otvet['text']

           
        sheet.update_cell(privateColumCell, privateRowCell, str(otvet))

        privateRowCell += 1    
           
        print('next')

    delite = usersId.index(privateUserInfo["id"])
    usersId.pop(delite)

    vk.messages.send(
                    user_id=user_id,
                    random_id=random_id,
                    attachment = photo,
                    message = 'Вы зарегистрированы '
                    # keyboard = keyboard
                )
                    
def getMessege (stringOtvet, user_id): # Получаем сообщение от конкретного пользователя
    for event in longpoll.listen(): # цикл для каждго ивента сервера
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id: # ждать ответа от данного юзера 
            vk.messages.getConversations(offset = 0, count = 1)  
    
            if event.text == stringOtvet: # если событие текст и он равен сообщению которое отправил пользователь
                return True

            return False

def newUser():
    global columCell

    print("Проверка подключения")

    for userId in usersId: # Перебираем список с пользователями 
        if event.user_id == userId:
            print("Старый пользователь...")

            return False 
    print("Новый пользователь...")

    userInfo = vk.users.get(user_ids = event.user_id) 
    print(userInfo)# Получили ответ в виде массива из одного списка
    
    return True

def firstConnection(user_id, columCell):
    # global columCell

    userInfo = vk.users.get(user_ids = user_id)
    userInfo = userInfo[0] 

    sheet.update_cell(columCell, 1, f"""vk.com/id{user_id}""")
    sheet.update_cell(columCell, 2, userInfo["first_name"])
    sheet.update_cell(columCell, 3, userInfo["last_name"])

        # input("ждем других \n")
        
for event in longpoll.listen():
    print(event.type)

    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:

        # startMessage = getMessege("Встреча",event.user_id)
        startMessage = event.text
        print((str(startMessage)) == ("Встреча" or "Встреча " or "встреча" or "встреча "))
        if (str(startMessage)) == ("Встреча" or "Встреча " or "встреча" or "встреча "):
            start = True
        else:
            start = False

        if start:
            whoUser = newUser()
            # whoUser = True
        
            if whoUser:
                print("Новый пользователь")
                
                usersId.append(event.user_id)
            
                Thread(target=printQuestion, args=(event.random_id, event.user_id,)).start() # Запуск нового потока для нового пользвоателя
            else:
                print("Старый пользователь")
        else:
            start = False

                

