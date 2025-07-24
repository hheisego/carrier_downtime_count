import httpx
import time
from datetime import datetime, timedelta
import asyncio
from datetime import datetime
from services.logging_service import logging1

# --- Configurable httpx client ---
limits = httpx.Limits(max_keepalive_connections=300, max_connections=1000, keepalive_expiry=100)
timeout = httpx.Timeout(77.7, read=None, pool=17.7)
default_headers = {"User-Agent": "TE-LEPORT/1.0"}

# Define a single global client for your script, or manage with context manager if needed
client = httpx.AsyncClient(limits=limits, timeout=timeout, headers=default_headers)

# --- Util: Logging async (runs in executor for no await penalty) ---
async def a_log_request(endpoint, status_code, roundtrip):
    
    msg = f"Status Code {status_code}: {endpoint} time: {roundtrip:.5f} seconds"
    await asyncio.get_running_loop().run_in_executor(None, logging1.info, msg)

async def a_handle_api_errors(response, endpoint):
    
    if response.status_code in {400, 401, 403, 404, 405}:
    
        error_message = f"Error {response.status_code} for {endpoint}: {response.text}"
    
        await asyncio.get_running_loop().run_in_executor(None, logging1.error, error_message)
    
        try:
    
            resp_json = response.json()
    
        except Exception:
    
            resp_json = {"raw": response.text}
    
        return response.status_code, resp_json, True
    
    return None, None, False

# --- Main async request with retry and pool ---
async def a_request_with_retry(method, url, max_retries=2, retry_sleep=7, **kwargs):
    
    response = None  # Ensure response is always defined
    for _ in range(max_retries + 1):
        
        start = datetime.now()
        response = await client.request(method, url, **kwargs)
        roundtrip = (datetime.now() - start).total_seconds()

        # Handle rate limits
        rate_limit_remaining = int(response.headers.get('x-organization-rate-limit-remaining', 240))
        reset_time = (
            datetime.fromtimestamp(
                int(response.headers.get('x-organization-rate-limit-reset', 5))
            ) - datetime.now()
        ).total_seconds()

        if rate_limit_remaining <= 25 and reset_time >= 10:
            await a_log_request(url, response.status_code, retry_sleep)
            await asyncio.sleep(retry_sleep)

        if response.status_code == 429:
            reset_timestamp = int(response.headers.get('x-organization-rate-limit-reset', 0))
            sleep_time = (
                datetime.fromtimestamp(reset_timestamp) - datetime.now()
            ).total_seconds() + 1
            
            await a_log_request(url, response.status_code, sleep_time)
            await asyncio.sleep(max(0, sleep_time))
            
            continue

        await a_log_request(url, response.status_code, roundtrip)

        status_code, error_response, has_error = await a_handle_api_errors(response, url)
        if has_error:
            return status_code, error_response

        # Try to decode JSON, fallback to raw text
        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        return response.status_code, data
    # All retries failed, return default error code
    return 500, {"error": "Max retries exceeded"}

# --- Async HTTP verbs ---
async def a_get_data(headers, endp_url, params=None):

    return await a_request_with_retry('GET', endp_url, headers=headers, params=params or {})

async def a_post_data(headers, endp_url, payload):

    return await a_request_with_retry('POST', endp_url, headers=headers, json=payload)

async def a_put_data(headers, endp_url, payload):

    return await a_request_with_retry('PUT', endp_url, headers=headers, json=payload)

async def a_delete_data(headers, endp_url, params=None):

    return await a_request_with_retry('DELETE', endp_url, headers=headers, params=params or {})


# Usage: pass this semaphore to your tasks
MAX_PARALLEL_REQUESTS = 10  # Change as needed

async def with_semaphore(sem, coro, *args, **kwargs):
    async with sem:
        return await coro(*args, **kwargs)







##############NO Async###################################
class ConnectorSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        
        if cls._instance is None:
            
            limits = httpx.Limits(max_keepalive_connections=300, max_connections=1000, keepalive_expiry=100)
            timeout = httpx.Timeout(17.7, read=None, pool=7.7)
            cls._instance = httpx.Client(limits=limits, timeout=timeout)
        
        return cls._instance


super_http = ConnectorSingleton.get_instance()


def log_request(endpoint, status_code, roundtrip):

    """Log the request details including the time taken and status code."""
    
    logging1.info(f"Status Code {status_code}: {endpoint} time: {roundtrip:.4f} seconds")

def handle_api_errors(response, endpoint):
    """Handle specific API error responses."""
    
    if response.status_code in {400, 401, 403, 404, 405}:
        
        error_message = f"Error {response.status_code} for {endpoint}: {response.text}"
        logging1.error(error_message)
        
        return response.status_code, response.json(), True
    
    return None, None, False



def request_with_retry(method, url, **kwargs):

    """Generic request function with retry for rate limiting, timing, extra sleep time, and error handling."""
    start = time.time()
    response = super_http.request(method, url, **kwargs)
    roundtrip = time.time() - start

        # New rule: Check rate limit remaining and sleep if needed
    rate_limit_remaining = int(response.headers.get('x-organization-rate-limit-remaining', 240))
    reset_time =  (datetime.fromtimestamp(int(response.headers.get('x-organization-rate-limit-reset', 0))) - datetime.now()).total_seconds()
    
    if rate_limit_remaining <= 11 and reset_time >= 17:
        
        log_request(url, response.status_code, 5)  # Log this event
        time.sleep(5)  # Sleep for 7 seconds to relieve the API

    if response.status_code == 429:
        
        reset_timestamp = int(response.headers.get('x-organization-rate-limit-reset', 0))
        sleep_time = (datetime.fromtimestamp(reset_timestamp) - datetime.now()).total_seconds() + 1
        time.sleep(max(0, sleep_time))
        retry_start = time.time()
        response = super_http.request(method, url, **kwargs)
        roundtrip = time.time() - retry_start
    
    log_request(url, response.status_code, roundtrip)
    
    # Handle specific error codes
    status_code, error_response, has_error = handle_api_errors(response, url)
    
    if has_error:

        return status_code, error_response
    
    return response.status_code, response.json()



def get_data(headers, endp_url, params):
    
    status_code, response = request_with_retry('GET', endp_url, headers=headers, params=params)
    
    if isinstance(response, dict) or status_code in {200, 201}:
    
        return status_code, response
    
    else:
        # Handle non-JSON responses or unexpected outcomes
    
        return status_code, {"error": f"{response.text}"}


def post_data(headers, endp_url, payload):
    
    status_code, response = request_with_retry('POST', endp_url, headers=headers, data=payload)
    
    if isinstance(response, dict) or status_code in {200, 201}:
    
        return status_code, response
    
    else:
    
        # Handle non-JSON responses or unexpected outcomes
        return status_code, {"error": f"{response.text}"}
