import logging
import os
import tweepy
from tweepy import OAuthHandler
from os import environ
import telegram
from datetime import date, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

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
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose one of the following :', reply_markup=reply_markup)

def city(update, context,*args):
    city=context.args[0]
    update.message.reply_text("The city has been set as:"+city+"\nEnter /menu for the options")
    f = open("city.txt", "w")
    f.write(city)
    f.close()
    


def scrapetweets(city,option):
    
    new_search = city +" "+ option + " -filter:retweets -verified -unverified -available" + " urgent AND required" # " required OR patients OR needed OR attendants OR #required"
    link=[]

    for tweet in tweepy.Cursor(api.search, q=new_search, lang="en",count=100).items(5):

        try: 
            data = [tweet.id]
            link.append(f"https://twitter.com/anyuser/status/"+str(data[0]))
        
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

    
    search=f"https://twitter.com/search?q=verified%20"+city+"%20"+str(query.data)+"%20-'not%20verified'%20-'un%20verified'+'urgent%20 unverified%20 needed%20 required%20 need%20 needs%20 requirement%20-filter:retweets&f=live"
    
    bot.sendMessage(update.effective_user.id,text="𝐓𝐨 𝐯𝐢𝐞𝐰 𝐚𝐥𝐥 𝐭𝐡𝐞 𝐫𝐞𝐬𝐮𝐥𝐭𝐬 𝐜𝐥𝐢𝐜𝐤 𝐭𝐡𝐢𝐬 𝐥𝐢𝐧𝐤:\n")
    bot.sendMessage(update.effective_user.id,text=search)

    
    
    

def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Use /city CITY NAME to enter the city name.\nUse /menu to start using the covid resource bot")


def main() -> None:
    

    updater = Updater(http_api)
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
