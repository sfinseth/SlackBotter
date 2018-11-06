import time
from slackbotter.bot import SlackBotter
from slackbotter.dictstore import DictStore


slack_channel = 'test_channel'  # Replace with channel to write in
slack_token = 'xoxb-2913143739-474123084806-ueBq5cM06ocnJ4Nhs9FNc3Pd'  # Replace with slackbot token
bot = SlackBotter(slack_token, slack_channel)

store = DictStore('message_log')
sent_messages = store.load()


def hello_world(args):  # { message }
    """
    :type args: dict
    """
    bot.send_message('Hello World! {}'.format(args['message']))
    sent_messages[time.time()] = args['message']
    store.write(sent_messages)


bot.add_trigger('hello', hello_world)
bot.add_parameter('hello', '-m', 'message', ['test', 'world', 'horse'])
bot.add_help_message('hello', 'Does something with the message input')

while True:
    bot.run_connection()
