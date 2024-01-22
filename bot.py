import telebot
from telebot import types
import json
import codecs

def load_questions(): # открываем .json в utf-8
    with codecs.open('levels.json', 'r', encoding='utf-8') as file:
        questions = json.load(file)
    return questions

def find_answer_by_id(answer_id, questions, current_question):
    return questions[current_question]['answers'][answer_id]

def get_question(question_id, questions):
    if question_id >= len(questions):
        return None
    return questions[question_id]

completed_quests = {}
current_questions = {}
def start_survey(message):
    global completed_quests
    completed_quests[message.chat.id] = False
#выше находится некая логика бота говорящая как и с чем работать, только смысл кромешную логику расписывать в отдельном файле
bot = telebot.TeleBot('')

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, """
Асалам алейкум, я главный враг всех дрифтеров на твоем районе
А также твой друг, который может провести маленький квест(/quest)
Для более подробной информации нажми /help""")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, """
Этот бот был написан очень лениво и лишился некоего функционала на этапе разработки из-за сложности его разработки
На этапе разработки и смотря на код сравнивая с прошлым можно понять что вопросы и ответы это четверть кода по строкам, а здесь то
Пардон за лишние слова, приступим к командам:
/quest - Начало/запуск квеста
/restart - некий аналог /quest только он работает как сбрасыватель некоего триггера""")

# это словарем тяжело назвать, но хоть как-то помогает
quest_statuses = {}

@bot.message_handler(commands=['quest'])
def start_survey(message):
    if message.chat.id in quest_statuses and quest_statuses[message.chat.id]:
        bot.send_message(message.chat.id, "Квест уже запущен. Пожалуйста, завершите текущий квест, прежде чем начинать новый.")
    else:
        quest_statuses[message.chat.id] = True
        questions = load_questions()
        current_question = 0
        first_question = get_question(current_question, questions)
        bot.send_message(message.chat.id, first_question['question'], parse_mode='html')
        for i, answer in enumerate(first_question['answers']):
            bot.send_photo(message.chat.id, photo=answer['image'])
            bot.send_message(message.chat.id, f"{i + 1}. {answer['text']}", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text=str(i + 1), callback_data=str(i))))

@bot.message_handler(commands=['restart'])
def restart_quest(message):
    if message.chat.id in quest_statuses and quest_statuses[message.chat.id]:
        quest_statuses[message.chat.id] = False
        bot.send_message(message.chat.id, "Квест успешно перезапущен.")
    else:
        bot.send_message(message.chat.id, "Квест еще не был начат.")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    answer_id = int(call.data)
    questions = load_questions()

    # начат ли квест
    if call.message.chat.id not in current_questions:
        current_questions[call.message.chat.id] = 0

    answer = find_answer_by_id(answer_id, questions, current_questions[call.message.chat.id])

    if 'winMessage' in answer or 'loseMessage' in answer:
        if 'winMessage' in answer:
            bot.send_message(call.message.chat.id, answer['winMessage'])
            bot.send_message(call.message.chat.id, "Поздравляем, вы выиграли!")
        else:
            bot.send_message(call.message.chat.id, answer['loseMessage'])
            bot.send_message(call.message.chat.id, "К сожалению, вы проиграли.")
        quest_statuses[call.message.chat.id] = False
    else:
        current_questions[call.message.chat.id] = answer['nextQuestion']
        if current_questions[call.message.chat.id] < len(questions):
            next_question = get_question(current_questions[call.message.chat.id], questions)
            bot.send_message(call.message.chat.id, next_question['question'], parse_mode='html')
            for i, answer in enumerate(next_question['answers']):
                bot.send_photo(call.message.chat.id, photo=answer['image'])
                bot.send_message(call.message.chat.id, f"{i + 1}. {answer['text']}",
                                 reply_markup=types.InlineKeyboardMarkup().add(
                                     types.InlineKeyboardButton(text=str(i + 1), callback_data=str(i))))

bot.polling()