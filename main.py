# -*- coding: utf-8 -*-
import feedparser
import smtplib
import google.generativeai as genai
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
# En lugar de poner el texto directo, usamos os.environ
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EMAIL_PASS_ENV = os.environ.get("EMAIL_PASSWORD")

genai.configure(api_key=GEMINI_API_KEY)

# Cambiado a 2.5-flash que es el que confirmamos que funciona en tu cuenta
MODEL_NAME = 'gemini-2.5-flash'

RSS_FEEDS = [
    # --- Fuentes Locales (Perú) ---
    "https://news.google.com/rss/search?q=site:gestion.pe+when:1d&hl=es-419&gl=PE&ceid=PE:es-419",
    "https://news.google.com/rss/search?q=site:elcomercio.pe+when:1d&hl=es-419&gl=PE&ceid=PE:es-419",
    "https://news.google.com/rss/search?q=site:rpp.pe+when:1d&hl=es-419&gl=PE&ceid=PE:es-419",
    
    # --- Investigación Académica & Económica ---
    "https://www.nber.org/rss/new.xml",               # NBER: New Working Papers (Fundamental)
    "https://www.imf.org/en/News/RSS",                # FMI: Comunicados y noticias globales
    "https://www.worldbank.org/en/news/rss",          # Banco Mundial
    "https://voxeu.org/feed/recent",                  # VoxEU (Análisis de política económica de alto nivel)

    # --- Noticias Internacionales de Prestigio ---
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",    # NYT: Noticias del Mundo
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", # NYT: Negocios y Economía
    "https://www.economist.com/sections/business-finance/rss.xml", # The Economist (Negocios/Finanzas)
    "https://www.dw.com/es/econom%C3%ADa/rss.xml",    # Deutsche Welle (Economía en español)
    
    # --- Mercados & Finanzas Globales ---
    "https://finance.yahoo.com/news/rssfeeds/",       # Yahoo Finance
    "https://www.cnbc.com/id/10001147/device/rss/rss.html",      # CNBC: Top News
    "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=es-419&gl=PE&ceid=PE:es-419", # Google Biz
    "https://finance.yahoo.com/news/category-currencies/rss/"    # Divisas/Forex
]

# 2. FUNCIÓN DE CLASIFICACIÓN POR LOTES (BATCHING)
def clasificar_titulares_batch(lista_items):
    if not lista_items:
        return []

    # Cargamos el modelo con la configuración de JSON
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={"response_mime_type": "application/json"}
    )

    titulares_texto = "\n".join([f"{i}. {item['titulo']}" for i, item in enumerate(lista_items)])

    prompt = f"""
    Actúa como editor de Mundo Social. Clasifica estos titulares en:
    - Macroeconomía & Perú
    - Mercados & Finanzas
    - Política & Coyuntura
    - Otros

    Responde ÚNICAMENTE en JSON con este formato:
    {{
      "clasificaciones": [
        {{"id": 0, "categoria": "Nombre de la Categoría"}},
        ...
      ]
    }}

    Titulares:
    {titulares_texto}
    """

    try:
        response = model.generate_content(prompt)
        # Verificamos que la respuesta tenga contenido
        if not response.text:
            return []

        resultado_json = json.loads(response.text)
        return resultado_json.get("clasificaciones", [])
    except Exception as e:
        print(f"Error crítico en clasificación: {e}")
        return []

