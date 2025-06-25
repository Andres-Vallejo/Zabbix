# 📊 Zabbix Traffic Monitor – Canal de Red ETB Bogotá

Este repositorio contiene un script en Python para consultar, exportar y analizar el tráfico de red desde un ítem de Zabbix. El monitoreo se centra en la interfaz de entrada (`IN`) del router de ETB en Bogotá y permite filtrar caídas de red según horarios laborales y feriados en Colombia.

## 🔧 Requisitos

- Python 3.11 o superior
- Acceso API a un servidor Zabbix
- Conexión a Internet
- Sistema operativo compatible con `pip` (Windows, Linux, Mac)

Instala las dependencias ejecutando:

```bash
pip install -r requirements.txt
```

## 📂 Estructura del repositorio

```text
Zabbix/
├── zabbix_monitor.py        # Script principal
├── requirements.txt         # Dependencias exactas
└── README.md                # Este archivo
```

## 🚀 Uso

1. **Clona el repositorio**:

```bash
git clone https://github.com/Andres-Vallejo/Zabbix.git
cd Zabbix
```

2. **Ejecuta el script**:

```bash
python zabbix_monitor.py
```

El script te pedirá:
- Fecha de inicio y fin
- Umbral mínimo en Mbps
- Filtrará solo días hábiles y horarios laborales (7am–7pm)
- Excluye automáticamente los días festivos en Colombia

3. **Salida**:

Se generará un archivo `.csv` en `C:\Users\valle\Desktop\Zbbix` con las caídas de red por debajo del umbral indicado.

## 🏢 Consideraciones técnicas

- **Canal supervisado:** Interface `xe-0/0/1 Bits per Second (IN)`
- **Capacidad del canal:** 7.5 Gbps
- **Definición de caída:** Tráfico menor al umbral ingresado (ej: 100 Mbps)
- **Horario laboral:** Lunes a viernes, 7:00 a.m. a 7:00 p.m.
- **Feriados:** Detectados automáticamente usando la librería `holidays` para Colombia

## 🛡️ Seguridad

El script hace peticiones HTTPS desactivando la verificación SSL (`verify=False`). Asegúrate de usar redes de confianza o configura certificados válidos en producción.

## 📬 Autor

**Andrés Vallejo**  
Repositorio oficial: [github.com/Andres-Vallejo/Zabbix](https://github.com/Andres-Vallejo/Zabbix)

---

© 2025 – Uso académico, técnico y profesional permitido bajo licencia MIT.

