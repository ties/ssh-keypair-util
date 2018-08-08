import augeas
import pwd
import os

import logging

log = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'ForwardX11': 'no',
    'ForwardX11Trusted': 'no',
    'ForwardAgent': 'no',
    'VisualHostKey': 'yes'
}

DEFAULT_MULTIPLEX = {
    'ControlMaster': 'auto',
    'ControlPersist': '1'
}


def default_host_config(user, host_alias, host_name, port):
    portspec = "_{}".format(port) if port else ""
    return {
        'IdentitiesOnly': 'yes',
        'HostKeyAlias': "{host_name}{portspec}".format(**locals())
    }


class AugeasSSHConfig(object):
    def __init__(self, username):
        # /etc/passwd entry:
        pw_entry = pwd.getpwnam(username)

        assert pw_entry
        # Get the home dir
        self.home_dir = pw_entry.pw_dir

        self.ssh_dir = os.path.join(self.home_dir, '.ssh')

        abs_ssh_config = os.path.join(self.ssh_dir, 'config')

        assert os.path.isdir(self.ssh_dir)
        # Important: Relative path, since augeas uses a relative path in its
        # dictionary to indicate where data is saved.
        self.ssh_config = os.path.relpath(abs_ssh_config, '/')

        log.info("config: '{}'".format(self.ssh_config))

        self.augeas = augeas.Augeas(flags=augeas.Augeas.SAVE_BACKUP)
        self.augeas.load()

    def config_path(self, *args):
        path = os.path.join('/files/', self.ssh_config, *args)
        return path

    def set_config_path(self, *args):
        log.debug("set_config_path({}) = '{}'".format(", ".join(args[:-1]),
                                                      args[-1]))
        return self.augeas.set(self.config_path(*args[:-1]), args[-1])

    def set_defaults(self, configure_multiplex=False):
        defaults = dict(DEFAULT_CONFIG)

        if configure_multiplex:
            defaults.update(DEFAULT_MULTIPLEX)
            # Create multiplex directory
            multiplex_dir = os.path.join(self.ssh_dir, 'multiplex')
            if not os.path.isdir(multiplex_dir):
                os.mkdir(multiplex_dir)

                defaults['ControlPath'] = "{}/%r@%h:%p".format(multiplex_dir)
        
        host_key = "Host[.='*']"
        if not self.augeas.get(self.config_path('Host', '*')):
            self.set_config_path(host_key, '*')

        for key, value in defaults.items():
            if not self.augeas.get(self.config_path(host_key, key)):
                log.info("[default] {} {}".format(key, value))
                self.set_config_path(host_key, key, value)

    def set_host_field(self, host_alias, field, value):
        host_key = "Host[.='{}']".format(host_alias)
        if not self.augeas.get(self.config_path('Host', host_alias)):
            self.set_config_path(host_key, host_alias)

        self.set_config_path(host_key, field, value)

    def define_host(self, user, host_alias, host_name, key_file,
                    proxy_command, port, **kwargs):
        if not os.path.isfile(key_file):
            raise ValueError("'{}' is not a valid file".format(key_file))

        config_fields = default_host_config(user, host_alias, host_name, port)
        config_fields['Hostname'] = host_name
        config_fields['user'] = user
        config_fields['IdentityFile'] = key_file

        if port:
            config_fields['Port'] = str(port)

        if proxy_command:
            cmd = 'ssh -q -W %h:%p {}'.format(proxy_command)
            config_fields['ProxyCommand'] = cmd

        config_fields.update(kwargs)

        for key, value in config_fields.items():
            self.set_host_field(host_alias, key, value)

    def save(self):
        log.debug("augeas.save()")
        self.augeas.save()
