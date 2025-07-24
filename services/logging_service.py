import asyncio,socket
import logging
from logging.handlers import RotatingFileHandler

from config.configuration import config


########### Configurar logging ########################################################


def debug_standard_logger():
    # Obtener el logger estándar de Python
    logger = logging.getLogger("debug_logger")
    
    # Verificar si el logger ya tiene handlers (lo que significa que ya fue configurado)
    if not logger.hasHandlers():

        logger.setLevel(logging.DEBUG)

        # Configurar un handler para escribir logs en un archivo con rotación automática
        file_handler = RotatingFileHandler(filename='./Logs/debug.log', maxBytes=10000000, backupCount=5, encoding='utf-8')
        

        # Configurar el formato del log
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        
        # Agregar el handler al logger
        logger.addHandler(file_handler)
        
        # Handler para consola (stdout)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    
    return logger


debug_logger = debug_standard_logger()


def info_standard_logger():
    
    # Obtener el logger estándar de Python
    logger = logging.getLogger("app_logger")
    
    # Verificar si el logger ya tiene handlers (lo que significa que ya fue configurado)
    if not logger.hasHandlers():

        logger.setLevel(logging.INFO)

        # Configurar un handler para escribir logs en un archivo con rotación automática
        file_handler = RotatingFileHandler(filename='./Logs/app.log', maxBytes=10000000, backupCount=5, encoding='utf-8')
        
        # Configurar el formato del log
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        
        # Agregar el handler al logger
        logger.addHandler(file_handler)
        
        # Handler para consola (stdout)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    
    return logger

app_logger = info_standard_logger()


def setup_api_calls_logger():
    # Crear el logger para las llamadas de API
    logger = logging.getLogger("api_calls_logger")
    
    # Verificar si ya está configurado
    if not logger.hasHandlers():

        logger.setLevel(logging.INFO)
        
        # Configurar un handler para escribir logs en un archivo con rotación automática
        file_handler = RotatingFileHandler(filename='./Logs/api_calls.log', maxBytes=10000000, backupCount=5, encoding='utf-8')
        
        # Configurar el formato del log
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        file_handler.setFormatter(formatter)
        
        # Agregar el handler al logger
        logger.addHandler(file_handler)

        # Handler para consola (stdout)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    
    return logger


# Configurar el logger para las llamadas de API
logging1 = setup_api_calls_logger()



async def a_log_request(level, message):

    loop = asyncio.get_running_loop()

    if level in ['Debug', 'DEBUG']:
        await loop.run_in_executor(None, debug_logger.debug, message)

        return

    elif level in ['Info', 'INFO']:
        await loop.run_in_executor(None, app_logger.info, message)

        return

    elif level in ['Warning', 'WARNING']:
        await loop.run_in_executor(None, app_logger.warning, message)

        return

    elif level in ['Critical', 'CRITICAL']:
        await loop.run_in_executor(None, app_logger.critical, message)

        return
    



def setup_standard_logger():
    # Obtener el logger estándar de Python
    logger = logging.getLogger("endpoint_logger")
    
    # Verificar si el logger ya tiene handlers (lo que significa que ya fue configurado)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        # Configurar un handler para escribir logs en un archivo con rotación automática
        file_handler = RotatingFileHandler(filename='./Logs/app.log', maxBytes=10000, backupCount=5, encoding='utf-8')

        # Configurar el formato del log
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        
        # Agregar el handler al logger
        logger.addHandler(file_handler)
        
        # Handler para consola (stdout)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    
    return logger


def setup_graylog():

    # Configure the basic logging setup once
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s %(levelname)s %(message)s'
    )
    
    # Create or get the logger for graylog
    gray_logger = logging.getLogger("New backend")
    
    # Set up the syslog handler if it's not already present
    if not any(isinstance(handler, logging.handlers.SysLogHandler) for handler in gray_logger.handlers):
        try: # Set up the syslog handler 
            handler = logging.handlers.SysLogHandler(address=(config.graylog, 1514)) 
            gray_logger.addHandler(handler) 
        except socket.gaierror as e: 
            print(f"Failed to connect to graylog: {e}") # Handle the error or fallback to another logging method 
        except Exception as e: 
            print(f"An error occurred: {e}")
    
    return gray_logger

