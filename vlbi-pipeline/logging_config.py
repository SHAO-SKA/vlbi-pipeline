import logging
import time, os, sys
from config import logfilename

def current_time():
    cur_time = time.strftime('%Y%m%d.%H%M%S')
    print(time.strftime('%Y%m%d.%H%M%S'))
    return cur_time

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
#                     datefmt='%m-%d %H:%M',
#                     filemode='a')
logger = logging.getLogger(__name__)  
logger.setLevel(logging.DEBUG)

if os.path.exists('logs'):
    logger.info("<< Start VLBI-pipeline >>")
    logger.info("Commanding : %s ", sys.argv)
else:
    os.mkdir('logs')
    logger.info("<< Start VLBI-pipeline >>")

#set loggings in output file
file_handler = logging.FileHandler('logs/'+current_time()+logfilename+'.log',mode='a')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.DEBUG)
#set loggings in the command console
console_handler = logging.StreamHandler()  
console_handler.setFormatter(logging.Formatter('%(message)s'))
console_handler.setLevel(logging.INFO)  
#get logger, both on counsole and file output
logger.addHandler(file_handler)
logger.addHandler(console_handler)



#Examples
logger.debug('Test Debug message')
logger.info('Test Info message')
logger.warning('Test Warning message')
logger.error('Test Error message')
logger.critical('Test Critical message')

#For other modoules to import this
__all__ = ['logger'] 


