import os
import time
import json
from slackclient import SlackClient

SLACK_BOT_TOKEN = 'xoxb-250812903346-TT7IJzEQhPkmXGmJRQaeU8fg'
#SLACK_BOT_TOKEN = 'xoxb-251274004660-dBVWTDY6JIh28LH4AwG9vyVG'
BOT_NAME = 'ekinobot'
EXAMPLE_COMMAND = ['add', 'list', 'set']
TIMESHEET = {'hors-projet':0, 'vacances':0, 'arval': 0}

# json attachment structure


# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

def get_bot_id():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print(user.get('id'))
                return user.get('id')
    else:
        return None


def handle_add_command(command, channel):
    """
        Receive commands to add worked hours to a precise project.
    """
    args = command.split(' ')
    hours = args[1]
    if is_number(hours):
        if args[2] == 'to':
            project = args[3]
            if project in TIMESHEET:
                TIMESHEET[project] = TIMESHEET[project] + int(hours)
                response = hours + " heures imputées sur le projet " + project
                print(slack_client.api_call("chat.postMessage",
                    channel=channel, text=response, as_user=True, 
                    attachments=json.dumps([{'text': 'Valider votre imputation ?', 'fallback': 'Validate your request', 'attachment_type': 'default',
                                 'actions':[{'name': 'validate', 'text': 'Valider', 'type': 'button', 'value': True},
                                            {'name': 'validate', 'text': 'Refuser', 'type': 'button', 'value': False}]}])
                )
                )

            else:
                response = "Le projet " + project + " ne vous est pas associé"
                slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)
    else:
        response = "Veuillez renseigner une valeur d'heure valide : "+ hours
        slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)
    


def handle_set_command(command, channel):
    """
        Receive commands to set worked hours to a precise project.
    """
    args = command.split(' ')
    hours = args[1]
    if is_number(hours):
        if args[2] == 'to':
            project = args[3]
            if project in TIMESHEET:
                TIMESHEET[project] = int(hours)
                response = hours + " heures imputées sur le projet " + project
            else:
                response = "Le projet " + project + " ne vous est pas associé"
    else:
        response = "Veuillez renseigner une valeur d'heure valide : "+ hours
    slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)

def handle_list_command(command, channel):
    """
        Receive command to list worked hours for one or many projects.
    """
    args = command.split(' ')
    del(args[0])
    response = 'Heures imputées du jour :\n'
    if len(args) >= 1:
        for project in args:
            if project in TIMESHEET:
                response = response + str(TIMESHEET[project]) + ' heures imputées sur le projet *' +project + '*\n'
            else:
                response = response + project + 'ne vous est pas associé'
    else:
        for project in TIMESHEET:
            response = response + str(TIMESHEET[project]) + ' heures imputées sur le projet *' +project + '*\n'
    slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    response = "Not sure what you mean. Use the *" 
    for cmd in EXAMPLE_COMMAND:
        response + cmd +', '
    "* command with numbers, delimited by spaces."
    
    action = command.split(' ')[0]
    if action in EXAMPLE_COMMAND:
        if action == 'add':
            handle_add_command(command, channel)
        elif action == 'list':
            handle_list_command(command, channel)
        elif action == 'set':
            handle_set_command(command, channel)
    else:
        slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    # starterbot's ID 
    BOT_ID = get_bot_id()
    # constants
    AT_BOT = "<@" + BOT_ID + ">"

    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
