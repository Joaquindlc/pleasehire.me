"""
File: scraper.py
----------------
"""

import os
import time
from playwright.sync_api import sync_playwright

RUTA_AUTH = "./auth.json"

def de_un_escape_html(texto):
    """A simple defense mechanism for normalizing special characters in the DOM."""
    if not texto:
        return ""
    return texto.strip().replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")

# Modificaciones y adiciones en scraper.py

def ejecutar_login_manual(plataforma):
    """
    Open the browser to a blank page. 
    Adapts instructions based on selected platform.
    """
    if os.path.exists(RUTA_AUTH): 
        os.remove(RUTA_AUTH)
        
    print("\n🕵️‍♂️ [AUTH] ‘New User’ mode detected. Opening visible browser...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized", 
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--exclude-switches=enable-automation"
            ]
        )
        context = browser.new_context(
            viewport=None,
            locale="es-AR",
            timezone_id="America/Argentina/Buenos_Aires",
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        print("🌐 Initializing isolated browsing environment...")
        page.goto("about:blank")
        time.sleep(1)
        
        # Instrucciones dinámicas segun la UI
        url_destino = "https://linkedin.com/" if "LinkedIn" in plataforma else "https://ar.computrabajo.com/"
        
        print(f"1. In the address bar of the browser you just opened, type:\n   {url_destino}")
        print("2. Press Enter and sign in with your professional account credentials.")
        print("3. DO NOT touch the terminal or press Ctrl+C! Just let the process run its course.")
        print("4. Once you're logged in and in your main feed/profile, stay there until the session is saved.\n")
        print("⏳ Stopwatch started. Waiting for you to complete the flow (120s)...")
        
        time.sleep(120)
        
        print("\n💾 Timeout. Saving persistent session state...")
        context.storage_state(path=RUTA_AUTH)
        print("✅ [AUTH] The auth.json file was generated successfully!")
        
        context.close()
        browser.close()


def extraer_linkedin(page, topico, resultados_totales):
    """
    Navega a la búsqueda de LinkedIn y extrae ofertas adaptándose dinámicamente 
    tanto a la interfaz de usuario logueada como a la interfaz pública (Guest).
    """
    topico_query = topico.strip().replace(" ", "%20")
    # Usamos la URL limpia para búsquedas globales/remotas
    url_completa = f"https://www.linkedin.com/jobs/search/?keywords={topico_query}&f_WT=2"
    
    print(f"   🌐 Navegando de forma segura a LinkedIn: {url_completa}")
    
    try:
        # Usamos wait_until="commit" para evitar bloqueos por scripts pesados de tracking
        page.goto(url_completa, wait_until="commit", timeout=15000)
    except Exception:
        print("   ⚠️ La red de LinkedIn tardó en responder, analizando el DOM disponible...")
        
    # Pausa estratégica para que la SPA termine de renderizar los elementos asíncronos
    time.sleep(6)
    
    # --- SELECTORES PARA MUNDO LOGUEADO VS MUNDO PÚBLICO (GUEST) ---
    selectores_tarjetas = [
        "li.scaffold-layout__list-item",         # Logueado - Panel izquierdo estructurado
        "li[data-occludable-job-id]",             # Logueado - Variación genérica
        "div.base-card",                         # PÚBLICO - Tarjetas de la vista invitado (¡Tu caso actual!)
        ".jobs-search__results-list li",         # PÚBLICO - Elemento de lista estándar
        "div.job-card-container"                 # Variación alternativa
    ]
    
    tarjetas_locator = None
    selector_valido = None
    
    # Buscamos cuál estructura se imprimió en pantalla
    for selector in selectores_tarjetas:
        locator_intento = page.locator(selector)
        if locator_intento.count() > 0:
            tarjetas_locator = locator_intento
            selector_valido = selector
            break

    # Si no los detectó de inmediato, le damos una última espera defensiva de 5 segundos
    if not tarjetas_locator:
        try:
            page.wait_for_selector("div.base-card, li.scaffold-layout__list-item, li[data-occludable-job-id]", timeout=5000)
            for selector in selectores_tarjetas:
                if page.locator(selector).count() > 0:
                    tarjetas_locator = page.locator(selector)
                    selector_valido = selector
                    break
        except Exception:
            pass

    if not tarjetas_locator or tarjetas_locator.count() == 0:
        print(f"   ⏭️ No se pudo visualizar el contenedor de ofertas para el tópico '{topico}'.")
        return

    total_tarjetas = tarjetas_locator.count()
    vueltas = min(total_tarjetas, 4)
    print(f"   📊 Interfaz detectada vía selector: '{selector_valido}'. Analizando primeras {vueltas} tarjetas...")
    
    for i in range(vueltas):
        try:
            tarjeta = tarjetas_locator.nth(i)
            
            # 1. Extracción del ID de oferta
            id_oferta = tarjeta.get_attribute('data-occludable-job-id')
            if not id_oferta:
                id_oferta = tarjeta.get_attribute('data-entity-urn') or f"linkedin_{topico}_{i}"
                if "jobPosting:" in id_oferta:
                    id_oferta = id_oferta.split("jobPosting:")[1]
            
            # 2. Localización del enlace del título (Soporta Clases Logueado y Clases de Invitado)
            enlace_titulo = tarjeta.locator(
                'a.job-card-list__title--link, a.base-card__full-link, h3.base-search-card__title a, h3 a'
            ).first
            
            if not enlace_titulo or not enlace_titulo.is_visible():
                continue
                
            titulo_texto = de_un_escape_html(enlace_titulo.inner_text())
            link_empleo = enlace_titulo.get_attribute('href') or ""
            
            # Limpieza de parámetros de tracking innecesarios
            if "?" in link_empleo:
                link_empleo = link_empleo.split("?")[0]
            url_absoluta = f"https://www.linkedin.com{link_empleo}" if not link_empleo.startswith("http") else link_empleo
            
            # 3. Localización del nombre de la Empresa (Soporta Logueado y Guest)
            empresa_locator = tarjeta.locator(
                '.artdeco-entity-lockup__subtitle, .job-card-container__company-name, h4.base-search-card__subtitle a, .base-search-card__subtitle'
            ).first
            
            nombre_empresa = "Empresa no especificada"
            if empresa_locator and empresa_locator.is_visible():
                nombre_empresa = de_un_escape_html(empresa_locator.inner_text())
            
            # Hacemos clic simulado para emular actividad orgánica (solo si el elemento es clickable)
            if enlace_titulo.is_visible():
                enlace_titulo.click()
                time.sleep(2)
            
            print(f"      📌 [LINKEDIN {i+1}] \"{titulo_texto}\" – Empresa: {nombre_empresa}")
            
            resultados_totales.append({
                "id": id_oferta,
                "titulo": titulo_texto,
                "empresa": nombre_empresa,
                "enlace": url_absoluta
            })
        except Exception:
            # Si una tarjeta tiene un layout roto o inconsistente, pasamos limpiamente a la siguiente
            continue

def iniciar_scraping_automatico(array_topicos, plataforma):
    """
    Orquestador principal que redirige el flujo automático según la plataforma elegida.
    Aplica una estrategia de warm-up (precalentamiento) en la primera carga para LinkedIn.
    """
    print("\n🚀 Initializing Orchestrator with injected cookies...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, 
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = browser.new_context(
            storage_state=RUTA_AUTH,
            viewport=None,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        resultados_totales = []
        
        # Flag estratégico para controlar la inercia de la primera inyección de sesión
        es_primera_carga = True
        
        try:
            es_linkedin = "LinkedIn" in plataforma
            
            for idx, topico in enumerate(array_topicos):
                print(f"\n⚡ Procesando Tópico {idx + 1}/{len(array_topicos)}: '{topico}'")
                
                if es_linkedin:
                    # Si es la primera query de la lista, le damos un tiempo de asentamiento a la red
                    if es_primera_carga:
                        print("   ⏳ Primera carga detectada. Estabilizando sesión e inyección de tokens...")
                        time.sleep(5)
                        es_primera_carga = False
                        
                    extraer_linkedin(page, topico, resultados_totales)
                else:
                    # --- Bloque de CompuTrabajo ---
                    topico_url = topico.lower().strip().replace(" ", "-")
                    url_completa = f"https://ar.computrabajo.com/trabajo-de-{topico_url}"
                    print(f"   🌐 Navegando de forma segura a CompuTrabajo: {url_completa}")
                    page.goto(url_completa, wait_until="domcontentloaded")
                    time.sleep(4)
                    
                    try:
                        page.wait_for_selector('#offersGridOfferContainer', timeout=8000)
                        tarjetas = page.locator('#offersGridOfferContainer article.box_offer')
                        vueltas = min(tarjetas.count(), 3)
                        for i in range(vueltas):
                            tarjeta = tarjetas.nth(i)
                            id_oferta = tarjeta.get_attribute('id') or f"generico_{i}"
                            titulo_locator = tarjeta.locator('h2.fs18.fwB.prB a.js-o-link').first
                            if not titulo_locator.is_visible(): continue
                            
                            # Optimizamos: Limpiamos saltos de línea por consistencia
                            titulo_sucio = de_un_escape_html(titulo_locator.inner_text())
                            titulo_texto = titulo_sucio.split("\n")[0].strip()
                            
                            link_relativo = titulo_locator.get_attribute('href') or ""
                            url_absoluta = link_relativo if link_relativo.startswith("http") else f"https://ar.computrabajo.com{link_relativo}"
                            
                            titulo_locator.click()
                            time.sleep(2)
                            panel_derecho = page.locator('.box_detail, #dd-detailOffer').first
                            empresa_locator = panel_derecho.locator('a.link_ec, .p_empresa, a.empresa').first
                            nombre_empresa = de_un_escape_html(empresa_locator.inner_text()) if empresa_locator.is_visible() else "Empresa Confidencial"
                            
                            print(f"      📌 [COMPUTRABAJO {i+1}] \"{titulo_texto}\" – Empresa: {nombre_empresa}")
                            resultados_totales.append({"id": id_oferta, "titulo": titulo_texto, "empresa": nombre_empresa, "enlace": url_absoluta})
                    except Exception:
                        print(f"   ⏭️ No visible offers were found for '{topico}' en CompuTrabajo.")
            
            # Fin del bucle: Sumario unificado ensanchado estéticamente a 40 y 30 caracteres
            print("\n✨✦ [END] The bot has finished going through the list of topics entered.")
            print("="*85)
            print("Terminal extraction summary:")
            print("="*85)
            for item in resultados_totales:
                # Limpieza de saltos de línea dobles residuales para el reporte final
                tit_clean = item['titulo'].split("\n")[0].strip()
                print(f"🎯 PUESTO: {tit_clean[:40].ljust(40)} | EMPRESA: {item['empresa'][:30].ljust(30)}")
            print("="*85)
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Critical error in the application process: {str(e)}")
        finally:
            context.close()
            browser.close()
            print("🔒 The process has finished and the browser has closed safely.")