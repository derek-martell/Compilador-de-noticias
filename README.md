# 📰 Boletín Mundo Social Diario
Este proyecto automatiza la generación y envío de un boletín informativo diario enfocado en investigación y difusión económica. Utiliza Python para el procesamiento, Google Gemini AI para la síntesis de contenido y GitHub Actions para la ejecución programada.

📂 Estructura del Proyecto
La organización del repositorio es la siguiente:

Plaintext

Automatizaciones/
├── .github/
│   └── workflows/
│       └── main.yml          # Configuración de GitHub Actions (horarios y secretos)
├── main.py                   # Script principal (Extracción RSS -> Gemini -> Email)
├── requirements.txt          # Librerías necesarias (feedparser, google-generativeai, etc.)
└── README.md                 # Documentación general del proyecto
Descripción de Componentes:
main.py: El núcleo del sistema. Contiene la lógica para conectarse a las fuentes de noticias, enviarlas a la IA y gestionar el servidor de correo SMTP.

.github/workflows/main.yml: Define la "receta" de ejecución. Configura el entorno virtual, instala las dependencias y lanza el script cada mañana a las 07:30 AM.

requirements.txt: Lista de herramientas externas. Es vital para que GitHub Actions sepa qué instalar antes de intentar correr el código de Python.

🚀 Funcionalidades
Extracción de Noticias: Obtención automática de datos mediante fuentes RSS (feedparser).

Análisis con IA: Resumen y jerarquización de información económica usando Gemini Pro.

Envío Automatizado: Distribución vía correo electrónico con formato profesional.

Programación Crónica: Ejecución diaria automática a las 07:30 AM (Hora Perú).
