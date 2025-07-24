import asyncio
import time
from controller.general_controller import super_main
from services.logging_service import app_logger
from config.configuration import config



#############################
#           MAIN
#############################

if __name__ == "__main__":
    
    try: 
        app_logger.debug(f"{__name__} Starting the main loop...")
        app_logger.info(f"{__name__} Starting the main loop...")

        start = time.perf_counter()

        super_main()
        

        end = time.perf_counter()
        app_logger.debug(f"{__name__} Execution Time: {end - start:.2f} seconds")

    except Exception as e:

        msg = f"{__name__} An error occurred: {e}"

        app_logger.error(msg)

