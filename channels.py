import functools

from twisted.python import log

class Channel(object):
    def __init__(self, name, config):
        """
        Configuration for a channel.

        @param name     - name of the channel.
        @param config   - configuration for the channel.

        Configuration is a dictionary mapping plugin names to a list of
        commands, passives and user joins to load from the plugin.  If
        unspecified, every command for the plugin is loaded.
        """
        self._name = name
        self._config = config
        self._commands = {}
        self._passives = {}
        self._user_joins = {}

    @property
    def name(self):
        """
        Name of the channel
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
        Mapping of passive name to passive method.
        """
        return self._passives

    @property
    def user_joins(self):
        """
        Mapping of user join callback name to method.
        """
        return self._user_joins

    def register_plugin(self, plugin):
        """
        Register a plugin with this channel.  The channel configuration will
        be used to decide which methods should be used from the plugin.

        @param plugin   - plugin to load.
        """
        info = functools.partial(log.msg, system=self.name)
        err = functools.partial(log.err, system=self.name)

        pc = self._config.get(plugin.name, {})
        if not pc.get('load', True):
            info('Skipping plugin %s' % (plugin.name,))
            return

        cmds = pc.get('commands', plugin.commands.keys())
        passives = pc.get('passives', plugin.passives.keys())
        user_joins = pc.get('user_joins', plugin.user_joins.keys())

        if self._config.get('load_commands', True):
            for f in cmds:
                if f in self._commands:
                    err('Duplicate command %s' % (f,))
                self._commands[f] = plugin.commands[f]

            if len(cmds):
                info('%s commands:  %s' % (plugin.name, self._commands.keys(),))

        if self._config.get('load_passives', True):
            for f in passives:
                if f in self._passives:
                    err('Duplicate passive command %s' % (f,))
                self._passives[f] = plugin.passives[f]

            if len(passives):
                info('%s passives:  %s' % (plugin.name, self._passives.keys(),))

        if self._config.get('load_user_joins', True):
            for f in user_joins:
                if f in self._user_joins:
                    err('Duplicate user_join command %s' % (f,))
                self._user_joins[f] = plugin.user_joins[f]

            if len(user_joins):
                info('%s user joins:  %s' % (plugin.name, self._user_joins.keys(),))

