import os
import sys
import logging
import logging.config
import traceback
from logging.handlers import RotatingFileHandler
import ConfigParser
import types

#default values
DEFAULT_LOG_FILE = 'test.log'
DEFAULT_LOG_LEVEL = 'DEBUG'
DEFAULT_LOG_NAME = 'root'
DEFAULT_CONFIG_FILE = 'sample.cfg'

LOGGING_FILE_SIZE = 50 * 1024
LOGGING_BACKUP_COUNT = 10
LOGGING_FORMAT_STRING = '%(asctime)s %(module)s %(funcName)s line#%(lineno)d %(levelname)s %(message)s'

class Base(object):
    def __init__(self):
        self.logger = None
        self.config = None
    
    def set_logger(self, logger):
        self.logger = logger
    
    def create_logger_from_file(self, log_config_file, name=DEFAULT_LOG_NAME):
        try:
            logging.config.fileConfig(log_config_file)
            self.logger = logging.getLogger(name)
        except Exception as excp:
            raise Exception('failed to initialize logger: %s' % excp.message)
            traceback.format_exc()
    
    def create_logger(self, params): 
        logger_obj = None
        try:
            #set logging parameters
            log_file_name = params.get('log_file_name', DEFAULT_LOG_FILE)
            log_level = params.get('log_level', DEFAULT_LOG_LEVEL)
            name = params.get('name', DEFAULT_LOG_NAME)
            console = params.get('console', False)
            
            logger_obj = logging.getLogger(name)
            rotate = RotatingFileHandler(log_file_name, maxBytes=LOGGING_FILE_SIZE,
                                         backupCount=LOGGING_BACKUP_COUNT)
            formatter = logging.Formatter(LOGGING_FORMAT_STRING)
            rotate.setFormatter(formatter)
            logger_obj.addHandler(rotate)
            if console:
                consoleHandler = logging.StreamHandler()
                consoleHandler.setFormatter(formatter)
                logger_obj.addHandler(consoleHandler)
            if log_level.upper() == 'DEBUG':
                logger_obj.setLevel(logging.DEBUG)
            elif log_level.upper() == 'WARNING':
                logger_obj.setLevel(logging.WARNING)
            elif log_level.upper() == 'INFO':
                logger_obj.setLevel(logging.INFO)
            elif log_level.upper() == 'CRITICAL':
                logger_obj.setLevel(logging.CRITICAL)
            elif log_level.upper() == 'ERROR':
                logger_obj.setLevel(logging.ERROR)
            elif log_level.upper() == 'FATAL':
                logger_obj.setLevel(logging.FATAL)
        except Exception as excp:
            traceback.format_exc()
            print('Error in logger initialization with log file %s' %
                                log_file_name)
            raise Exception(
                    'error in logger initialization with log file %s' %
                    log_file_name
                    )
            logger_obj = None
        self.logger = logger_obj
        return logger_obj
    
    def create_logger_from_config(self):
        params = self.get_config_section_as_dict('logging')
        self.create_logger(params)
    
    def load_config(self, config_file=DEFAULT_CONFIG_FILE, exception_on_error=True):
        self.config = None
        try:
            status = None
            self.config = ConfigParser.RawConfigParser()
            status = self.config.read(config_file)
            if len(status) == 0:
                raise
            #print('configuration file loaded successfully.')
        except Exception as excp:
            #print('Error in reading configuration file %s' % config_file)
            self.config = None
            if exception_on_error:
                raise Exception('can not read config file: %s' % config_file)
        return self.config
    
    def get_config_section_as_dict(self, section_name):
        try:
            return dict(self.config.items(section_name))
        except Exception as excp:
            #print('Error in reading section %s from configuration' % section_name)
            raise Exception('can not read section %s from configuration' % section_name)
            return None
        return None
    
    def read_config_section(self, config_file, section_name):
        try:
            self.load_config(config_file)
            return self.get_config_section_as_dict(section_name)
        except Exception as excp:
            #print('Error in reading configuration file %s' % config_file)
            raise Exception('Error in reading configuration file %s' % config_file)
        return None

class DebugLogger(type):
    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.iteritems():
            if isinstance(attr_value, types.FunctionType):
                if not attr_name == '__init__':
                    attrs[attr_name] = cls.deco(attr_value)
        return super(DebugLogger, cls).__new__(cls, name, bases, attrs)
    
    @classmethod
    def deco(cls, func):
        def wrapper(*args, **kwargs):
            self_p = None
            if args:
                self_p = args[0]
            if kwargs:
                self_p = kwargs['self']
            self_p.logger.debug('Calling function: %s' % func.func_name)
            if args:
                self_p.logger.debug('Argument list for function %s is: (%s)' % (func.func_name, str(args)) )
            else:
                self_p.logger.debug('Argument list for function %s is: (%s)' % (func.func_name, str(kwargs)) )
            result = func(*args, **kwargs)
            self_p.logger.debug('Returning from function: %s' % func.func_name)
            return result
        return wrapper
