from twisted.internet import threads
from twisted.python import log

class Channel(object):
    def __init__(self, name, command_char):
        """
        Create a handler for channel messages.

        @param name         - name of the channel.
        @param command_char - command character.
        """
        self._name = name
        self._command_char = command_char
        self._cmds = {}
        self._passive = {}
        self._user_join = {}

    def _log_callback(self, *args, **kwds):
        if hasattr(args[0], 'printTraceback'):
            args[0].printTraceback()
        log.msg(args[1], system=self._name)

    @property
    def name(self):
        """
        Name of the channel
        """
        return self._name

    @property
    def cmds(self):
        """
        List of names of registered commands
        """
        return self._cmds.keys()

    def register_cmd(self, name, func):
        """
        Register a command for this channel.

        @param name - name of the command
        @param func - command function.  Signature should be:
                      (proto, user, channel, args)
        """
        if not name in self._cmds:
            self._cmds[name] = []
        self._cmds[name].append(func)
        log.msg('Added command %s' % (name,), system=self._name)

    def register_passive(self, name, func):
        """
        Register a passive command for this channel.

        @param name - name of the passive command.
        @param func - command function.  Signature should be:
                      (proto, channel, user, msg)
        """
        if not name in self._passive:
            self._passive[name] = []
        self._passive[name].append(func)
        log.msg('Added passive %s' % (name,), system=self._name)

    def register_user_join(self, name, func):
        """
        Register a command to be executed on user join.

        @param name - name of the command.
        @param func - command function.  Signature should be:
                      (proto, channel, user)
        """
        if not name in self._user_join:
            self._user_join[name] = []
        self._user_join[name].append(func)
        log.msg('Added user_join %s' % (name,), system=self._name)

    def handle_msg(self, proto, user, msg):
        """
        Handle a new message to the channel.  If the message is a
        registered command or passive callback, it will be called.

        @param proto    - IRC protocol
        @param user     - full user identifier
        @param msg      - user input
        """
        if msg.startswith(self._command_char):
            cmd = msg[1:]
            try:
                cmd, args = cmd.split(" ", 1)
            except ValueError:
                args = ""

            for func in self._cmds.get(cmd, []):
                th = threads.deferToThread(func, proto, user, self._name, args)
                th.addCallback(self._log_callback, '<%s> completed' % (cmd,))
                th.addErrback(self._log_callback, '<%s> error' % (cmd,))
        else:
            for name, funcs in self._passive.items():
                for func in funcs:
                    th = threads.deferToThread(func, proto, self._name, user, msg)
                    th.addErrback(self._log_callback, '<%s> error' % (name,))

    def handle_join(self, proto, user):
        """
        Handle a new user joining the channel.

        @param proto    - IRC protocol
        @param user     - full user identifier
        """
        for name, funcs in self._user_join.items():
            for func in funcs:
                th = threads.deferToThread(func, proto, self._name, user)
                th.addCallback(self._log_callback, '<%s> completed' % (name,))
                th.addErrback(self._log_callback, '<%s> error' % (name,))

