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

def ejecutar_login_manual():
    """
    Open the browser to a blank, neutral page to bypass strict IP/signature blocking.
    Allow 120 seconds for the user to browse and log in manually.
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
        
        print("1. In the address bar of the browser you just opened, type:")
        print("   https://ar.computrabajo.com/")
        print("2. Press Enter and click the ‘Log In’ button (top right).")
        print("3. Sign in using your Google account or your login credentials.")
        print("4. DO NOT touch the terminal or press Ctrl+C! Just let the process run its course.")
        print("5. Once you're logged in, stay on your profile page until the bot saves your session.\n")
        
        print("⏳ Stopwatch started. Waiting for you to complete the flow in the Chromium window...")
        
        
        time.sleep(120)
        
        print("\n💾 Timeout. Saving persistent session state...")
        context.storage_state(path=RUTA_AUTH)
        print("✅ [AUTH] The auth.json file was generated successfully!")
        
        context.close()
        browser.close()
        print("🔒 Securely closed authentication environment.")

def iniciar_scraping_automatico(array_topicos):
    """
    The system tracks offers using cookies injected from auth.json.
    It keeps the browser visible (headless=False) for monitoring on the screen.
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
        
        try:
            for idx, topico in enumerate(array_topicos):
                print(f"\n⚡ Procesando Tópico {idx + 1}/{len(array_topicos)}: '{topico}'")
                
                topico_url = topico.lower().strip().replace(" ", "-")
                url_completa = f"https://ar.computrabajo.com/trabajo-de-{topico_url}"
                
                print(f"   🌐 Navegando de forma segura a: {url_completa}")
                page.goto(url_completa, wait_until="domcontentloaded")
                time.sleep(4)
                
                try:
                    page.wait_for_selector('#offersGridOfferContainer', timeout=8000)
                    
                    tarjetas = page.locator('#offersGridOfferContainer article.box_offer')
                    total_tarjetas = tarjetas.count()
                    
                    vueltas = min(total_tarjetas, 3)
                    print(f"   📊 Se encontraron {total_tarjetas} ofertas disponibles. Analizando las {vueltas} primeras:")
                    
                    for i in range(vueltas):
                        tarjeta = tarjetas.nth(i)
                        id_oferta = tarjeta.get_attribute('id') or f"generico_{i}"
                        
                        titulo_locator = tarjeta.locator('h2.fs18.fwB.prB a.js-o-link').first
                        
                        if not titulo_locator.is_visible(): 
                            continue
                            
                        titulo_texto = de_un_escape_html(titulo_locator.inner_text())
                        link_relativo = titulo_locator.get_attribute('href') or ""
                        
                        if link_relativo.startswith("http"):
                            url_absoluta = link_relativo
                        else:
                            url_absoluta = f"https://ar.computrabajo.com{link_relativo}"
                        
                        titulo_locator.click()
                        time.sleep(2)
                        
                        panel_derecho = page.locator('.box_detail, #dd-detailOffer').first
                        empresa_locator = panel_derecho.locator('a.link_ec, .p_empresa, a.empresa').first
                        
                        nombre_empresa = "Empresa Confidencial"
                        if empresa_locator.is_visible():
                            nombre_empresa = de_un_escape_html(empresa_locator.inner_text())
                            
                        print(f"      📌 [OFERTA {i+1}] \"{titulo_texto}\" – Empresa: {nombre_empresa}")
                        
                        resultados_totales.append({
                            "id": id_oferta,
                            "titulo": titulo_texto,
                            "empresa": nombre_empresa,
                            "enlace": url_absoluta
                        })
                        
                except Exception:
                    print(f"   ⏭️ No visible offers were found, or the container is missing for '{topico}'.")
            
            print("\n✨✦ [END] The bot has finished going through the list of topics entered.")
            print("="*60)
            print("Terminal extraction summary:")
            print("="*60)
            for item in resultados_totales:
                print(f"🎯 PUESTO: {item['titulo'][:30].ljust(30)} | EMPRESA: {item['empresa'][:25].ljust(25)}")
            print("="*60)
            
            print("⏳ Keeping the browser open for a moment for visual confirmation...")
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Critical error in the application process: {str(e)}")
        finally:
            context.close()
            browser.close()
            print("🔒 The process has finished and the browser has closed safely.")