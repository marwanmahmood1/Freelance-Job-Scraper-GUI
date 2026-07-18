import customtkinter as ctk
import threading
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
import pystray
from PIL import Image, ImageDraw

# --- MULTILINGUAL DICTIONARY ---
LANGUAGES = {
    "English": {
        "title": "Market Scraper",
        "status": "Ready. Enter jobs separated by commas.",
        "start": "▶ Start Scraping",
        "cancel": "✖ Cancel",
        "target": "🎯 Target Job Roles:",
        "theme": "🎨 Accent Color",
        "mode": "🌗 UI Mode",
        "lang": "🌐 Language",
        "footer": "Developed by Marwan Mahmoud © 2026"
    },
    "العربية": {
        "title": "مستخرج السوق",
        "status": "جاهز. أدخل الوظائف مفصولة بفواصل.",
        "start": "▶ ابدأ الاستخراج",
        "cancel": "✖ إلغاء",
        "target": "🎯 الوظائف المستهدفة:",
        "theme": "🎨 لون التمييز",
        "mode": "🌗 وضع الشاشة",
        "lang": "🌐 اللغة",
        "footer": "تم التطوير بواسطة مروان محمود © 2026"
    },
    "Español": {
        "title": "Extractor",
        "status": "Listo. Ingrese roles separados por comas.",
        "start": "▶ Iniciar",
        "cancel": "✖ Cancelar",
        "target": "🎯 Roles Objetivo:",
        "theme": "🎨 Color de Acento",
        "mode": "🌗 Modo de UI",
        "lang": "🌐 Idioma",
        "footer": "Desarrollado por Marwan Mahmoud © 2026"
    }
}

# --- DYNAMIC THEME PALETTES ---
THEME_COLORS = {
    "Standard Blue": {
        "btn": "#1f6aa5", "btn_hover": "#144870",
        "sidebar": ("#e6f0fa", "#0c1219"),
        "status": ("#d1e8ff", "#132538"),
        "log_bg": ("#f4f9ff", "#06090c"),
        "log_text": ("#003366", "#66b3ff")
    },
    "Galactic Purple": {
        "btn": "#8a2be2", "btn_hover": "#5c10a6",
        "sidebar": ("#f3e6fa", "#110c19"),
        "status": ("#e6ccff", "#261338"),
        "log_bg": ("#faf4ff", "#09060c"),
        "log_text": ("#330066", "#c266ff")
    },
    "Emerald Green": {
        "btn": "#2e8b57", "btn_hover": "#1e5c3a",
        "sidebar": ("#e6faec", "#0c1910"),
        "status": ("#ccffda", "#13381c"),
        "log_bg": ("#f4fff6", "#060c08"),
        "log_text": ("#004d00", "#4dff88")
    }
}

class JobScraperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Version number removed from title
        self.title("Market Scraper Pro")
        self.geometry("900x600") 
        self.minsize(750, 500)
        
        ctk.set_appearance_mode("Dark")
        self.current_lang = "English"
        self.current_theme = "Standard Blue"
        self.cancel_event = threading.Event()
        self.tray_icon = None

        self.bind("<Unmap>", self.on_minimize)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        colors = THEME_COLORS[self.current_theme]

        # --- LEFT SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=colors["sidebar"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=LANGUAGES[self.current_lang]["title"], font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        self.target_label = ctk.CTkLabel(self.sidebar_frame, text=LANGUAGES[self.current_lang]["target"], font=ctk.CTkFont(size=13, weight="bold"))
        self.target_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
        
        self.job_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="e.g. Robotics, Automation", height=35)
        self.job_entry.insert(0, "Software Engineer")
        self.job_entry.grid(row=2, column=0, padx=20, pady=(0, 25), sticky="ew")

        self.theme_label = ctk.CTkLabel(self.sidebar_frame, text=LANGUAGES[self.current_lang]["theme"], font=ctk.CTkFont(size=12))
        self.theme_label.grid(row=3, column=0, padx=20, sticky="w")
        self.theme_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Standard Blue", "Galactic Purple", "Emerald Green"], command=self.change_theme)
        self.theme_menu.grid(row=4, column=0, padx=20, pady=(5, 15), sticky="ew")
        
        self.mode_label = ctk.CTkLabel(self.sidebar_frame, text=LANGUAGES[self.current_lang]["mode"], font=ctk.CTkFont(size=12))
        self.mode_label.grid(row=5, column=0, padx=20, sticky="w")
        self.mode_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"], command=self.change_mode)
        self.mode_menu.grid(row=6, column=0, padx=20, pady=(5, 15), sticky="ew")

        self.lang_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["English", "العربية", "Español"], command=self.change_language)
        self.lang_menu.grid(row=8, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.footer_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text=LANGUAGES[self.current_lang]["footer"], 
            font=ctk.CTkFont(size=11, slant="italic"), 
            text_color=("gray40", "gray75"), 
            wraplength=180
        )
        self.footer_label.grid(row=9, column=0, padx=20, pady=(10, 20))

        # --- RIGHT MAIN AREA ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color=colors["status"], corner_radius=10)
        self.status_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.status_label = ctk.CTkLabel(self.status_frame, text=LANGUAGES[self.current_lang]["status"], font=ctk.CTkFont(size=16, weight="bold"), text_color="gray")
        self.status_label.pack(pady=15)

        self.log_box = ctk.CTkTextbox(self.main_frame, font=ctk.CTkFont(family="Consolas", size=13), fg_color=colors["log_bg"], text_color=colors["log_text"])
        self.log_box.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        self.log_box.insert("0.0", "--- Terminal Initialized ---\nSystem ready for extraction...\n")
        self.log_box.configure(state="disabled")

        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, sticky="ew")
        self.action_frame.grid_columnconfigure((0, 1), weight=1)

        self.start_btn = ctk.CTkButton(self.action_frame, text=LANGUAGES[self.current_lang]["start"], font=ctk.CTkFont(size=15, weight="bold"), fg_color=colors["btn"], hover_color=colors["btn_hover"], height=45, command=self.start_process)
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(self.action_frame, text=LANGUAGES[self.current_lang]["cancel"], font=ctk.CTkFont(size=15, weight="bold"), fg_color="#b22222", hover_color="#8b0000", height=45, state="disabled", command=self.cancel_process)
        self.cancel_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))

    # --- SYSTEM TRAY ---
    def on_minimize(self, event):
        if event.widget == self and self.state() == 'iconic':
            self.withdraw()
            self.create_tray_icon()

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color=(31, 106, 165))
        draw = ImageDraw.Draw(image)
        draw.ellipse((10, 10, 54, 54), fill="white")
        menu = pystray.Menu(
            pystray.MenuItem("Restore Application", self.restore_from_tray, default=True),
            pystray.MenuItem("Exit", self.quit_from_tray)
        )
        self.tray_icon = pystray.Icon("MarketScraper", image, "Market Scraper Running", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon, item):
        current_time = time.time()
        if current_time - getattr(self, 'last_click_time', 0) < 0.5:
            self.tray_icon.stop()
            self.after(0, self.deiconify)
        self.last_click_time = current_time

    def quit_from_tray(self, icon, item):
        self.tray_icon.stop()
        self.quit()

    # --- SETTINGS FUNCTIONS ---
    def change_language(self, choice):
        self.current_lang = choice
        lang = LANGUAGES[choice]
        self.logo_label.configure(text=lang["title"])
        self.target_label.configure(text=lang["target"])
        self.theme_label.configure(text=lang["theme"])
        self.mode_label.configure(text=lang["mode"])
        self.start_btn.configure(text=lang["start"])
        self.cancel_btn.configure(text=lang["cancel"])
        self.footer_label.configure(text=lang["footer"])
        if "Ready" in self.status_label.cget("text") or "جاهز" in self.status_label.cget("text") or "Listo" in self.status_label.cget("text"):
            self.status_label.configure(text=lang["status"])

    def change_mode(self, choice):
        ctk.set_appearance_mode(choice)

    def change_theme(self, choice):
        self.current_theme = choice
        colors = THEME_COLORS[choice]
        self.sidebar_frame.configure(fg_color=colors["sidebar"])
        self.status_frame.configure(fg_color=colors["status"])
        self.log_box.configure(fg_color=colors["log_bg"], text_color=colors["log_text"])
        self.start_btn.configure(fg_color=colors["btn"], hover_color=colors["btn_hover"])

    # --- UNIVERSAL BROWSER FALLBACK ---
    def create_universal_webdriver(self):
        self.log("[System] Detecting available web browsers...")
        
        # 1. Try Google Chrome
        try:
            options = ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
            driver = webdriver.Chrome(options=options)
            self.log("[System] Google Chrome connected successfully.")
            return driver
        except Exception:
            pass

        # 2. Try Microsoft Edge (Built into Windows)
        try:
            options = EdgeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            driver = webdriver.Edge(options=options)
            self.log("[System] Microsoft Edge connected successfully.")
            return driver
        except Exception:
            pass

        # 3. Try Mozilla Firefox
        try:
            options = FirefoxOptions()
            driver = webdriver.Firefox(options=options)
            self.log("[System] Mozilla Firefox connected successfully.")
            return driver
        except Exception:
            raise Exception("No supported browser found. Please install Chrome, Edge, or Firefox.")

    # --- SCRAPER LOGIC (Batch Processing Enabled) ---
    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def start_process(self):
        raw_input = self.job_entry.get().strip()
        if not raw_input:
            self.status_label.configure(text="Please enter at least one job title!", text_color="red")
            return

        # Split input by commas into a list
        target_jobs = [job.strip() for job in raw_input.split(',') if job.strip()]

        if not target_jobs:
            self.status_label.configure(text="Please enter valid job titles!", text_color="red")
            return

        self.cancel_event.clear()
        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.job_entry.configure(state="disabled")
        self.log_box.configure(state="normal")
        self.log_box.delete("0.0", "end") 
        self.log_box.configure(state="disabled")
        self.status_label.configure(text="Running Batch Analysis...", text_color="#f39c12")
        
        threading.Thread(target=self.run_pipeline, args=(target_jobs,), daemon=True).start()

    def cancel_process(self):
        self.log("\n[!] Cancellation requested... halting after current task.")
        self.status_label.configure(text="Cancelling...", text_color="red")
        self.cancel_event.set()
        self.cancel_btn.configure(state="disabled")

    def run_pipeline(self, target_jobs):
        driver = None
        try:
            # Launch the universal browser sequence
            driver = self.create_universal_webdriver()

            # Loop through each job in the list
            for job in target_jobs:
                if self.cancel_event.is_set(): break
                
                self.log(f"\n[*] === Targeting: {job} ===")
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop', f'{job.replace(" ", "_")}_Data')
                if not os.path.exists(desktop_path):
                    os.makedirs(desktop_path)
                
                formatted_job = job.replace(" ", "%20")
                url = f"https://www.linkedin.com/jobs/search?keywords={formatted_job}&location=Egypt&f_E=1%2C2"
                
                driver.get(url)
                time.sleep(4)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_cards = soup.find_all('div', class_='base-card')
                jobs_data = []

                for card in job_cards:
                    if self.cancel_event.is_set(): break 
                    try:
                        title = card.find('h3', class_='base-search-card__title').text.strip()
                        company = card.find('h4', class_='base-search-card__subtitle').text.strip()
                        link = card.find('a', class_='base-card__full-link')['href']
                        jobs_data.append({'Job Title': title, 'Company': company, 'Link': link})
                    except AttributeError:
                        continue

                if self.cancel_event.is_set(): break

                df = pd.DataFrame(jobs_data)
                self.log(f"[✓] Extracted {len(df)} listings for {job}.")

                csv_path = os.path.join(desktop_path, f"{job.replace(' ', '_')}_Market_Data.csv")
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            if driver:
                driver.quit()
            
            if self.cancel_event.is_set():
                self.reset_ui("Cancelled by user.")
                return
            
            self.log(f"\n[Success] Batch processing complete! All folders saved to Desktop.")
            self.reset_ui("Batch Complete! Files saved to Desktop.", success=True)

        except Exception as e:
            self.log(f"\nCRITICAL ERROR: {str(e)}")
            self.reset_ui("Process failed due to error.", success=False)
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def reset_ui(self, message, success=False):
        color = "#2ecc71" if success else "#e74c3c"
        self.status_label.configure(text=message, text_color=color)
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.job_entry.configure(state="normal")

if __name__ == "__main__":
    app = JobScraperApp()
    app.mainloop()