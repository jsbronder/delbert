import inspect

def irc_command(text):
    """
    Declare a method as an irc command.

    @param text - help string for the command.
    """
    def f(func):
        func.is_command = True
        func.help = text
        return func
    return f

def irc_passive(text):
    """
    Declare a method as a passive irc command.  Passive commands
    are run on every message sent to a public channel that the
    bot is in.

    @param text - help string for the passive command.
    """
    def f(func):
        func.is_passive = True
        func.help = text
        return func
    return f

def irc_user_join(text):
    """
    Declare a method as a user join callback.  User joins are called
    whenever a user joins a channel the bot is in.

    @param text - help string for the passive command.
    """
    def f(func):
        func.is_user_join = True
        func.help = text
        return func
    return f

class Plugin(object):
    """
    IRC Plugin base class.

    Plugins use the irc_command, irc_passive and irc_user_join method
    decorators to declare commands they can accept from users.

    Prior to use, a plugin should be initialized with the initalize()
    method in order to set the irc protocol and bot nickname.
    """
    class NullProto(object):
        def send_msg(self, channel, msg):
            pass

        def send_notice(self, channel, msg):
            pass

    def __init__(self, name):
        """
        Create a Plugin.

        @param name - name of the plugin.
        """
        self._name = name
        self._nickname = ''
        self._proto = Plugin.NullProto()
        self._commands = {}
        self._passives = {}
        self._user_joins = {}

        for name, method in inspect.getmembers(self, inspect.ismethod):
            if getattr(method, 'is_command', False):
                self._commands[name] = method

            elif getattr(method, 'is_passive', False):
                self._passives[name] = method

            elif getattr(method, 'is_user_join', False):
                self._user_joins[name] = method

    @property
    def name(self):
        """
        Plugin name
        """
        return self._name

    @property
    def commands(self):
        """
        Mapping of command name to command method.
        """
        return self._commands

    @property
    def passives(self):
        """
        Mapping of passive function name to method.
        """
        return self._passives

    @property
    def user_joins(self):
        """
        Mapping of user join name to method.
        """
        return self._user_joins

    @property
    def proto(self):
        """
        Plugin irc protocol.
        """
        return self._proto

    @property
    def nickname(self):
        """
        Name of the bot.
        """
        return self._nickname

    def initialize(self, nickname, proto):
        """
        Initialize the plugin.

        @param nickname - nickname of the bot.
        @param proto    - irc protocol.
        """
        self._nickname = nickname
        self._proto = proto

