import os
import re

from audrey import Audrey
from switcher import Switcher

from dotenv import load_dotenv
from slackbot.bot import Bot
from slackbot.bot import listen_to
from slackbot.bot import respond_to


load_dotenv()

AUDREY_MAC_ADDRESS = os.getenv('AUDREY_MAC_ADDRESS')
SWITCHER_MAC_ADDRESS = os.getenv('SWITCHER_MAC_ADDRESS')
SWITCHER_SHARE_CODE = os.getenv('SWITCHER_SHARE_CODE')

RECEIVED_EMOJI = 'white_check_mark'
DONE_EMOJI = 'heavy_check_mark'

bot = None
audrey = Audrey(AUDREY_MAC_ADDRESS)
switcher = Switcher(SWITCHER_MAC_ADDRESS, SWITCHER_SHARE_CODE)

def remove_emoji(message, emoji):
    params = {
        'name': emoji,
        'channel': message._body['channel'],
        'timestamp': message._body['ts']
    }
    try:
        bot._client.webapi.reactions.remove(**params)
    except Exception as e:
        print(e)

def mark_received(message):
        message.react(RECEIVED_EMOJI)

def mark_done(message):
    remove_emoji(message, RECEIVED_EMOJI)
    message.react(DONE_EMOJI)

@respond_to('audrey (.*)', re.IGNORECASE)
@listen_to('audrey (.*)', re.IGNORECASE)
def command_audrey(message, command):
    def on_success():
        mark_done(message)

    print('Command for Audrey Received: ' + command)
    mark_received(message)
    audrey.send_command(command, on_success)

@respond_to('switcher (.*)', re.IGNORECASE)
@listen_to('switcher (.*)', re.IGNORECASE)
def command_switcher(message, command):
    print('Command for Switcher Received: ' + command)
    mark_received(message)
    params = command.split()
    if params[0] == 'SWITCH':
        # "SWITCH 1 1"
        # "SWITCH 1 0"
        switcher.manage_switch(int(params[1]), params[2]=='1')
    elif params[0] == 'BAT':
        message.reply('Battery Status: {}%'.format(switcher.get_battery()))
    elif params[0] == 'TIME':
        message.reply('Time : {}'.format(switcher.get_time()))
    elif params[0] == 'INFO':
        message.reply.show_informations()
    elif params[0] == 'DIS':
        switcher.disconnect()


def main():
    global bot

    audrey.connect()
    switcher.connect()
    print('Connect to slack')
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
