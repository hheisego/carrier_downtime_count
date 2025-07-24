from services.logging_service import app_logger
from services.connector_service import get_data

from config.configuration import config

from models.alerts import Alert

from datetime import datetime

def fetch_active_alerts():
    """
    Fetch active alerts from TE
    This function should be implemented to retrieve alerts based on your application's logic.
    """
    active_alerts = []

    # Puede haber pagination
    app_logger.debug(f"{__name__} Fetching active alerts for the past {config.window_size} days...")


    # Para el primer request -- ya de ahi vemos si hay pagination
    active_endpoint = f"{config.te_base_url}alerts"
    params = {'aid': config.aid, 'window': f'{config.window_size}d'}

    print(params)


    """
    1. Fetch active alerts from the API
    2. Pa sacar agentes afectados tenemos que sacar-- alertDetails -- alert["_links"]["self"]["href"]
    3. Sacar los tests asociados a cada alerta -- alert["_links"]["self"]["test"] pero le tenemos que poner aid y expand = label
    4. Sacar el ruleName -- alert["_links"]["self"]["rule"]
    """
    

    while True:  # Loop para manejar paginación
        try:
            status, active_list = get_data(headers=config.te_headers_hal, endp_url=active_endpoint, params=params)
            app_logger.info(f"{__name__} API response status: {status}, endpoint: {active_endpoint}")
        except Exception as e:
            app_logger.error(f"{__name__} Exception fetching alerts: {e}")
            break

        if status != 200:
            message = f"[HCv7] API Error {status} for alerts in AG {config.aid}"
            app_logger.error(message=message)
            break

        if "alerts" not in active_list:
            message = f"[HCv7] No alerts found in response for AG {config.aid}"
            app_logger.warning(message=message)
            break

        for alert in active_list["alerts"]:
            try:
                app_logger.debug(f"{__name__} Processing alert: {alert.get('id', 'no-id')}")
                # Sacamos agents
                alert_details_url = alert["_links"]["self"]["href"]
                status, alert_details = get_data(headers=config.te_headers_hal, endp_url=alert_details_url, params={'aid': config.aid})
                app_logger.debug(f"{__name__} Alert details status: {status}, url: {alert_details_url}")
                agents = [agent['name'] for agent in alert_details.get("details", [])]

                # Sacamos tests asociados
                test_url = alert["_links"].get("test", {}).get("href")
                if not test_url:
                    app_logger.error(f"{__name__} Alert {alert.get('id', 'no-id')} missing test URL: {alert['_links']}")
                    testId = testName = labels = ""
                else:
                    status, test_info = get_data(headers=config.te_headers_hal, endp_url=test_url, params={'aid': config.aid, "expand": "label"})
                    app_logger.debug(f"{__name__} Test info status: {status}, url: {test_url}")
                    testId = test_info.get("testId", "")
                    testName = test_info.get("testName", "")
                    labels = [label['name'] for label in test_info.get("labels", [])]

                # Sacamos ruleName y ruleId
                rule_url = alert["_links"].get("rule", {}).get("href")
                if not rule_url:
                    app_logger.error(f"{__name__} Alert {alert.get('id', 'no-id')} missing rule URL: {alert['_links']}")
                    ruleName = ruleId = ""
                else:
                    status, rule_info = get_data(headers=config.te_headers_hal, endp_url=rule_url, params={'aid': config.aid})
                    app_logger.debug(f"{__name__} Rule info status: {status}, url: {rule_url}")
                    ruleName = rule_info.get("ruleName", "")
                    ruleId = rule_info.get("ruleId", "")

                if "duration" in alert and alert['state'] == 'CLEARED':
                    duration = alert["duration"] / 1000
                else:
                    # Si no tiene dateEnd, lo consideramos activo hasta ahora
                    start = datetime.fromisoformat(alert["startDate"].replace('Z', '+00:00')).replace(tzinfo=None)
                    end = datetime.now()
                    duration = (end - start).total_seconds()

                alert_obj = Alert(
                    alertId=alert.get("id", 0),
                    agents=agents,
                    testId=testId,
                    testName=testName,
                    labels=labels,
                    ruleName=ruleName,
                    ruleId=ruleId,
                    duration=duration,
                )
                active_alerts.append(alert_obj)
            except KeyError as ke:
                app_logger.error(f"{__name__} KeyError in alert {alert.get('id', 'no-id')}: {ke}")
            except Exception as e:
                app_logger.error(f"{__name__} Exception in alert {alert.get('id', 'no-id')}: {e}")
        
        # Verificar si hay más páginas
        if "_links" in active_list and "next" in active_list["_links"]:
            # Obtener URL de la siguiente página
            active_endpoint = active_list["_links"]["next"]["href"]
            params = {"aid": config.aid}  # La URL ya tiene todos los parámetros
            
            message = f"[HCv7] Fetching next page of alerts for AG {config.aid}"
            app_logger.debug(message)
        else:
            # No hay más páginas, salir del loop
            break


    return active_alerts



def get_carriers_metrics(active_alerts):

    app_logger.info(f"{__name__} Starting get_carriers_metrics for {len(active_alerts)} alerts...")

    carrier_metrics = {}

    """
    [
        {label: { alertRule1: {“Cancun”: 20ms , “Ashburn”:50ms},
            alertRule2: {“Toronto”: 20ms , “Ashburn”:50ms}, 
            “total”: 70ms } },
        {}
    ]

    """

    for alert in active_alerts:
        
        app_logger.info(f"{__name__} Processing alert: {alert} \n")
        
       
       
    return carrier_metrics

