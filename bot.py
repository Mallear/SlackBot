import os
import time
import json
from slackclient import SlackClient

SLACK_BOT_TOKEN = 'xoxb-'
BOT_NAME = 'ekinobot'
# Commands handled by the bot
COMMAND_LIST = ['add', 'list', 'set']
# Dictionnary used to stub a timesheet
TIMESHEET = {'hors-projet':0, 'vacances':0, 'arval': 0}

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

def get_bot_id():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print(user.get('id')) # Log..ish
                return user.get('id')
    else:
        return None


def handle_add_command(command, channel):
    """
        Receive commands to add worked hours to a precise project.
    """
    # Get command arguments
    args = command.split(' ')
    # Get the hour arg value
    hours = args[1]
    # If value type is OK
    if is_number(hours):
        # POC : "sementic" reading
        if args[3] == 'to':
            # Get project arg value
            project = args[-1]
            if project in TIMESHEET:
                # Incr TIMESHEET value for given project
                TIMESHEET[project] = TIMESHEET[project] + int(hours)
                # Build response
                response = hours + " heures imputées sur le projet " + project
                # Build attachments (message buttons) as JSON object
                attachments = json.dumps([{'text': 'Valider votre imputation ?', 'fallback': 'Validate your request', 'attachment_type': 'default',
                                 'actions':[{'name': 'validate', 'text': 'Valider', 'type': 'button', 'value': True},
                                            {'name': 'validate', 'text': 'Refuser', 'type': 'button', 'value': False}]}])
                # Send response
                slack_client.api_call("chat.postMessage",
                    channel=channel, text=response, as_user=True, 
                    attachments=attachments)

            else:
                response = "Le projet " + project + " ne vous est pas associé"
                slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)
    else:
        response = "Veuillez renseigner une valeur d'heure valide : "+ hours
        slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)


def handle_list_command(command, channel):
    """
        Receive command to list worked hours for one or many projects.
    """
    # Get command arguments
    args = command.split(' ')
    # Delete command name
    del(args[0])
    # Init variables
    response = 'Heures imputées du jour :\n'
    sum_hours = 0
    # If any project are send as args, get value in TIMESHEET and print it
    if len(args) >= 1:
        for project in args:
            if project in TIMESHEET:
                response = response + '*' + str(TIMESHEET[project]) + '*' + ' heures imputées sur le projet *' +project + '*\n'
            else:
                response = response + project + 'ne vous est pas associé'
    # Else print all projects worked hours
    else:
        for project in TIMESHEET:
            response = response + '*' + str(TIMESHEET[project]) + '*' + ' heures imputées sur le projet *' +project + '*\n' 
            sum_hours = sum_hours + TIMESHEET[project]
        response = response + 'Total de la journée : *' + str(sum_hours) + '*\n' + \
            'Manque à imputer : *' + str(8-sum_hours) + '*'
    # Sent the response
    slack_client.api_call("chat.postMessage", channel=channel,
                            text=response, as_user=True)


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    # Build response for random command (like 'help' command)
    response = "Not sure what you mean. Use one of the *" 
    for cmd in COMMAND_LIST:
        response = response + cmd +', '
    "* command with numbers, delimited by spaces."

    # Get command args value
    action = command.split(' ')[0]
    # If action handled, do it
    if action in COMMAND_LIST:
        if action == 'add':
            handle_add_command(command, channel)
        elif action == 'list':
            handle_list_command(command, channel)
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
    """
        Homemade check for char as int.
    """
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
