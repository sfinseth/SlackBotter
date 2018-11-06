from slackclient import SlackClient


class SlackBotter(object):
    def __init__(self, token: str, channel: str):
        self.token = token
        self.channel = channel
        self.triggers = {
            '!help': self.send_help_message,
        }
        self.help_messages = {
            'unknown': 'Use !help to get help; available commands are:\n',
        }
        self.recurring_functions = []
        self.parameters = {}
        self.allowed_values = {}
        self.slack_client = SlackClient(token)
        return

    def add_trigger(self, keyword: str, command):
        self.triggers['!{}'.format(keyword)] = command
        return

    def add_parameter(self, trigger: str, flag: str, name: str, allowed_values: list = None):
        if ('!{}'.format(trigger)) not in self.parameters.keys():
            self.parameters['!{}'.format(trigger)] = {}
        self.parameters['!{}'.format(trigger)][flag] = name
        if('!{}'.format(trigger)) not in self.allowed_values.keys():
            self.allowed_values['!{}'.format(trigger)] = {}
        if allowed_values:
            self.allowed_values['!{}'.format(trigger)][flag] = allowed_values
        return

    def add_recurring_function(self, command):
        self.recurring_functions.append(command)
        return

    def add_help_message(self, trigger: str, message: str):
        self.help_messages[trigger] = message
        return

    def check_message(self, message: str):
        command = message.split(' ', 1)[0]
        try:
            if command in self.triggers:
                if command == '!help':
                    self.send_help_message(message.split(' ')[1])
                    return None
                if command in self.parameters.keys():
                    args = self.parse_args(command, message.split(' ', 1)[1])
                    if args:
                        self.triggers[command](args)
                    else:
                        return
                else:
                    self.triggers[command]()
        except IndexError as e:
            self.triggers['!help']('unknown')
        return

    def parse_args(self, command: str, args: str):
        params = {}
        for k, v in self.parameters[command].items():
            try:
                param_value = args.split(str('{} '.format(k)), 1)[1].lstrip().split(' ')[0]
                params[v] = param_value
                if k in self.allowed_values[command].keys():
                    if param_value not in self.allowed_values[command][k]:
                        self.send_message('Invalid Paramater value: *{}*\n for parameter *{} ({})*'
                                          ', should be one of:\n *- {}*'
                                          .format(param_value, v, k, '*\n*- '.join(self.allowed_values[command][k])))
                        return
            except IndexError:
                self.send_message('Parameter *{}* is missing.'.format(v))
                self.send_help_message(command[1:])
        return params

    def send_message(self, msg: str):
        self.slack_client.rtm_send_message(self.channel, msg)
        return

    def send_help_message(self, trigger: str):
        if trigger in self.help_messages:
            self.send_message(self.help_messages[trigger])
        else:
            self.send_message(self.help_messages['unknown'])

    def run_connection(self):
        for t in sorted(self.triggers):
            self.help_messages['unknown'] += '`{}`\n'.format(t.replace('!', ''))
        if self.slack_client.rtm_connect():
            while True:
                incoming = self.slack_client.rtm_read()
                for inc in incoming:
                    if 'type' in inc and 'user' in inc:
                        if inc['type'] == 'message':
                            if 'text' in inc:
                                self.check_message(inc['text'])
                for command in self.recurring_functions:
                    command()
        else:
            print('Connection failed, invalid token?')
        return