# 3. EXTRACCIÓN Y ORGANIZACIÓN
def get_intelligent_news():
    pool_noticias = []
    titulos_vistos = set()
    boletin = {
        "Macroeconomía & Perú": [],
        "Mercados & Finanzas": [],
        "Política & Coyuntura": []
    }

    print("Recolectando noticias de RSS...")
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            titulo = entry.title.split(" - ")[0]
            if titulo not in titulos_vistos:
                pool_noticias.append({"titulo": titulo, "link": entry.link})
                titulos_vistos.add(titulo)

    if not pool_noticias:
        print("No se encontraron noticias nuevas.")
        return None

    print(f"Clasificando {len(pool_noticias)} noticias con {MODEL_NAME}...")
    clasificaciones = clasificar_titulares_batch(pool_noticias)

    if not clasificaciones:
        print("La clasificación falló. Usando categoría 'Otros' por defecto.")
        # Fallback por si la API falla
        for item in pool_noticias:
            boletin.setdefault("Otros", []).append(item)
        return boletin

    for res in clasificaciones:
        idx = res.get("id")
        cat = res.get("categoria")
        if idx is not None and idx < len(pool_noticias):
            noticia = pool_noticias[idx]
            if cat in boletin:
                boletin[cat].append(noticia)
            else:
                # Si la IA inventa una categoría o usa 'Otros'
                boletin.setdefault("Otros", []).append(noticia)

    return boletin
from datetime import datetime

def build_html_report(boletin):
    if not boletin:
        return ""

    fecha_str = datetime.now().strftime("%d de %B de %Y")

    html = f"""
    <html>
    <body style="margin:0; padding:0; background-color:#f4f6f8; font-family: Arial, Helvetica, sans-serif; color:#333;">
        <div style="max-width: 680px; margin: 30px auto; background:#ffffff; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); overflow:hidden;">

            <!-- HEADER -->
            <div style="background: linear-gradient(135deg, #1a2a6c, #2c3e50); padding: 25px; text-align: center; color: #ffffff;">
                <h1 style="margin:0; font-size: 26px; letter-spacing: 1px;">Mundo Social</h1>
                <p style="margin:6px 0 0; font-size: 14px; font-weight: bold; color:#ffcccb;">
                    By Derek Martell
                </p>
                <p style="margin-top:8px; font-size:12px; opacity:0.9;">
                    {fecha_str}
                </p>
            </div>

            <!-- CONTENT -->
            <div style="padding: 25px;">
    """

    for area, noticias in boletin.items():
        if noticias:
            html += f"""
                <div style="margin-bottom: 30px;">
                    <h2 style="
                        font-size:18px;
                        color:#1a2a6c;
                        border-left:5px solid #d32f2f;
                        padding-left:12px;
                        margin-bottom:18px;
                    ">
                        {area}
                    </h2>
            """

            for n in noticias:
                html += f"""
                    <div style="
                        background:#fafafa;
                        border:1px solid #eaeaea;
                        border-radius:10px;
                        padding:14px 16px;
                        margin-bottom:12px;
                    ">
                        <a href="{n['link']}"
                           style="
                               text-decoration:none;
                               color:#2c3e50;
                               font-weight:bold;
                               font-size:14px;
                               line-height:1.4;
                           "
                           target="_blank">
                            {n['titulo']}
                        </a>
                    </div>
                """

            html += "</div>"

    html += """
            </div>

            <!-- FOOTER -->
            <div style="
                text-align:center;
                padding:18px;
                font-size:11px;
                color:#888;
                border-top:1px solid #eee;
                background:#fafafa;
            ">
                Boletín generado automáticamente para <b>Mundo Social</b> © 2026<br>
                Análisis • Investigación • Formación
            </div>

        </div>
    </body>
    </html>
    """ 
    return html
    

            
def send_email(html_content):
    if not html_content:
        return

    remitente = "yago.martell@unmsm.edu.pe"
    destinatarios = ["7073248@gmail.com","anjalyarcos@gmail.com","JeffCB40@gmail.com"]
    
    # IMPORTANTE: Aquí usamos la variable global que definimos arriba
    # No hace falta poner "password = password"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📊 Boletín DEREK MARTELL - {datetime.now().strftime('%d/%m')}"
    msg["From"] = f"DEREK MARTELL AI <{remitente}>"
    msg["To"] = ", ".join(destinatarios)
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            # Usamos directamente la variable global EMAIL_PASS_ENV
            server.login(remitente, EMAIL_PASS_ENV) 
            server.send_message(msg)
        print(f"✅ Boletín enviado con éxito.")
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")

if __name__ == "__main__":
    datos = get_intelligent_news()
    if datos:
        html = build_html_report(datos)
        send_email(html)
