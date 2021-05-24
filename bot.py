import logging
import os
import tweepy
from tweepy import OAuthHandler
from os import environ
import telegram
from datetime import date, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from datetime import datetime
from pytz import timezone
format = "%d-%m-%Y %H:%M:%S %Z%z"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

access_token = environ['access_token']
access_token_secret = environ['access_token_secret']
consumer_key = environ['consumer_key']
consumer_secret = environ['consumer_secret']
http_api = environ['http_api']
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token,access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
tweets = []
dt = date.today() - timedelta(1)

def menu(update: Update, _: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Beds", callback_data='Beds'),
            InlineKeyboardButton("ICU", callback_data='ICU'),
        ],
        [
            InlineKeyboardButton("Oxygen Cylinders", callback_data='Oxygen%20Cylinders'),
            InlineKeyboardButton("Plasma", callback_data='Plasma')
        ],
        [
            InlineKeyboardButton("Food", callback_data='Food'),
            InlineKeyboardButton("Ambulance", callback_data='Ambulance'),
        ],
        [
            InlineKeyboardButton("Blood", callback_data='Blood'),
            InlineKeyboardButton("Amphotericin", callback_data='Amphotericin'),
        ],
        [
            InlineKeyboardButton("Remdesivir", callback_data='Remdesivir'),
            InlineKeyboardButton("Favipiravir", callback_data='Favipiravir'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose one of the following :', reply_markup=reply_markup)

def city(update, context,*args):
    try:
        city=context.args[0]
    except:
        update.message.reply_text("Hey, User I also need the name of a city after /city. Let me give you an example: /city mumbai")
    update.message.reply_text("The city has been set as:"+city+"\nEnter /menu for the options")
    f = open("city.txt", "w")
    f.write(city)
    f.close()

def time_converter(time_input):
    flag = 0
    date_tweet = time_input[0:2] + "/" + time_input[3:5]+ "/" + time_input[6:11]
    hrs = int(time_input[11] + (time_input[12]))
    mins = int(time_input[14] + (time_input[15]))
    secs = time_input[17] + time_input[18]
    mins = mins + 30
    if mins>=60:
        mins = mins - 60
        flag = 1
    hrs = hrs + 5 + flag
    if hrs>24:
        hrs = hrs-24
    if hrs<10:
        hrs = "0" + str(hrs)
    if mins<10:
        mins = "0" + str(mins)
    d = datetime.strptime(str(hrs) + ":" + str(mins), "%H:%M")
    f_time = "     DATE:" + date_tweet + " TIME:" + d.strftime("%I:%M %p")
    return f_time 

def scrapetweets(city,option):
    
    new_search = city +" "+ option + " -filter:retweets -verified -unverified -available" + " urgent AND required" # " required OR patients OR needed OR attendants OR #required"
    link=[]

    for tweet in tweepy.Cursor(api.search, q=new_search, lang="en",count=100).items(5):

        try:
            data = [tweet.id]
            status = api.get_status(tweet.id)
            created_at = status.created_at
            temp_time = created_at.strftime(format)
            final_time = time_converter(str(temp_time))
            link.append(f"https://twitter.com/anyuser/status/"+str(data[0]) + " " + str(final_time))
        
        except tweepy.TweepError as e:
            print(e.reason)
            continue

        except StopIteration:
            break

    return link


def button(update: Update, _: CallbackContext) -> None:

    query = update.callback_query
    
    f = open("city.txt", "r")
    city=f.read()
    f.close()

    bot = telegram.Bot(token=http_api)  
    query.answer()

    if(city=='%20'or city==''):
        city='India'

    link=scrapetweets(city,str(query.data))
    
    if (len(link)>0):
        bot.sendMessage(update.effective_user.id,text=f"{len(link)} 𝐫𝐞𝐜𝐞𝐧𝐭 𝐭𝐰𝐞𝐞𝐭𝐬 𝐚𝐫𝐞:\n")
    else:
        bot.sendMessage(update.effective_user.id,text=f"𝐒𝐨𝐫𝐫𝐲, 𝐍𝐨 𝐫𝐞𝐜𝐞𝐧𝐭 𝐭𝐰𝐞𝐞𝐭𝐬 𝐰𝐞𝐫𝐞 𝐟𝐨𝐮𝐧𝐝\n")

    for i in link:
        bot.sendMessage(update.effective_user.id,text=i)

    search=f"https://twitter.com/search?q=verified%20"+city+"%20"+str(query.data)+"%20-'not%20verified'%20-'un%20verified'+'urgent'-filter:retweets&f=live"
    
    bot.sendMessage(update.effective_user.id,text="𝐓𝐨 𝐯𝐢𝐞𝐰 𝐚𝐥𝐥 𝐭𝐡𝐞 𝐫𝐞𝐬𝐮𝐥𝐭𝐬 𝐜𝐥𝐢𝐜𝐤 𝐭𝐡𝐢𝐬 𝐥𝐢𝐧𝐤:\n")
    bot.sendMessage(update.effective_user.id,text=search)

    
    
    

def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Use /city CITY NAME to enter the city name.\nUse /menu to start using the covid resource bot")

def bot_intro(update: Uptry:
        city=context.args[0]
    except:
        update.message.reply_text("Hey, User I also need the name of a city after /city. Let me give you an example: /city mumbai")

    

    updater = Updater(http_api)
    updater.dispatcher.add_handler(CommandHandler('start', bot_intro))
    updater.dispatcher.add_handler(CommandHandler('city', city))
    updater.dispatcher.add_handler(CommandHandler('menu', menu))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    f = open("city.txt", "w")
    f.write(' ')
    f.close()
    main()