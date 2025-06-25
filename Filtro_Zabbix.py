import requests
import csv
import datetime
import time
import os
import math
import holidays

# === CONFIGURACIÓN GENERAL ===
ZABBIX_URL = 'https://168.176.239.64/zabbix/api_jsonrpc.php'
AUTH_TOKEN = '924c13997164be7a219326c5011c053ba0778a23ed0536a33b4226da4cbc8114'
HOST_NAME = 'Router ETB Bogota'
ITEM_NAME = 'Interface xe-0/0/1 Bits per Second (IN)'
CSV_FOLDER = r'C:\Users\valle\Desktop\Zbbix'

# === ENTRADAS ===
print("📅 Ingreso manual de fechas")
dia_i = int(input("Día de inicio (1–31): "))
mes_i = int(input("Mes de inicio (1–12): "))
anio_i = int(input("Año de inicio: "))
dia_f = int(input("Día final (1–31): "))
mes_f = int(input("Mes final (1–12): "))
anio_f = int(input("Año final: "))
umbral_mbps = float(input("⚠ Ingrese el umbral de caída en Mbps (ej: 100): "))

fecha_inicio = datetime.datetime(anio_i, mes_i, dia_i, 0, 0, 0)
fecha_fin    = datetime.datetime(anio_f, mes_f, dia_f, 0, 0, 0)

print(f"⏱ Consultando desde: {fecha_inicio} hasta {fecha_fin}")
print(f"📉 Filtrando caídas laborales por debajo de {umbral_mbps} Mbps")

# === PREPARACIÓN ===
total_minutos = int((fecha_fin - fecha_inicio).total_seconds()) // 60
num_bloques = math.ceil(total_minutos / 10000)
print(f"🔢 Total de minutos: {total_minutos}")
print(f"📦 Total de bloques: {num_bloques}")

if not os.path.exists(CSV_FOLDER):
    os.makedirs(CSV_FOLDER)

time_from = int(time.mktime(fecha_inicio.timetuple()))
time_till = int(time.mktime(fecha_fin.timetuple()))

# === FERIADOS COLOMBIA ===
feriados_colombia = holidays.country_holidays('CO', years=[anio_i, anio_f])

def zabbix_api_request(payload):
    headers = {'Content-Type': 'application/json-rpc'}
    response = requests.post(ZABBIX_URL, json=payload, headers=headers, verify=False)
    if response.status_code != 200:
        print(f"❌ Error HTTP {response.status_code}")
        print(response.text)
        exit()
    try:
        data = response.json()
        if 'error' in data:
            print("❌ Error en respuesta de API:")
            print(data['error'])
            exit()
        return data
    except Exception as e:
        print("❌ Error al decodificar JSON:")
        print(response.text)
        raise

# === OBTENER HOST E ITEM ID ===
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
host_id = zabbix_api_request(host_payload)['result'][0]['hostid']

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
item_id = zabbix_api_request(item_payload)['result'][0]['itemid']

# === DESCARGA DE HISTÓRICO ===
history_all = []
delta = 7 * 24 * 60 * 60  # 7 días
start = time_from

while start < time_till:
    end = min(start + delta, time_till)
    print(f"🔍 Consultando: {datetime.datetime.fromtimestamp(start)} → {datetime.datetime.fromtimestamp(end)}")

    history_payload = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "history": 3,
            "itemids": item_id,
            "sortfield": "clock",
            "sortorder": "ASC",
            "time_from": start,
            "time_till": end,
            "limit": 10000
        },
        "auth": AUTH_TOKEN,
        "id": 3
    }
    response = zabbix_api_request(history_payload)
    history_all.extend(response['result'])
    start = end + 1

# === EXPORTACIÓN FILTRADA ===
csv_filename = f"trafico_filtrado_menor_{int(umbral_mbps)}Mbps_laboral.csv"
csv_output = os.path.join(CSV_FOLDER, csv_filename)

with open(csv_output, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Fecha', 'Hora', 'Mbps'])

    registros = 0
    for entry in history_all:
        ts = int(entry['clock'])
        dt = datetime.datetime.fromtimestamp(ts)
        weekday = dt.weekday()  # 0 = lunes, 6 = domingo
        hour = dt.hour

        if dt.date() in feriados_colombia:
            continue  # Omitir días festivos

        value_mbps = round(float(entry['value']) / 1_000_000, 3)

        if 0 <= weekday <= 4 and 7 <= hour < 19 and value_mbps < umbral_mbps:
            writer.writerow([dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M'), value_mbps])
            registros += 1

print(f"✅ {registros} caídas laborales por debajo de {umbral_mbps} Mbps exportadas a:\n{csv_output}")
