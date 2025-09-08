import csv

from services.logging_service import app_logger
from services.connector_service import get_data

from config.configuration import config

from datetime import datetime, timezone

def fetch_active_alerts():
    """
    Fetch active alerts from TE
    This function should be implemented to retrieve alerts based on your application's logic.
    """
    active_count = {}

    # Puede haber pagination
    app_logger.info(f"{__name__} Fetching active alerts for the past {config.window_size} days...")


    # Para el primer request -- ya de ahi vemos si hay pagination
    active_endpoint = f"{config.te_base_url}alerts"
    params = {'aid': config.aid, 'window': f'{config.window_size}d'}
    

    while True:  # Loop para manejar paginación
        try:
            status, active_list = get_data(headers=config.te_headers_hal, endp_url=active_endpoint, params=params)
            app_logger.info(f"{__name__} Active alerts successfully fetched with status: {status}")
        except Exception as e:
            app_logger.error(f"{__name__} Exception fetching alerts: {e}")
            break

        if status != 200:
            message = f"API Error {status} for alerts in AG {config.aid}"
            app_logger.error(message=message)
            break

        if "alerts" not in active_list:
            message = f"No alerts found in response for AG {config.aid}"
            app_logger.warning(message=message)
            break

        for alert in active_list["alerts"]:
            try:
                app_logger.info(f"{__name__} Processing alert: {alert.get('id', 'no-id')}")
                # Sacamos agents
                alert_details_url = alert["_links"]["self"]["href"]
                status, alert_details = get_data(headers=config.te_headers_hal, endp_url=alert_details_url, params={'aid': config.aid})
                app_logger.info(f"{__name__} Alert details status: {status}")
                agents = [agent['name'] for agent in alert_details.get("details", [])]

                # Sacamos tests asociados
                test_url = alert["_links"].get("test", {}).get("href")
                if not test_url:
                    app_logger.error(f"{__name__} Alert {alert.get('id', 'no-id')} missing test URL: {alert['_links']}")
                    testId = testName = labels = ""
                    target = ""
                else:
                    status, test_info = get_data(headers=config.te_headers_hal, endp_url=test_url, params={'aid': config.aid, "expand": "label"})
                    app_logger.debug(f"{__name__} Test info status: {status}, url: {test_url}")
                    testId = test_info.get("testId", "")
                    testName = test_info.get("testName", "")
                    labels = [label['name'] for label in test_info.get("labels", [])]

                    target = test_info.get("server", "") or test_info.get("domain", "") or test_info.get("url", "")

                    test_interval = test_info.get("interval", 1)  # En segundos

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
                    roundsViolatingOutOf = rule_info.get("roundsViolatingOutOf", 0)
                    roundsViolatingRequired = rule_info.get("roundsViolatingRequired", 0)



                """"
                effective_down_time = duration + tq
                tq = (# intervals - 1) * intervalo del test
                """
                # calculo de tq dependiendo de roundsViolatingOut and required
                if roundsViolatingOutOf == roundsViolatingRequired:
                    #TQ=(N−1)×Δ
                    tq = (roundsViolatingRequired - 1) * test_interval

                # esta condicion siempre se cumple porque required no puede ser mas grande que outOf
                elif roundsViolatingRequired <= roundsViolatingOutOf:
                    #TQ=(M−1+N−1)/2 ​×Δ
                    tq = ((roundsViolatingRequired - 1) + (roundsViolatingOutOf - 1)) / 2 * test_interval

                else:
                    tq = 0  # Si no se cumplen las condiciones, no hay TQ



                if "duration" in alert and alert['state'] == 'CLEARED':
                    duration = round(alert["duration"] / 1000,2) + tq
                else:
                    # Si no tiene dateEnd, lo consideramos activo hasta ahora
                    start = datetime.fromisoformat(alert["startDate"].replace('Z', '+00:00'))
                    if start.tzinfo is None:
                        start = start.replace(tzinfo=timezone.utc)
                    end = datetime.now(timezone.utc)
                    duration = round((end - start).total_seconds(), 2) + tq


                for label in labels:

                    if "Carriers" in labels:
                        if label != "Carriers":
                            key = (label, testName)
                            if key not in active_count:
                                active_count[key] = {}
                            if target:  # Solo si target no está vacío
                                if target not in active_count[key]:
                                    active_count[key][target] = 0
                                active_count[key][target] += duration

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


    return active_count



def get_carriers_metrics(active_count):

    app_logger.info(f"{__name__} Starting get_carriers_metrics for {len(active_count)} alerts...")

    carrier_metrics = {}

    with open('carrier_count.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Carrier', 'Region', 'Internet','Provider', 'Test Name', 'Destination', 'Downtime'])

        for alert_key, alert_data in active_count.items():
            # Procesar alert_key[0] (ejemplo: "NA - DIA - Lumen")
            carrier_parts = [part.strip() for part in alert_key[0].split('-')]  # Separar por '-' y quitar espacios
            
            for target, duration in alert_data.items():
                if target not in carrier_metrics:
                    carrier_metrics[target] = 0
                carrier_metrics[target] += duration

                # Asegurarse de que siempre haya 3 partes, incluso si faltan algunos separadores
                while len(carrier_parts) < 3:
                    carrier_parts.append("")

                writer.writerow([
                    alert_key[0],
                    carrier_parts[0],  # Region (NA)
                    carrier_parts[1],  # Type (DIA)
                    carrier_parts[2],  # Provider (Lumen)
                    alert_key[1],      # Test Name
                    target,            # Destination
                    round(duration,2)           # Downtime
                ])


