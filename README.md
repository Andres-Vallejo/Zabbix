# 📊 Zabbix Monitor - Análisis de Tráfico IN

Este proyecto permite extraer y analizar automáticamente los datos de tráfico **IN** desde un servidor **Zabbix**, considerando días hábiles, horarios laborales y feriados en Colombia.

## 🔧 Características

- Consulta de métricas de interfaces de red a través de la API de Zabbix.
- Exportación a CSV de los valores históricos por minuto.
- Filtro configurable por umbral (en Mbps).
- Consideración automática de días festivos colombianos.
- Reportes de caídas laborales.

## 📁 Estructura

- `zabbix_monitor.py`: Script principal para conexión y extracción de datos.
- `requirements.txt`: Lista de dependencias del proyecto.
- `output/*.csv`: Archivos generados con las caídas filtradas.

## ▶ Requisitos

- Tener acceso al servidor Zabbix y su API.
- Python 3.9 o superior.

## ▶ Uso

1. Clona este repositorio:

```bash
git clone https://github.com/Andres-Vallejo/Zabbix.git
cd Zabbix

