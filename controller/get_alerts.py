from services.logging_service import app_logger

def fetch_active_alerts():
    """
    Fetch active alerts from the database.
    This function should be implemented to retrieve alerts based on your application's logic.
    """
    # Placeholder for actual implementation
    return ["alert1", "alert2", "alert3"]


def get_carriers_metrics(active_alerts):

    app_logger.debug(f"{__name__} Starting get_carriers_metrics for {len(active_alerts)} alerts...")

    carrier_metrics = {}

        # Split the labels into batches
    for alert in active_alerts:
        app_logger.debug(f"{__name__} Processing alert: {alert}")
        
        # Sacamos los tests asociados
        # Sacamos los labels asociados a esos tests -- label == carrier entonces ya de aqui podemos construir carrier_metrics
       
    return carrier_metrics