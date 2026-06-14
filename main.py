"""
File: main.py
----------------
Punto de entrada principal para pleasehire.me. Maneja la interfaz gráfica (Tkinter) 
y orquesta dinámicamente los ciclos de autenticación y scraping con feedback visual.
Diseñado para el Showcase de Code in Place.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import time
from scraper import ejecutar_login_manual, iniciar_scraping_automatico

# Configuración estética
COLOR_BG = "#F3F4F6"
COLOR_PRIMARY = "#1D4ED8"
COLOR_SUCCESS = "#10B981"
COLOR_TEXT = "#374151"

class BotPostuladorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("pleasehire.me - Setup Assistant")
        self.root.geometry("520x500")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)
        
        # Variables de control
        self.topicos_input = tk.StringVar()
        self.plataforma_elegida = tk.StringVar()
        
        # Variables de progreso dinámico
        self.status_step_var = tk.StringVar()
        self.status_detail_var = tk.StringVar()
        
        self.mostrar_pantalla_bienvenida()

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_pantalla_bienvenida(self):
        self.limpiar_pantalla()
        
        frame = tk.Frame(self.root, bg=COLOR_BG, padx=40, pady=40)
        frame.pack(fill="both", expand=True)
        
        lbl_titulo = tk.Label(
            frame, text="¡Welcome to pleasehire.me!", 
            font=("Arial", 18, "bold"), bg=COLOR_BG, fg=COLOR_PRIMARY
        )
        lbl_titulo.pack(pady=(10, 20))
        
        lbl_descripcion = tk.Label(
            frame, 
            text="This smart bot assists your job hunting flow by securely\n"
                 "extracting target positions based on your core tech stack.\n"
                 "Everything runs under your local control via Playwright.",
            font=("Arial", 10), bg=COLOR_BG, fg="#4B5563", justify="center"
        )
        lbl_descripcion.pack(pady=10)
        
        btn_configurar = tk.Button(
            frame, text="Configure Search Profile →", font=("Arial", 11, "bold"),
            bg=COLOR_PRIMARY, fg="white", relief="flat", padx=20, pady=10,
            command=self.mostrar_pantalla_configuracion
        )
        btn_configurar.pack(pady=40)

    def mostrar_pantalla_configuracion(self):
        self.limpiar_pantalla()
        
        frame = tk.Frame(self.root, bg=COLOR_BG, padx=35, pady=25)
        frame.pack(fill="both", expand=True)
        
        # 1. Selección de plataforma
        lbl_plat = tk.Label(frame, text="1. Select target platform:", font=("Arial", 10, "bold"), bg=COLOR_BG, fg=COLOR_TEXT)
        lbl_plat.pack(anchor="w", pady=(10, 5))
        
        cbo_paginas = ttk.Combobox(frame, textvariable=self.plataforma_elegida, state="readonly", font=("Arial", 10))
        cbo_paginas['values'] = ("CompuTrabajo (Argentina)", "LinkedIn (Global/Remoto)")
        cbo_paginas.current(0)
        cbo_paginas.pack(fill="x", pady=5)
        
        # 2. Entrada de Tópicos / Keywords
        lbl_topicos = tk.Label(frame, text="2. Enter keywords / technical stack:", font=("Arial", 10, "bold"), bg=COLOR_BG, fg=COLOR_TEXT)
        lbl_topicos.pack(anchor="w", pady=(15, 5))
        
        txt_topicos = tk.Entry(frame, textvariable=self.topicos_input, font=("Arial", 10), relief="solid", bd=1)
        txt_topicos.pack(fill="x", pady=5)
        txt_topicos.insert(0, "Salesforce, React, Node, Developer")
        
        lbl_ayuda = tk.Label(frame, text="Separate terms with commas (e.g., Salesforce, React, Node)", font=("Arial", 8, "italic"), bg=COLOR_BG, fg="#6B7280")
        lbl_ayuda.pack(anchor="w", pady=2)
        
        # Botón de Lanzamiento de Flujo
        btn_siguiente = tk.Button(
            frame, text="Launch Engine 🚀", font=("Arial", 11, "bold"),
            bg=COLOR_SUCCESS, fg="white", relief="flat", pady=10,
            command=self.procesar_configuracion
        )
        btn_siguiente.pack(fill="x", pady=(35, 10))

    def procesar_configuracion(self):
        raw_topicos = self.topicos_input.get()
        if not raw_topicos.strip():
            messagebox.showwarning("Missing Data", "Please enter at least one topic keyword.")
            return
            
        # Parseo y limpieza de los tópicos ingresados
        self.array_topicos = [t.strip() for t in raw_topicos.split(",") if t.strip()]
        self.mostrar_pantalla_progreso()

    def mostrar_pantalla_progreso(self):
        """Pantalla intermedia de alto impacto visual para dar feedback en tiempo real."""
        self.limpiar_pantalla()
        
        frame = tk.Frame(self.root, bg=COLOR_BG, padx=40, pady=40)
        frame.pack(fill="both", expand=True)
        
        lbl_ejecucion = tk.Label(frame, text="pleasehire.me is processing...", font=("Arial", 14, "bold"), bg=COLOR_BG, fg=COLOR_PRIMARY)
        lbl_ejecucion.pack(pady=(10, 20))
        
        # Caja contenedora de estado / Pasos
        status_frame = tk.LabelFrame(frame, text=" Core Engine Status ", font=("Arial", 9, "bold"), bg=COLOR_BG, fg=COLOR_TEXT, padx=15, pady=15)
        status_frame.pack(fill="x", pady=10)
        
        self.lbl_step = tk.Label(status_frame, textvariable=self.status_step_var, font=("Arial", 11, "bold"), bg=COLOR_BG, fg=COLOR_SUCCESS, anchor="w")
        self.lbl_step.pack(fill="x", pady=2)
        
        self.lbl_detail = tk.Label(status_frame, textvariable=self.status_detail_var, font=("Arial", 9, "italic"), bg=COLOR_BG, fg="#4B5563", anchor="w", justify="left")
        self.lbl_detail.pack(fill="x", pady=(5, 2))
        
        # Barra de Progreso Visual
        lbl_progreso = tk.Label(frame, text="Overall Progress:", font=("Arial", 9), bg=COLOR_BG, fg=COLOR_TEXT)
        lbl_progreso.pack(anchor="w", pady=(20, 5))
        
        self.progress_bar = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(fill="x", pady=5)
        
        # Mensaje de advertencia para dar tranquilidad y paciencia al usuario
        lbl_advertencia = tk.Label(
            frame, 
            text="⚠️ PLEASE NOTE: A browser window might open for safety checks.\n"
                 "Do not close this application window. Look at your terminal\n"
                 "for technical logs. This cycle can take a few minutes.",
            font=("Arial", 8, "bold"), bg=COLOR_BG, fg="#B45309", justify="center"
        )
        lbl_advertencia.pack(pady=25)
        
        # Forzamos renderizado gráfico antes de pasarle el control al core síncrono
        self.root.update()
        self.lanzar_core_scraper()

    def actualizar_status(self, paso_titulo, detalle_texto, progreso_valor):
        """Actualiza las etiquetas y la barra de progreso forzando el dibujado en la UI."""
        self.status_step_var.set(paso_titulo)
        self.status_detail_var.set(detalle_texto)
        self.progress_bar['value'] = progreso_valor
        self.root.update()

    def lanzar_core_scraper(self):
        plataforma = self.plataforma_elegida.get()
        
        print("\n" + "="*60)
        print("🚀 SYSTEM INITIALIZED - CORE RUNNING PER TERMINAL")
        print("="*60)
        
        # --- PASO 1: Inicializando ---
        self.actualizar_status(
            "Step 1/4: Initializing Browser Environment", 
            f"Preparing security context for {plataforma}.\nClearing previous temp states...", 
            15
        )
        time.sleep(2) # Pausa dramática para que el usuario llegue a leer el paso
        
        # --- PASO 2: Login Manual / Validación de Sesión ---
        self.actualizar_status(
            "Step 2/4: Awaiting Secure Authentication", 
            "A visible browser opened. Please log in manually\n"
            "or stay active so we can capture the session state.", 
            40
        )
        
        # Ejecutamos tu flujo síncrono nativo (se queda esperando los 120s o lo que definiste)
        ejecutar_login_manual(plataforma)
        
        # --- PASO 3: Procesando Keywords de Extracción ---
        if os.path.exists("./auth.json"):
            self.actualizar_status(
                "Step 3/4: Extracting Targeted Job Offers", 
                f"Injecting tokens. Processing criteria list:\n{', '.join(self.array_topicos)}", 
                70
            )
            
            # Lanzamos el orquestador automático que ya sabemos que canta bingo impecable
            iniciar_scraping_automatico(self.array_topicos, plataforma)
            
            # --- PASO 4: Finalizado ---
            self.actualizar_status(
                "Step 4/4: Execution Finished Successfully!", 
                "All items parsed. The summary table has been printed\n"
                "directly in your Linux terminal. Check the outputs!", 
                100
            )
            
            messagebox.showinfo("Success!", "The scan cycle completed successfully. Check the results in the terminal.")
        else:
            self.actualizar_status("Execution Failed", "The authentication tokens could not be preserved.", 0)
            messagebox.showerror("Error", "The session could not be captured correctly. Please try again.")
            
        # Volvemos al estado inicial listo para otra ronda
        self.mostrar_pantalla_bienvenida()

if __name__ == "__main__":
    root = tk.Tk()
    app = BotPostuladorApp(root)
    root.mainloop()