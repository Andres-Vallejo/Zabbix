import requests
import csv
import datetime
import time

# === CONFIGURACIÓN PERSONAL ===
ZABBIX_URL = 'https://168.176.239.64/zabbix/api_jsonrpc.php'  # Asegúrate que esta sea tu URL válida
AUTH_TOKEN = '924c13997164be7a219326c5011c053ba0778a23ed0536a33b4226da4cbc8114'  # Pega aquí tu token generado desde Zabbix
HOST_NAME = 'Router ETB Bogota'  # Nombre exacto del host en Zabbix
ITEM_NAME = 'Interface xe-0/0/1 Bits per Second (OUT)'  # Nombre exacto del ítem
START_DATE = '2025-06-01 00:00:00'
END_DATE   = '2025-06-16 23:59:59'
CSV_OUTPUT = 'trafico_etb.csv'

# === CONVERTIR FECHAS A TIMESTAMP UNIX ===
def to_unix_timestamp(date_str):
    return int(time.mktime(datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').timetuple()))

time_from = to_unix_timestamp(START_DATE)
time_till = to_unix_timestamp(END_DATE)

# === PETICIÓN A LA API ZABBIX ===
def zabbix_api_request(payload):
    headers = {'Content-Type': 'application/json-rpc'}
    response = requests.post(ZABBIX_URL, json=payload, headers=headers, verify=False)
    
    # Diagnóstico si algo falla
    if response.status_code != 200:
        print(f"Error HTTP {response.status_code}")
        print(response.text)
        exit()

    try:
        return response.json()
    except Exception as e:
        print("Error decodificando JSON:")
        print(response.text)
        raise

# === 1. Obtener el ID del host ===
host_payload = {
    "jsonrpc": "2.0",
    "method": "host.get",
    "params": {
        "output": ["hostid"],
        "filter": {"host": [HOST_NAME]}
    },
    "auth": AUTH_TOKEN,
    "id": 1
}
host_response = zabbix_api_request(host_payload)
host_id = host_response['result'][0]['hostid']

# === 2. Obtener el ID del ítem ===
item_payload = {
    "jsonrpc": "2.0",
    "method": "item.get",
    "params": {
        "output": ["itemid", "name"],
        "hostids": host_id,
        "search": {"name": ITEM_NAME}
    },
    "auth": AUTH_TOKEN,
    "id": 2
}
item_response = zabbix_api_request(item_payload)
item_id = item_response['result'][0]['itemid']

# === 3. Obtener datos históricos ===
history_payload = {
    "jsonrpc": "2.0",
    "method": "history.get",
    "params": {
        "output": "extend",
        "history": 3,  # 3 = Numeric float
        "itemids": item_id,
        "sortfield": "clock",
        "sortorder": "ASC",
        "time_from": time_from,
        "time_till": time_till,
        "limit": 10000  # O ajusta según tu servidor
    },
    "auth": AUTH_TOKEN,
    "id": 3
}
history_response = zabbix_api_request(history_payload)
history = history_response['result']

# === 4. Guardar los datos en CSV ===
with open(CSV_OUTPUT, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Timestamp', 'Datetime', 'Value (bps)'])
    for entry in history:
        ts = int(entry['clock'])
        dt = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        value = float(entry['value'])
        writer.writerow([ts, dt, value])

print(f'Datos exportados exitosamente a: {CSV_OUTPUT}')
