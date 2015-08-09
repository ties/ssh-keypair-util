import augeas
import pwd
import os

import logging

log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(logging.DEBUG)

DEFAULT_CONFIG = {
    'ForwardX11': 'no',
    'ForwardX11Trusted': 'no',
    'ForwardAgent': 'no'
}


DEFAULT_HOST_CONFIG = {
    'IdentitiesOnly': 'yes'
}


class AugeasSSHConfig(object):
    def __init__(self, username):
        # /etc/passwd entry:
        pw_entry = pwd.getpwnam(username)

        assert pw_entry
        # Get the home dir
        self.home_dir = pw_entry.pw_dir
        abs_ssh_config = os.path.join(self.home_dir, '.ssh/config')

        assert os.path.isdir(os.path.dirname(abs_ssh_config))
        self.ssh_config = os.path.relpath(abs_ssh_config, '/')

        self.augeas = augeas.Augeas()
        self.augeas.load()

    def config_path(self, *args):
        path = os.path.join('/files/', self.ssh_config, *args)
        return path

    def set_config_path(self, *args):
        print("'{}': '{}'".format(self.config_path(*args[:-1]), args[-1]))
        return self.augeas.set(self.config_path(*args[:-1]), args[-1])

    def set_defaults(self):
        for key, value in DEFAULT_CONFIG.items():
            if not self.augeas.get(self.config_path(key)):
                log.info("[default] {} {}".format(key, value))
                self.set_config_path(key, value)

    def set_host_field(self, host_alias, field, value):
        host_key = "Host[.='{}']".format(host_alias)
        if not self.augeas.get(self.config_path('Host', host_alias)):
            self.set_config_path(host_key, host_alias)

        self.set_config_path(host_key, field, value)

    def define_host(self, user, host_alias, host_name, key_file, **kwargs):
        if not os.path.isfile(key_file):
            raise ValueError("'{}' is not a valid file".format(key_file))

        config_fields = dict(DEFAULT_HOST_CONFIG)
        config_fields['Hostname'] = host_name
        config_fields['user'] = user
        config_fields['IdentityFile'] = key_file

        config_fields.update(kwargs)

        for key, value in config_fields.items():
            self.set_host_field(host_alias, key, value)

    def save(self):
        self.augeas.save()
