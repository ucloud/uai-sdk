import logging
import logging.config
import collections

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'uaiservice': {
            'format': '[pid: %(process)d][thread: %(thread)d]%(asctime)s - %(levelname)s[%(filename)s][%(module)s][%(funcName)s#%(lineno)d] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'uaiservice',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'uaiservice',
            'filename': './uaiservice.log',
        }
    },
    'loggers': {
        'uaiservice': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

logging.config.dictConfig(LOGGING)
uai_logger = logging.getLogger("uaiservice")

class LogMessage(object):
    def __init__(self, message, *args):
        self.__message = message
        #
        # The following statement allows passing of a dictionary as a sole
        # argument, so that you can do something like
        #  logging.debug("a %(a)d b %(b)s", {'a':1, 'b':2})
        # Suggested by Stefan Behnel.
        # Note that without the test for args[0], we get a problem because
        # during formatting, we test to see if the arg is present using
        # 'if self.args:'. If the event being logged is e.g. 'Value is %d'
        # and if the passed arg fails 'if self.args:' then no formatting
        # is done. For example_tf, logger.warn('Value is %d', 0) would log
        # 'Value is %d' instead of 'Value is 0'.
        # For the use case of passing a dictionary, this should not be a
        # problem.
        # Issue #21172: a request was made to relax the isinstance check
        # to hasattr(args[0], '__getitem__'). However, the docs on string
        # formatting still seem to suggest a mapping object is required.
        # Thus, while not removing the isinstance check, it does now look
        # for collections.Mapping rather than, as before, dict.
        if (args and len(args) == 1 and isinstance(args[0], collections.Mapping)
                and args[0]):
            args = args[0]
            self.__args = args

    def format_begin(self):
        return "BEGIN>> " + self.__message % self.__args

    def format_end(self):
        return "END>> " + self.__message % self.__args

    def format_normal(self):
        return self.__message % self.__args

    def format_exception(self, *args):
        return ("%s%s: " + self.__message) % args % self.__args
