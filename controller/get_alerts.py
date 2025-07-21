from services.logging_service import app_logger
from config.configuration import config
from services.connector_service import get_data

def fetch_active_alerts():
    """
    Fetch active alerts from TE
    This function should be implemented to retrieve alerts based on your application's logic.
    """
    active_alerts = []

    # Puede haber pagination
    app_logger.debug(f"{__name__} Fetching active alerts for the past {config.window_size} days...")

    alerts_url = f"{config.te_base_url}alerts"
    alerts = get_data(
        url=alerts_url,
        headers=config.te_headers_hal,
        params={
            "aid": config.aid,
            "window": config.window_size
        }
    )

    if alerts and 'alerts' in alerts:

        while alerts.get("_links", {}).get("next"):

            for alert in alerts['alerts']: #iteramos en todas las alertas para limpiarlas e irles dando formato
                if alert.get('status') == 'active':
                    active_alerts.append(alert)



def get_carriers_metrics(active_alerts):

    app_logger.debug(f"{__name__} Starting get_carriers_metrics for {len(active_alerts)} alerts...")

    carrier_metrics = {}

        # Split the labels into batches
    for alert in active_alerts:
        app_logger.debug(f"{__name__} Processing alert: {alert}")
        
        # Sacamos los tests asociados
        # Sacamos los labels asociados a esos tests -- label == carrier entonces ya de aqui podemos construir carrier_metrics
       
    return carrier_metrics