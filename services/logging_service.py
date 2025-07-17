import asyncio
import logging
from logging.handlers import RotatingFileHandler


########### Configurar logging ########################################################


def debug_standard_logger():
    # Obtener el logger estándar de Python
    logger = logging.getLogger("debug_logger")
    
    # Verificar si el logger ya tiene handlers (lo que significa que ya fue configurado)
    if not logger.hasHandlers():

        logger.setLevel(logging.DEBUG)

        # Configurar un handler para escribir logs en un archivo con rotación automática
        file_handler = RotatingFileHandler(filename="./logs/debug.log", maxBytes=10000000, backupCount=5)
        
        # Configurar el formato del log
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        
        # Agregar el handler al logger
        logger.addHandler(file_handler)
    
    return logger


debug_logger = debug_standard_logger()


def info_standard_logger():
    
    # Obtener el logger estándar de Python
    logger = logging.getLogger("app_logger")
    
    # Verificar si el logger ya tiene handlers (lo que significa que ya fue configurado)
    if not logger.hasHandlers():

        logger.setLevel(logging.INFO)

        # Configurar un handler para escribir logs en un archivo con rotación automática
        file_handler = RotatingFileHandler(filename="./logs/app.log", maxBytes=10000000, backupCount=5)
        
        # Configurar el formato del log
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        
        # Agregar el handler al logger
        logger.addHandler(file_handler)
    
    return logger

app_logger = info_standard_logger()


def setup_api_calls_logger():
    # Crear el logger para las llamadas de API
    logger = logging.getLogger("api_calls_logger")
    
    # Verificar si ya está configurado
    if not logger.hasHandlers():

        logger.setLevel(logging.INFO)
        
        # Configurar un handler para escribir logs en un archivo con rotación automática
        file_handler = RotatingFileHandler(filename="./logs/api_calls.log", maxBytes=10000000, backupCount=5)
        
        # Configurar el formato del log
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        file_handler.setFormatter(formatter)
        
        # Agregar el handler al logger
        logger.addHandler(file_handler)

    
    return logger


# Configurar el logger para las llamadas de API
logging1 = setup_api_calls_logger()



async def a_log_request(level, message):

    loop = asyncio.get_running_loop()

    level = level.upper()

    if level == 'DEBUG':
        
        return await loop.run_in_executor(None, debug_logger.debug, message)

    elif level == 'INFO':

        return await loop.run_in_executor(None, app_logger.info, message)

    elif level == 'WARNING':

        return await loop.run_in_executor(None, app_logger.info, message)

    elif level == 'CRITICAL':

        return await loop.run_in_executor(None, app_logger.critical, message)
    
    elif level == 'ERROR':

        return await loop.run_in_executor(None, app_logger.error, message)