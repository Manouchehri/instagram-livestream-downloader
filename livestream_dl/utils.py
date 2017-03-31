import logging
import json

from instagram_private_api.compat import compat_urllib_request


class TerminalColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Formatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None):
        super(Formatter, self).__init__(fmt, datefmt)

    def format(self, record):
        color = ''
        if record.levelno == logging.ERROR:
            color = TerminalColors.FAIL
        if record.levelno == logging.INFO:
            color = TerminalColors.OKGREEN
        if record.levelno == logging.WARNING:
            color = TerminalColors.WARNING
        return color + str(record.msg) + TerminalColors.ENDC


class UserConfig(object):

    def __init__(self, section, defaults, argparser=None, configparser=None):
        self.section = section
        self.defaults = defaults
        self.argparse = argparser
        self.configparser = configparser

    def get(self, key, type=None):
        value = None
        if self.argparse:
            value = getattr(self.argparse, key)

        # argparser takes precedence over configparser
        if value:
            return value
        try:
            if not value and self.configparser and self.configparser.has_option(self.section, key):
                if type == int:
                    value = self.configparser.getint(self.section, key)
                elif type == float:
                    value = self.configparser.getfloat(self.section, key)
                elif type == bool:
                    value = self.configparser.getboolean(self.section, key)
                elif type == list:
                    items = self.configparser.get(self.section, key)
                    if items:
                        value = [i.strip() for i in items.split(',')]
                else:
                    value = self.configparser.get(self.section, key)
        except ValueError:
            pass

        return value or self.defaults.get(key)

    def __str__(self):
        return 'UserConfig(%s)' % ', '.join([
            'settings=%s' % self.settings,
            'username=%s' % self.username,
            'password=%s' % self.password,
            'outputdir=%s' % self.outputdir,
            'collectcomments=%s' % self.collectcomments,
            'nocleanup=%s' % self.nocleanup,
            'openwhendone=%s' % self.openwhendone,
            'mpdtimeout=%s' % self.mpdtimeout,
            'downloadtimeout=%s' % self.downloadtimeout,
            'verbose=%s' % self.verbose,
            'ffmpegbinary=%s' % self.ffmpegbinary,
            'skipffmpeg=%s' % self.skipffmpeg,
            'log=%s' % self.log,
        ])

    @property
    def settings(self):
        return self.get('settings')

    @property
    def username(self):
        return self.get('username')

    @property
    def password(self):
        return self.get('password')

    @property
    def outputdir(self):
        return self.get('outputdir')

    @property
    def commenters(self):
        return self.get('commenters', type=list)

    @property
    def collectcomments(self):
        return self.get('collectcomments', type=bool)

    @property
    def nocleanup(self):
        return self.get('nocleanup', type=bool)

    @property
    def openwhendone(self):
        return self.get('openwhendone', type=bool)

    @property
    def mpdtimeout(self):
        return self.get('mpdtimeout', type=int)

    @property
    def downloadtimeout(self):
        return self.get('downloadtimeout', type=int)

    @property
    def verbose(self):
        return self.get('verbose', type=bool)

    @property
    def skipffmpeg(self):
        return self.get('skipffmpeg', type=bool)

    @property
    def ffmpegbinary(self):
        return self.get('ffmpegbinary', type=bool)

    @property
    def log(self):
        return self.get('log')


def check_for_updates(current_version):
    try:
        repo = 'taengstagram/instagram-livestream-downloader'
        res = compat_urllib_request.urlopen('https://api.github.com/repos/%s/releases' % repo)
        releases = json.load(res)
        if not releases:
            return ''
        latest_tag = releases[0]['tag_name']
        if latest_tag != current_version:
            return (
                '[!] A newer version %(tag)s is available.\n'
                'Upgrade with the command:\n'
                '    pip install git+ssh://git@github.com/%(repo)s.git@%(tag)s --process-dependency-links --upgrade'
                '\nCheck https://github.com/%(repo)s/ for more information.'
                % {'tag': latest_tag, 'repo': repo})
    except:
        pass

    return ''