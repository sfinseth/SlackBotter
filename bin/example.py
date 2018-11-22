import time
from slackbotter.bot import SlackBotter
from slackbotter.dictstore import DictStore

slack_channel = 'test_channel'  # Replace with channel to write in
slack_token = '#######'  # Replace with slackbot token
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


# This is a really bad example of what flows in their current form are capable of
# The current flow capabilities are too simpel to support deployment flows -> this would need a proper
# decision tree structure instead of the simple multi-choice steps outlined in the current version.
# A later version will allow a better way to control nested options in a flow.
def deploy_service(args):  # { service, environment, version, confirm }
    """
    :type args: dict
    """
    bot.send_message('Starting deployment:\n'
                     'Service: *{}*\n'
                     'Version: *{}*\n'
                     'Environment: *{}*\n'
                     'Please wait...'.format(args['service'], args['version'], args['environment']))
    time.sleep(3)
    bot.send_message('Finished deployment, running tests..\n'
                     'Please wait...')
    time.sleep(4)
    bot.send_message('Tests passed, deploy successful')


bot.add_trigger('hello', hello_world)
bot.add_parameter('hello', '-m', 'message', ['test', 'world', 'horse'])
bot.add_help_message('hello', 'Does something with the message input')

bot.flow_create('deploy', 'Starting deploy flow!')
bot.flow_step('deploy', 'service', 'Which service would you like to deploy? ', ['ott', 'oase-epg'])
bot.flow_step('deploy', 'environment', 'Which environment would you like to deploy to? ', ['test', 'staging'])
bot.flow_step('deploy', 'version', 'Which version would you like to deploy? ', ['1.0.0', '1.0.1', '1.1.0', '1.2.0'])
bot.flow_step('deploy', 'confirm', 'please approve/deny', ['approve', 'deny'])
bot.flow_action('deploy', deploy_service)

while True:
    bot.run_connection()
