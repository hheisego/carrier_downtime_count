from services.logging_service import app_logger
from controller.get_alerts import fetch_active_alerts, get_carriers_metrics


def super_main():

    app_logger.info(f"{__name__} Starting super_main...")

    #1. Fetch active alerts from desired interval
    active_alerts = fetch_active_alerts()

    #2. Process active alerts
    if active_alerts:
        app_logger.info(f"{__name__} Found {len(active_alerts)} active alerts.")

        #3. Get details for each alert
        carriers_metrics = get_carriers_metrics(active_alerts)


    app_logger.info(f"{__name__} Finished super_main.")