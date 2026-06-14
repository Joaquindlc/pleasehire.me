"""
File: main.py
----------------
Punto de entrada principal. Maneja la interfaz gráfica (Tkinter) y
orquesta síncronamente los ciclos de autenticación y scraping.
Diseñado para el Showcase de Code in Place.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from scraper import ejecutar_login_manual, iniciar_scraping_automatico

# Configuración estética básica
COLOR_BG = "#F3F4F6"
COLOR_PRIMARY = "#1D4ED8"
COLOR_SUCCESS = "#10B981"

class BotPostuladorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot Postulador Setup")
        self.root.geometry("500x450")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)
        
        # Variables de control
        self.topicos_input = tk.StringVar()
        self.plataforma_elegida = tk.StringVar()
        
        self.mostrar_pantalla_bienvenida()

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_pantalla_bienvenida(self):
        self.limpiar_pantalla()
        
        frame = tk.Frame(self.root, bg=COLOR_BG, padx=40, pady=50)
        frame.pack(fill="both", expand=True)
        
        lbl_titulo = tk.Label(frame, text="¡Welcome to pleasehire.me!", font=("Arial", 18, "bold"), bg=COLOR_BG, fg="#111827")
        lbl_titulo.pack(pady=10)
        
        lbl_desc = tk.Label(
            frame, 
            text="This tool automates the search for local job listings\nand processes the data securely within your environment.",
            font=("Arial", 10), bg=COLOR_BG, fg="#4B5563", justify="center"
        )
        lbl_desc.pack(pady=15)
        
        lbl_badge = tk.Label(frame, text="Designed exclusively for the Code in Place Showcase.", font=("Arial", 9, "italic"), bg=COLOR_BG, fg="#9CA3AF")
        lbl_badge.pack(pady=10)
        
        btn_comenzar = tk.Button(
            frame, text="Get Started Settings →", font=("Arial", 11, "bold"),
            bg=COLOR_PRIMARY, fg="white", relief="flat", padx=20, pady=8,
            command=self.mostrar_pantalla_configuracion
        )
        btn_comenzar.pack(pady=25)

    def mostrar_pantalla_configuracion(self):
        self.limpiar_pantalla()
        
        frame = tk.Frame(self.root, bg=COLOR_BG, padx=30, pady=25)
        frame.pack(fill="both", expand=True)
        
        # 1. Selección de plataforma
        lbl_plat = tk.Label(frame, text="1. Select the destination platform:", font=("Arial", 10, "bold"), bg=COLOR_BG, fg="#374151")
        lbl_plat.pack(anchor="w", pady=(10, 5))
        
        cbo_paginas = ttk.Combobox(frame, textvariable=self.plataforma_elegida, state="readonly", font=("Arial", 10))
        cbo_paginas['values'] = ("CompuTrabajo (Argentina)",)
        cbo_paginas.current(0)
        cbo_paginas.pack(fill="x", pady=5)
        
        # 2. Entrada de Tópicos
        lbl_topicos = tk.Label(frame, text="2. Enter the topics/keywords:", font=("Arial", 10, "bold"), bg=COLOR_BG, fg="#374151")
        lbl_topicos.pack(anchor="w", pady=(15, 5))
        
        txt_topicos = tk.Entry(frame, textvariable=self.topicos_input, font=("Arial", 10), relief="solid", bd=1)
        txt_topicos.pack(fill="x", pady=5)
        txt_topicos.insert(0, "Salesforce, React, Node, Developer")
        
        lbl_ayuda = tk.Label(frame, text="Separate the items with commas (ej: React, Node, Python)", font=("Arial", 8, "italic"), bg=COLOR_BG, fg="#6B7280")
        lbl_ayuda.pack(anchor="w", pady=2)
        
        btn_siguiente = tk.Button(
            frame, text="Next step →", font=("Arial", 10, "bold"),
            bg=COLOR_PRIMARY, fg="white", relief="flat", padx=15, pady=6,
            command=self.procesar_configuracion
        )
        btn_siguiente.pack(anchor="e", pady=30)

    def procesar_configuracion(self):
        entrada = self.topicos_input.get().strip()
        if not entrada:
            messagebox.showwarning("Incomplete Fields", "Please enter at least one search term.")
            return
            
        # We parse the topics into a clean array
        self.array_topicos = [t.strip() for t in entrada.split(",") if t.strip()]
        self.mostrar_pantalla_autenticacion()

    def mostrar_pantalla_autenticacion(self):
        self.limpiar_pantalla()
        
        frame = tk.Frame(self.root, bg=COLOR_BG, padx=30, pady=30)
        frame.pack(fill="both", expand=True)
        
        lbl_auth = tk.Label(frame, text="3. Local Session Verification", font=("Arial", 12, "bold"), bg=COLOR_BG, fg="#111827")
        lbl_auth.pack(anchor="w", pady=10)
        
        lbl_info = tk.Label(
            frame, 
            text="⚠️ No local login cookies were detected.\nYou'll need to sign in as a ‘New User’ to log in.",
            font=("Arial", 9), bg=COLOR_BG, fg="#4B5563", justify="left"
        )
        lbl_info.pack(anchor="w", pady=10)
        
        self.chk_forzar = tk.BooleanVar(value=True)
        chk_box = tk.Checkbutton(
            frame, text="Log in as a new user (Clear previous session)",
            variable=self.chk_forzar, bg=COLOR_BG, font=("Arial", 9)
        )
        chk_box.pack(anchor="w", pady=15)
        

        self.btn_accion = tk.Button(
            frame, text="Start as a New User (Manual Login)", font=("Arial", 11, "bold"),
            bg=COLOR_SUCCESS, fg="white", relief="flat", pady=10,
            command=self.lanzar_flujo_scraper
        )
        self.btn_accion.pack(fill="x", pady=10)

    def lanzar_flujo_scraper(self):
        # We hide the UI to draw attention to the terminal
        self.btn_accion.config(text="Procesando en Terminal...", state="disabled", bg="#9CA3AF")
        self.root.update()
        
        print("\n" + "="*60)
        print("🚀 SYSTEM INITIALIZED - CORE RUNNING PER TERMINAL")
        print("="*60)
        print(f"📋 Search platform: {self.plataforma_elegida.get()}")
        print(f"📝 Topics: {self.array_topicos}")
        
        #1. Fixed Human Login Flow (120 seconds to interact securely with Google)
        ejecutar_login_manual()
        
        #2. Defensive validation before proceed
        if os.path.exists("./auth.json"):
            #3. Automated scraping using the captured credentials
            iniciar_scraping_automatico(self.array_topicos)
            messagebox.showinfo("Success!", "The scan cycle completed successfully. Check the results in the terminal.")
        else:
            messagebox.showerror("Error", "The session could not be captured correctly. Please try again.")
            
        self.mostrar_pantalla_bienvenida()

if __name__ == "__main__":
    root = tk.Tk()
    app = BotPostuladorApp(root)
    root.mainloop()