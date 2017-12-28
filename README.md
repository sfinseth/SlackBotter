MspSlackBot
===========
Purpose of this package:
************************
Provides a quick and easy way to hook your
python code up to a slack bot, letting you
worry about writing functionality instead of
spending time writing slack integration.

Packages:
*********
What:

    MspSlackBot

Contains:

    functionality to set up triggers and parameters for functions
    based on slack messages

What:

    DictStore

Contains:

    functionality to save a dictionary to a json file on disk

Typical Usage:
**************
    # import the bot
    from mspslackbot import MspSlackBot
    from dictstore import Dictstore
    import time

    # instantiate the bot
    bot = MspSlackBot('token', 'channel')

    # instantiate dictionary store
    store = DictStore('log_file.json')
    message_log = {}  # we use this to store our message log in

    # define your own function

    def say_hello(args: dict):
        # send a hello message with the passed arguments
        message = 'Hello, %s, how are you?' % args['name'])
        bot.send_message(message)
        message_log[time.time()] = message
        store.write(message_log)  # save the log to the disk

    # add a trigger for the function
    bot.add_trigger('say_hello', say_hello)
    # add a name parameter to the function
    bot.add_parameter('say_hello', '-n', 'name')
    # add a help message for our function
    bot.add_help_message('say_hello', 'write `!say_hello -n [your_name]` to have the bot say hello

    # run the connection on the bot
    bot.run_connection()


Authors: Stefan Finseth

Version: 1.0 of 2017-07-05
