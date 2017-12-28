import time
from dictstore import DictStore
from slackbotter import SlackBotter


slack_channel = 'test_channel'  # Replace with channel to write in
slack_token = 'XXXXXXXXXXXXXXXXXXXX'  # Replace with slackbot token
bot = SlackBotter(slack_token, slack_channel)

store = DictStore('message_log')
sent_messages = store.load()


def hello_world(args):  # { message }
    """
    :type args: dict
    """
    bot.send_message('Hello World! {0}'.format(args['message']))
    sent_messages[time.time()] = args['message']
    store.write(sent_messages)


bot.add_trigger('hello', hello_world)
bot.add_parameter('hello', '-m', 'message')
bot.add_help_message('hello', 'Does something with the message input')

while True:
    bot.run_connection()
