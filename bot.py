# modules
import logging

from pyowm.owm import OWM
from telegram import Update
from telegram.ext import CommandHandler, Updater, ConversationHandler, MessageHandler, Filters, CallbackContext

# logger
open('logs', 'w').close()
logging.basicConfig(filename='logs', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# vars
SEARCH_CITY, SELECT_CITY = range(2)
updater = Updater('1823894112:AAEW3_uIk1K_Uju8Gjvd6n1qRDpbovpPHio')
owm = OWM('4421353dad4ed558c2a80c85fcb1cf0c')
reg = owm.city_id_registry()

id_of_city = str()
job_hour = 0
select_lat = 0
select_lon = 0

list_of_selected_cities = list()
list_of_updated_messages = list()
matching_cities = dict()


def start_txt():
    txt = f"Hello, to start just write correct name of needed city.\n" \
          "Available commands:\n" \
          "/search - to start a search,\n" \
          "/stop - to stop the bot."
    return txt


def stop_txt():
    txt = 'To search a city write /search.'
    return txt


def search_txt():
    txt = "Write a name of needed city."
    return txt


def delete_txt(tf):
    if tf:
        txt = f"Try write a correct name of command.\n" \
              f"Example: /delete 1."
    else:
        txt = "Removing - SUCCEED."
    return txt


# functions
def start(update: Update, context: CallbackContext):
    global list_of_selected_cities, job_hour
    user = update.message.from_user
    logger.info(f"{user.id} starts a conversation.")

    list_of_selected_cities = list()
    if type(job_hour) != int:
        job_hour.enabled = False
    update.message.reply_text(start_txt())
    return SEARCH_CITY


def search_city(update: Update, context: CallbackContext):
    global matching_cities, list_of_selected_cities, job_hour
    user = update.message.from_user
    user_search = update.message.text

    # error commands
    if user_search == '/start':
        logger.info(f"{user.id} reboot the bot.")

        update.message.reply_text(start_txt())
        return SEARCH_CITY
    elif user_search == '/stop':
        logger.info(f"{user.id} stopped the bot.")

        update.message.reply_text(stop_txt())
        job_hour.enabled = False
        return ConversationHandler.END
    elif user_search == '/search':
        logger.info(f"{user.id} is ready for searching.")

        update.message.reply_text(search_txt())
        return SEARCH_CITY
    elif user_search.count('/delete'):
        logger.info(f"{user.id} wants to delete a city.")

        user_search = user_search.replace('/delete', '')
        user_search = user_search[1:]
        try :
            user_search=int(user_search)
        except ValueError:
            update.message.bot.send_message(chat_id=update.message.chat_id,text=f"Write a correct number.")
            return SEARCH_CITY
        if len(list_of_selected_cities)<=user_search:
            del list_of_selected_cities[user_search-1]
            update.message.bot.send_message(chat_id=update.message.chat_id,text=delete_txt(0))
        else:
            update.message.bot.send_message(chat_id=update.message.chat_id,text=delete_txt(1))
            return SEARCH_CITY
    current_list_of_cities = reg.ids_for(user_search, matching='like')
    current_list_of_coordinates = reg.locations_for(user_search, matching='like')

    if len(user_search) < 3 and not reg.ids_for(user_search):
        logger.info(f"{user.id} trying to search {user_search} - FAILED")

        update.message.reply_text("Try write name with more than 2 letters or write a correct name of your city.\n"
                                  "Example: London, Moscow, Washington.")
        return SEARCH_CITY
    elif not current_list_of_cities:
        logger.info(f"{user.id} trying to search {user_search} - FAILED.")

        update.message.reply_text('Try write a correct name of your city.\n'
                                  'Example: London, Moscow, Washington.')
        return SEARCH_CITY

    if len(user_search) < 3:
        current_list_of_cities = reg.ids_for(user_search)
        current_list_of_coordinates = reg.ids_for(user_search)

    logger.info(f"{user.id} trying to search {user_search} - SUCCEED.")

    sorted(current_list_of_coordinates, key=lambda x: x.name)
    sorted(current_list_of_cities, key=lambda x: x[1])
    for num in range(len(current_list_of_coordinates)):
        cur_name_1 = current_list_of_cities[num][2]
        cur_name_2 = current_list_of_coordinates[num].name
        cur_lon = current_list_of_coordinates[num].lon
        cur_lat = current_list_of_coordinates[num].lat
        if (cur_name_1, cur_name_2) in matching_cities:
            matching_cities[(cur_name_1, cur_name_2)].append([cur_lon, cur_lat])
        else:
            matching_cities[(cur_name_1, cur_name_2)] = [[cur_lon, cur_lat]]
    print(matching_cities)
    update.message.reply_text(
        "Select one of this cities and his latitude, longitude (if he has), to do this write a 2 numbers that represents your city:\n")
    # print(current_list_of_cities)
    # print(current_list_of_coordinates)
    num = 1
    for item in matching_cities.items():
        cur_name_1 = item[0][0]
        cur_name_2 = item[0][1]
        text = f"{num}) Country: {cur_name_1}, City: {cur_name_2}\n"
        for i in range(len(item[1])):
            cur_lon = item[1][i][0]
            cur_lat = item[1][i][1]
            text += f"{len(str(num)) * '   '}{i + 1}) Longitude: {cur_lon}, Latitude: {cur_lat}\n"
        num += 1
        update.message.bot.send_message(chat_id=update.message.chat_id, text=text)
        if num > 100:
            break
    return SELECT_CITY


def select_city(update: Update, context: CallbackContext):
    global list_of_selected_cities, list_of_updated_messages, matching_cities, job_hour
    user = update.message.from_user
    user_search = update.message.text
    chat_id = update.message.chat_id

    if user_search == '/start':
        logger.info(f"{user.id} reboot the bot.")

        update.message.reply_text(start_txt())
        return SEARCH_CITY
    elif user_search == '/stop':
        logger.info(f"{user.id} stopped the bot.")

        update.message.reply_text(stop_txt())
        job_hour.enabled = False
        return ConversationHandler.END
    elif user_search == '/search':
        logger.info(f"{user.id} is ready for searching.")

        update.message.reply_text(search_txt())
        return SEARCH_CITY
    elif user_search.count('/delete'):
        logger.info(f"{user.id} wants to delete a city.")

        user_search = user_search.replace('/delete', '')
        user_search = user_search[1:]
        if list_of_selected_cities.count(user_search):
            list_of_selected_cities.remove(user_search)
            update.message.bot.send_message(chat_id=update.message.chat_id,text=delete_txt(0))
        else:
            update.message.bot.send_message(chat_id=update.message.chat_id,text=delete_txt(1))
            return SELECT_CITY
    try:
        user_choice = (int(user_search.split(' ')[0]), int(user_search.split(' ')[1]))
    except ValueError:
        update.message.reply_text("Write a correct number.")
        return SELECT_CITY
    if user_choice[0] < 1 or user_choice[0] > len(matching_cities) or user_choice[1] < 1:
        update.message.bot.send_message(chat_id=update.message.chat_id,text=f"Write a correct numbers.\n")
        return SELECT_CITY
    tf = 0
    for _ in matching_cities.items():
        tf += 1
        if tf == user_choice[0]:
            if user_choice[1] <= len(_[1]):
                select_lon = _[1][user_choice[1] - 1][0]
                select_lat = _[1][user_choice[1] - 1][1]
                logger.info(f"{user.id} added {_[0][1]}")
                update.message.reply_text(
                    f"Nice!\nYour choice is {_[0][1]}")
                list_of_selected_cities.append([select_lon, select_lat])
                break
            else:
                update.message.bot.send_message(chat_id=update.message.chat_id,text=f"Write a correct numbers\n")
                return SELECT_CITY
    # if tf>len(matching_cities[user_choice[0]]):
    #     update.message.bot.send_message(text=f"Write a correct numbers\n")
    #     return SELECT_CITY
    # print(list_of_selected_cities)
    # for i in range(len(list_of_selected_cities)):
    #     update.message.bot.send_message(f"0\n")
    #     list_of_updated_messages.append([update.message.chat_id,update.message.message_id])
    # print(list_of_updated_messages)
    if type(job_hour) == int:
        job_hour = context.job_queue.run_repeating(hour_weather, interval=1700, first=5, context=chat_id,
                                                   name=str(chat_id))
        job_hour.enabled = True
    matching_cities = dict()
    return SEARCH_CITY


# Dont/
def hour_weather(context: CallbackContext):
    global list_of_selected_cities, list_of_updated_messages
    logger.info(f"Bot is doing work - sending information")

    job = context.job
    mgr = owm.weather_manager()
    for _ in range(len(list_of_selected_cities)):
        select_lon = list_of_selected_cities[_][0]
        select_lat = list_of_selected_cities[_][1]
        one_call_city = mgr.one_call(lat=select_lat,
                                     lon=select_lon,
                                     exclude='minutely', units='metric')
        name_of_city = mgr.weather_at_coords(lat=select_lat, lon=select_lon).location.name
        current_detailed_status = one_call_city.current.detailed_status
        current_clouds = one_call_city.current.clouds
        current_humidity = one_call_city.current.humidity
        # context.bot.edit_message_text()
        try:
            current_temp = f"{one_call_city.current.temp['temp']} ℃"
        except KeyError:
            current_temp = 'No information'
        try:
            current_pressure = f"{one_call_city.current.pressure['press']} hPa"
        except KeyError:
            current_pressure = 'No information'
        try:
            current_wind_speed = f"{one_call_city.current.wind()['speed']} meter/sec"
        except KeyError:
            current_wind_speed = 'No information'
        try:
            current_wind_gust = f"{one_call_city.current.wind()['gust']} meter/sec"
        except KeyError:
            current_wind_gust = 'No information'

        text = f"Selected city: {name_of_city}\n" \
               f"Detailed status of weather: {current_detailed_status}\n" \
               f"Cloudiness: {current_clouds} %\n" \
               f"Temperature: {current_temp}\n" \
               f"Atmospheric pressure: {current_pressure}\n" \
               f"Humidity: {current_humidity}%\n" \
               f"Wind speed: {current_wind_speed}\n" \
               f"Wind gust: {current_wind_gust}\n\n" \
               f"To stop the bot write /stop"
        context.bot.send_message(job.context, text=text)


# Dont/

# main
def main():
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(entry_points=[CommandHandler('start', start)],
                                       states={SEARCH_CITY: [MessageHandler(Filters.text, search_city)],
                                               SELECT_CITY: [MessageHandler(Filters.text, select_city)]},
                                       fallbacks={})
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
