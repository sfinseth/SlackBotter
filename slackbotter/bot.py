import re
import time
from slackclient import SlackClient


class SlackBotter(object):
    def __init__(self, token: str, channel: str, rtm_read_delay: int):
        self.token = token
        self.channel = channel
        self.triggers = {
            '!help': self.send_help_message,
        }
        self.help_messages = {
            'unknown': 'Use !help to get help; available commands are:\n',
        }
        self.recurring_functions = {}
        self.parameters = {}
        self.allowed_values = {}
        self.allowed_pattern = {}
        self.flows = {}
        self.slack_client = SlackClient(token)
        self.rtm_read_delay = rtm_read_delay
        self.bot_id = None
        self.MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
        return

    def add_trigger(self, keyword: str, command):
        self.triggers['!{}'.format(keyword)] = command
        return

    def add_parameter(self, trigger: str, flag: str, name: str, allowed_values: list = None,
                      allowed_pattern: str = None):
        if ('!{}'.format(trigger)) not in self.parameters.keys():
            self.parameters['!{}'.format(trigger)] = {}
        self.parameters['!{}'.format(trigger)][flag] = name
        if ('!{}'.format(trigger)) not in self.allowed_values.keys():
            self.allowed_values['!{}'.format(trigger)] = {}
        if allowed_values:
            self.allowed_values['!{}'.format(trigger)][flag] = allowed_values
        if allowed_pattern:
            self.allowed_pattern['!{}'.format(trigger)][flag] = allowed_pattern
        return

    def flow_create(self, keyword: str, message: str):
        if keyword not in self.flows.keys():
            self.flows[keyword] = {
                'message': message,
                'steps': {},
                'action': None
            }

    def flow_step(self, keyword: str, step: str, message: str, allowed_values: list = None,
                  allowed_pattern: str = None):
        if step not in self.flows['{}'.format(keyword)]['steps'].keys():
            self.flows[keyword]['steps'][step] = {
                'message': message,
                'values': allowed_values,
                'pattern': allowed_pattern
            }

    def flow_action(self, keyword, command):
        self.flows[keyword]['action'] = command

    def add_recurring_function(self, command, interval):
        self.recurring_functions[command] = {
            'lastrun': time.time(),
            'interval': interval
        }
        return

    def add_help_message(self, trigger: str, message: str):
        self.help_messages[trigger] = message
        return

    def check_message(self, message: str, sender: str, thread_ts: str):
        command = message.split(' ', 1)[0]
        try:
            if command in self.triggers:
                if command == '!help':
                    self.send_help_message(message.split(' ')[1])
                    return None
                if command in self.parameters.keys():
                    args = self.parse_args(command, message.split(' ', 1)[1], thread_ts)
                    if args:
                        self.triggers[command](args)
                    else:
                        return
                else:
                    self.triggers[command]()
            user_id, msg = self.parse_direct_mention(message)
            if user_id == self.bot_id:
                command = msg.split(' ', 1)[0]
                if command in self.flows.keys():
                    self.handle_flow(command, sender, thread_ts)
        except IndexError:
            self.triggers['!help']('unknown')
        return

    def parse_args(self, command: str, args: str, thread_ts: str):
        params = {'thread_ts': thread_ts}
        for k, v in self.parameters[command].items():
            try:
                param_value = args.split(str('{} '.format(k)), 1)[1].lstrip().split(' ')[0]
                params[v] = param_value
                if k in self.allowed_values[command].keys():
                    if param_value not in self.allowed_values[command][k]:
                        self.send_message('Invalid Paramater value: *{}*\n for parameter *{} ({})*'
                                          ', should be one of:\n *- {}*'
                                          .format(param_value, v, k, '*\n*- '.join(self.allowed_values[command][k])),
                                          thread=thread_ts)
                        return
                if k in self.allowed_pattern[command].keys():
                    matches = re.search(self.allowed_pattern[command][k], param_value)
                    if not matches:
                        self.send_message('Invalid Parameter value: *{}*\nfor parameter *{} ({})*'
                                          ', must match pattern: `{}`'
                                          .format(param_value, v, k, self.allowed_pattern[command][k]),
                                          thread=thread_ts)
                        return
            except IndexError:
                self.send_message('Parameter *{}* is missing.'.format(v), thread=thread_ts)
                self.send_help_message(command[1:])
        return params

    def parse_direct_mention(self, message: str):
        matches = re.search(self.MENTION_REGEX, message)
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def handle_flow(self, command: str, sender: str, thread_ts: str):
        self.send_message(self.flows[command]['message'], thread_ts)
        args = {'thread_ts': thread_ts}
        for step in self.flows[command]['steps']:
            self.send_message(self.flows[command]['steps'][step]['message'], thread_ts)
            args[step] = None
            while not args[step]:
                incoming = self.slack_client.rtm_read()
                for inc in incoming:
                    if 'type' in inc and 'user' in inc:
                        if inc['user'] != 'USLACKBOT':
                            if inc['type'] == 'message':
                                if 'thread_ts' not in inc.keys():
                                    if inc['user'] != sender or inc['ts'] != thread_ts:
                                        user_id, msg = self.parse_direct_mention(inc['text'])
                                        if user_id == self.bot_id and msg == 'force abort':
                                            self.send_message('Forcefully aborting running flow', thread=inc['ts'])
                                            return
                                        self.send_message('I am currently processing another request, please wait...',
                                                          thread=inc['ts'])
                                        continue
                                if 'text' in inc:
                                    if self.flows[command]['steps'][step]['values']:
                                        if inc['text'] in self.flows[command]['steps'][step]['values']:
                                            args[step] = inc['text']
                                            continue
                                        elif inc['text'] == 'help':
                                            if self.flows[command]['steps'][step]['values']:
                                                self.send_message('Allowed values:\n*- {}*'.format(
                                                    '*\n*- '.join(self.flows[command]['steps'][step]['values'])),
                                                    thread_ts)
                                                continue
                                        elif inc['text'] == 'abort':
                                            self.send_message('Aborting flow', thread_ts)
                                            return
                                        else:
                                            if inc['type'] == 'message':
                                                if 'text' in inc:
                                                    if self.flows[command]['steps'][step]['values']:
                                                        if inc['text'] in self.flows[command]['steps'][step]['values']:
                                                            args[step] = inc['text']
                                                            continue
                                                        elif inc['text'] == 'help':
                                                            if self.flows[command]['steps'][step]['values']:
                                                                self.send_message('Allowed values:\n*- {}*'.format(
                                                                    '*\n*- '.join(
                                                                        self.flows[command]['steps'][step]['values'])),
                                                                    thread_ts)
                                                                continue
                                                        elif inc['text'] == 'abort':
                                                            self.send_message('Aborting flow', thread_ts)
                                                            return
                                                        else:
                                                            self.send_message(
                                                                'Invalid option\nTry one of these:\n* -{}*'.format(
                                                                    '*\n*- '.join(
                                                                        self.flows[command]['steps'][step]['values'])),
                                                                thread_ts)
                                                            continue
                                    elif self.flows[command]['steps'][step]['pattern']:
                                        if inc['text'] == 'help':
                                            if self.flows[command]['steps'][step]['pattern']:
                                                self.send_message('Allowed pattern:\n*- {}*'.format(
                                                    self.flows[command]['steps'][step]['pattern']),
                                                    thread_ts)
                                                continue
                                        elif inc['text'] == 'abort':
                                            self.send_message('Aborting flow', thread_ts)
                                            return
                                        matches = re.search(
                                            self.flows[command]['steps'][step]['pattern'], inc['text'])
                                        if matches is not None:
                                            args[step] = inc['text']
                                            continue
                                        else:
                                            self.send_message(
                                                'Invalid option, must match pattern: {}'.format(
                                                    self.flows[command]['steps'][step]['pattern']),
                                                thread_ts)
                                            continue
                                    elif inc['text'] == 'abort':
                                        self.send_message('Aborting flow', thread_ts)
                                        return
                                    elif inc['text'] == 'help':
                                        self.send_message('Allowed values:\n*- {}*'.format(
                                            '*\n*- '.join(
                                                self.flows[command]['steps'][step]['options'])),
                                            thread_ts)
                                        continue
                                    else:
                                        args[step] = inc['text']
                                        continue
        self.flows[command]['action'](args)

    def send_message(self, msg: str, thread: str = None):
        self.slack_client.api_call('chat.postMessage', channel=self.channel, text=msg, thread_ts=thread)
        return

    def send_help_message(self, trigger: str):
        if trigger in self.help_messages:
            self.send_message(self.help_messages[trigger])
        else:
            self.send_message(self.help_messages['unknown'])

    def run_connection(self):
        for t in sorted(self.triggers.keys()):
            self.help_messages['unknown'] += '`{}`\n'.format(t.replace('!', ''))
        if self.flows.keys():
            self.help_messages['unknown'] += '\nAvailable mentions are:\n'
            for t in sorted(self.flows.keys()):
                self.help_messages['unknown'] += '`{}`\n'.format(t)

        if self.slack_client.rtm_connect(with_team_state=False):
            self.bot_id = self.slack_client.api_call('auth.test')['user_id']
            while True:
                incoming = self.slack_client.rtm_read()
                for inc in incoming:
                    if 'type' in inc and 'user' in inc:
                        if inc['type'] == 'message' and inc['user'] != 'USLACKBOT':
                            if 'text' in inc:
                                self.check_message(inc['text'], inc['user'], inc['ts'])
                for command in self.recurring_functions:
                    if time.time() > self.recurring_functions[command]['lastrun'] + \
                            self.recurring_functions[command]['interval']:
                        self.recurring_functions[command]['lastrun'] = time.time()
                        command()
                time.sleep(self.rtm_read_delay)

        else:
            print('Connection failed, invalid token?')
        return
