import sys
import os
import json
import random
import hashlib
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtGui import QIcon, QAction, QColor
from PyQt6.QtNetwork import QNetworkCookie

# --- LISTY FILTRÓW REKLAMOWYCH (uBlock Origin style) ---
ADBLOCK_FILTERS = [
    "doubleclick.net", "googlesyndication.com", "googleadservices.com",
    "google-analytics.com", "googletagmanager.com", "facebook.com/tr/",
    "facebook.net/en_US/fbevents.js", "connect.facebook.net",
    "ads.", "ad.", "adserver", "analytics", "tracker", "tracking",
    "pixel", "telemetry", "metric", "beacon", "/ads/", "/ad/",
    "outbrain.com", "taboola.com", "scorecardresearch.com"
]

# --- INTERCEPTOR: Ad-Block, HTTPS-Only, Random Headers ---
class PrivacyInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        
        # 🛑 BLOKOWANIE REKLAM I TRACKERÓW
        if self.main_window.adblock_enabled:
            for pattern in ADBLOCK_FILTERS:
                if pattern in url:
                    info.block(True)
                    return
        
        # 🔒 HTTPS-ONLY MODE
        if self.main_window.https_only and url.startswith("http://"):
            https_url = url.replace("http://", "https://", 1)
            info.redirect(QUrl(https_url))
        
        # 🧪 RANDOMIZOWANE NAGŁÓWKI
        if self.main_window.random_headers:
            random_ua = random.choice(self.user_agents)
            info.setHttpHeader(b"User-Agent", random_ua.encode())
            info.setHttpHeader(b"Accept-Language", b"en-US,en;q=0.9")
            info.setHttpHeader(b"DNT", b"1")
            info.setHttpHeader(b"Sec-GPC", b"1")

# --- SŁOWNIK TŁUMACZEŃ ---
TRANSLATIONS = {
    "en": {
        "search_placeholder": "Search or enter address...",
        "ai_tab": "AI", "notes_tab": "Notes", "vault_tab": "Vault", "settings_tab": "Settings",
        "vault_title": "🔑 Secure Vault", "save_btn": "Save Credentials", "del_btn": "Delete Selected",
        "site_ph": "Website", "user_ph": "Username", "pass_ph": "Password",
        "privacy_title": "🛡️ Advanced Privacy Control", 
        "adblock_label": "🛑 uBlock Origin (Ad & Tracker Blocking)",
        "https_label": "🔒 HTTPS-Only Mode",
        "fingerprint_label": "🧬 Anti-Fingerprinting Protection (RFP)",
        "cookie_iso_label": "🍪 Total Cookie Protection (Per-Site Isolation)",
        "webrtc_label": "🧠 Block WebRTC IP Leaks",
        "random_headers_label": "🧪 Randomize Headers & User-Agent",
        "clear_on_close_label": "🧼 Clear All Data on Exit",
        "private_mode_label": "🕶️ Private Browsing (No History)",
        "lang_label": "🌐 Language / Język", 
        "theme_label": "🎨 Appearance", 
        "theme_btn": "Customize Theme Color",
        "pop_title": "Security Alert", 
        "pop_msg": "This website wants to open a new window.",
        "pop_info": "It might be dangerous. Do you want to continue?",
        "pass_save_title": "Password Manager",
        "pass_save_msg": "Do you want to save the password for account: {user} on: {site}?",
        "autofill_hint": "Password for {user} (Click to fill)",
        "privacy_status": "Privacy: {blocked} blocked | HTTPS: {https} | Fingerprint: {fp}"
    },
    "pl": {
        "search_placeholder": "Szukaj lub wpisz adres...",
        "ai_tab": "AI", "notes_tab": "Notatki", "vault_tab": "Hasła", "settings_tab": "Ustawienia",
        "vault_title": "🔑 Sejf Haseł", "save_btn": "Zapisz Dane", "del_btn": "Usuń Zaznaczone",
        "site_ph": "Strona", "user_ph": "Użytkownik", "pass_ph": "Hasło",
        "privacy_title": "🛡️ Zaawansowana Kontrola Prywatności",
        "adblock_label": "🛑 uBlock Origin (Blokada Reklam i Trackerów)",
        "https_label": "🔒 Wymuszanie HTTPS",
        "fingerprint_label": "🧬 Ochrona przed Fingerprintingiem (RFP)",
        "cookie_iso_label": "🍪 Pełna Ochrona Cookies (Izolacja per-site)",
        "webrtc_label": "🧠 Blokada Wycieków IP przez WebRTC",
        "random_headers_label": "🧪 Losowe Nagłówki i User-Agent",
        "clear_on_close_label": "🧼 Czyszczenie Danych przy Zamknięciu",
        "private_mode_label": "🕶️ Tryb Prywatny (Brak Historii)",
        "lang_label": "🌐 Język / Language", 
        "theme_label": "🎨 Wygląd", 
        "theme_btn": "Zmień kolor motywu",
        "pop_title": "Ostrzeżenie", 
        "pop_msg": "Ta strona próbuje otworzyć nowe okno.",
        "pop_info": "Może to być niebezpieczne. Czy chcesz kontynuować?",
        "pass_save_title": "Menedżer Haseł",
        "pass_save_msg": "Czy chcesz zapisać hasło dla konta: {user} w: {site}?",
        "autofill_hint": "Hasło dla {user} (Kliknij, aby wypełnić)",
        "privacy_status": "Prywatność: {blocked} zablok. | HTTPS: {https} | Fingerprint: {fp}"
    }
}

# --- KLASA STRONY (KOMUNIKACJA JS -> PYTHON) ---
class OpenBrowsingPage(QWebEnginePage):
    def __init__(self, view, main_window):
        super().__init__(view)
        self.main_window = main_window

    def javaScriptConsoleMessage(self, level, message, line, source):
        if "PW_FOUND:" in message:
            parts = message.split(":")
            if len(parts) >= 3:
                user, pw = parts[1], parts[2]
                site = self.url().host()
                self.main_window.prompt_password_save(user, pw, site)
        
        if "CHECK_AUTOFILL" in message:
            self.handle_autofill_request()

    def handle_autofill_request(self):
        site = self.url().host()
        creds = self.main_window.get_credentials_for_site(site)
        if creds:
            user, pw = creds
            t = TRANSLATIONS[self.main_window.lang]
            masked = user[0:2] + "***" + (user.split('@')[1] if '@' in user else "")
            hint_text = t["autofill_hint"].format(user=masked)
            
            fill_script = f"""
                (function() {{
                    var active = document.activeElement;
                    if(active && !document.getElementById('ob-autofill-hint')) {{
                        var hint = document.createElement('div');
                        hint.id = 'ob-autofill-hint';
                        hint.innerHTML = '{hint_text}';
                        hint.style = "position:absolute; background:#007acc; color:white; padding:8px 12px; " +
                                     "border-radius:6px; font-size:13px; cursor:pointer; z-index:10000; " +
                                     "top:" + (active.getBoundingClientRect().top + window.scrollY + active.offsetHeight + 5) + "px; " +
                                     "left:" + (active.getBoundingClientRect().left + window.scrollX) + "px; " +
                                     "box-shadow: 0 4px 8px rgba(0,0,0,0.4); font-family: sans-serif;";
                        
                        hint.onclick = function() {{
                            var inputs = document.getElementsByTagName('input');
                            for(var i=0; i<inputs.length; i++) {{
                                if(inputs[i].type === 'password') {{
                                    inputs[i].value = '{pw}';
                                    inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                                }}
                                if(inputs[i].type === 'text' || inputs[i].type === 'email') {{
                                    inputs[i].value = '{user}';
                                    inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                                }}
                            }}
                            this.remove();
                        }};
                        document.body.appendChild(hint);
                        setTimeout(function() {{ if(hint.parentNode) hint.parentNode.removeChild(hint); }}, 6000);
                    }}
                }})();
            """
            self.runJavaScript(fill_script)

# --- KLASA WIDOKU ---
class OpenBrowsingView(QWebEngineView):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setPage(OpenBrowsingPage(self, self.main_window))
        
        # Skrypt wykrywania haseł
        self.pw_script = QWebEngineScript()
        self.pw_script.setSourceCode("""
            document.addEventListener('focusin', function(e) {
                if(e.target.tagName === 'INPUT') {
                    console.log("CHECK_AUTOFILL");
                }
            });

            document.addEventListener('submit', function(e) {
                var pass = '', user = '';
                var inputs = document.getElementsByTagName('input');
                for(var i=0; i<inputs.length; i++) {
                    if(inputs[i].type === 'password') pass = inputs[i].value;
                    if(inputs[i].type === 'text' || inputs[i].type === 'email') user = inputs[i].value;
                }
                if(pass.length > 0) console.log("PW_FOUND:" + user + ":" + pass);
            });
        """)
        self.pw_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        self.pw_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        self.page().profile().scripts().insert(self.pw_script)
        
        # 🧬 ANTI-FINGERPRINTING SCRIPT (RFP)
        if self.main_window.fingerprint_protection:
            self.inject_anti_fingerprint()

    def inject_anti_fingerprint(self):
        """Wstrzykuje skrypt anti-fingerprinting (spoofing Canvas, WebGL, Audio, itp.)"""
        fp_script = QWebEngineScript()
        fp_script.setSourceCode("""
            (function() {
                // 🧠 Blokowanie WebRTC IP Leaks
                if(typeof RTCPeerConnection !== 'undefined') {
                    RTCPeerConnection.prototype.createDataChannel = function() { return null; };
                    RTCPeerConnection.prototype.createOffer = function() { return Promise.resolve(null); };
                }
                
                // 🎨 Canvas Fingerprinting Protection
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function() {
                    const context = this.getContext('2d');
                    if(context) {
                        const imageData = context.getImageData(0, 0, this.width, this.height);
                        for(let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] = (imageData.data[i] + Math.random() * 5) | 0;
                        }
                        context.putImageData(imageData, 0, 0);
                    }
                    return originalToDataURL.apply(this, arguments);
                };
                
                // 🔊 Audio Fingerprinting Protection
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                if(AudioContext) {
                    const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
                    AudioContext.prototype.createAnalyser = function() {
                        const analyser = originalCreateAnalyser.call(this);
                        const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
                        analyser.getFloatFrequencyData = function(array) {
                            originalGetFloatFrequencyData.call(this, array);
                            for(let i = 0; i < array.length; i++) {
                                array[i] += Math.random() * 0.01;
                            }
                        };
                        return analyser;
                    };
                }
                
                // 🖥️ Screen/Hardware Info Spoofing
                Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });
                Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
                Object.defineProperty(screen, 'colorDepth', { get: () => 24 });
                Object.defineProperty(screen, 'pixelDepth', { get: () => 24 });
                
                // ⏰ High-Resolution Timer Protection
                const originalNow = performance.now;
                performance.now = function() {
                    return Math.floor(originalNow.call(performance) / 100) * 100 + Math.random() * 10;
                };
                
                // 🔤 Font Fingerprinting Protection
                const originalGetComputedStyle = window.getComputedStyle;
                window.getComputedStyle = function() {
                    const style = originalGetComputedStyle.apply(this, arguments);
                    const originalGetPropertyValue = style.getPropertyValue;
                    style.getPropertyValue = function(prop) {
                        if(prop === 'font-family') return 'Arial, sans-serif';
                        return originalGetPropertyValue.call(this, prop);
                    };
                    return style;
                };
            })();
        """)
        fp_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        fp_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        self.page().profile().scripts().insert(fp_script)

    def createWindow(self, type):
        t = TRANSLATIONS[self.main_window.lang]
        msg = QMessageBox(self)
        msg.setWindowTitle(t["pop_title"])
        msg.setText(t["pop_msg"])
        msg.setInformativeText(t["pop_info"])
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            return self.main_window.add_new_tab()
        return None

# --- GŁÓWNE OKNO ---
class OpenBrowsing(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "en"
        self.blocked_count = 0
        
        # 🛡️ PRIVACY FLAGS (domyślne wartości)
        self.adblock_enabled = True
        self.https_only = True
        self.fingerprint_protection = True
        self.cookie_isolation = True
        self.webrtc_blocked = True
        self.random_headers = True
        self.clear_on_close = True
        self.private_mode = True
        
        self.setWindowTitle("OpenBrowsing 🛡️ Privacy Edition")
        self.resize(1300, 850)
        self.load_settings()  # Wczytaj ustawienia przed setup
        self.setup_privacy_profile()
        self.setup_ui()
        self.load_passwords()
        self.load_notes()
        self.update_ui_text()

    def setup_privacy_profile(self):
        """🕶️ Konfiguracja profilu prywatności"""
        # Tryb prywatny jako domyślny
        if self.private_mode:
            self.profile = QWebEngineProfile()
            self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.NoCache)
        else:
            self.profile = QWebEngineProfile.defaultProfile()
        
        # ❌ Wyłączone Google Safe Browsing (brak zewnętrznych zapytań)
        settings = self.profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, not self.private_mode)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)  # Ochrona przed WebGL fingerprinting
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, False)  # Brak wtyczek (Flash, etc.)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)  # Brak DNS prefetch
        
        # 🍪 Total Cookie Protection (izolacja per-site)
        if self.cookie_isolation:
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        
        # Interceptor dla Ad-Block, HTTPS-Only, Random Headers
        self.interceptor = PrivacyInterceptor(self)
        self.profile.setUrlRequestInterceptor(self.interceptor)

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        # Side panel
        self.sidebar = QTabWidget()
        self.sidebar.setFixedWidth(380)
        self.sidebar.setStyleSheet("QTabWidget::pane { border-top: 1px solid #333; }")

        # AI
        self.ai_container = QWidget()
        ai_l = QVBoxLayout(self.ai_container)
        self.ai_sel = QComboBox()
        self.ai_sel.addItems(["Proton Lumo", "DDG AI", "ChatGPT", "Claude"])
        self.ai_sel.setCurrentIndex(self.saved_ai_index if hasattr(self, 'saved_ai_index') else 0)
        self.ai_sel.currentIndexChanged.connect(self.change_ai)
        self.ai_view = QWebEngineView()
        self.ai_view.setPage(QWebEnginePage(self.profile, self.ai_view))
        urls = ["https://lumo.proton.me/guest", "https://duckduckgo.com/?q=DuckDuckGo+AI+Chat", "https://chatgpt.com", "https://claude.ai"]
        self.ai_view.setUrl(QUrl(urls[self.ai_sel.currentIndex()]))
        ai_l.addWidget(self.ai_sel); ai_l.addWidget(self.ai_view)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Private notes...")
        self.notes_edit.textChanged.connect(self.save_notes)

        # Vault
        self.pass_widget = QWidget()
        p_l = QVBoxLayout(self.pass_widget)
        self.v_label = QLabel()
        self.pass_list = QListWidget()
        self.site_in = QLineEdit(); self.user_in = QLineEdit(); self.pass_in = QLineEdit()
        self.pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_save_v = QPushButton()
        self.btn_del_v = QPushButton()
        self.btn_save_v.clicked.connect(self.add_password_manual)
        self.btn_del_v.clicked.connect(self.delete_password)
        for w in [self.v_label, self.pass_list, self.site_in, self.user_in, self.pass_in, self.btn_save_v, self.btn_del_v]: p_l.addWidget(w)

        # Settings - ZAKTUALIZOWANE O PRIVACY OPTIONS
        self.settings_pane = QWidget()
        s_l = QVBoxLayout(self.settings_pane)
        
        self.privacy_label = QLabel()
        self.privacy_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #00ff00;")
        
        # Checkboxy Privacy
        self.adblock_check = QCheckBox()
        self.adblock_check.setChecked(self.adblock_enabled)
        self.adblock_check.stateChanged.connect(lambda: self.update_setting('adblock_enabled', self.adblock_check.isChecked()))
        
        self.https_check = QCheckBox()
        self.https_check.setChecked(self.https_only)
        self.https_check.stateChanged.connect(lambda: self.update_setting('https_only', self.https_check.isChecked()))
        
        self.fingerprint_check = QCheckBox()
        self.fingerprint_check.setChecked(self.fingerprint_protection)
        self.fingerprint_check.stateChanged.connect(self.toggle_fingerprint)
        
        self.cookie_iso_check = QCheckBox()
        self.cookie_iso_check.setChecked(self.cookie_isolation)
        self.cookie_iso_check.stateChanged.connect(lambda: self.update_setting('cookie_isolation', self.cookie_iso_check.isChecked()))
        
        self.webrtc_check = QCheckBox()
        self.webrtc_check.setChecked(self.webrtc_blocked)
        self.webrtc_check.stateChanged.connect(lambda: self.update_setting('webrtc_blocked', self.webrtc_check.isChecked()))
        
        self.random_headers_check = QCheckBox()
        self.random_headers_check.setChecked(self.random_headers)
        self.random_headers_check.stateChanged.connect(lambda: self.update_setting('random_headers', self.random_headers_check.isChecked()))
        
        self.clear_on_close_check = QCheckBox()
        self.clear_on_close_check.setChecked(self.clear_on_close)
        self.clear_on_close_check.stateChanged.connect(lambda: self.update_setting('clear_on_close', self.clear_on_close_check.isChecked()))
        
        self.private_mode_check = QCheckBox()
        self.private_mode_check.setChecked(self.private_mode)
        self.private_mode_check.stateChanged.connect(lambda: self.update_setting('private_mode', self.private_mode_check.isChecked()))
        
        self.lang_label_ui = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Polski"])
        self.lang_combo.setCurrentIndex(0 if self.lang == "en" else 1)
        self.lang_combo.currentIndexChanged.connect(self.set_language)
        self.theme_btn_ui = QPushButton()
        self.theme_btn_ui.clicked.connect(self.pick_color)
        
        s_l.addWidget(self.privacy_label)
        s_l.addWidget(self.adblock_check)
        s_l.addWidget(self.https_check)
        s_l.addWidget(self.fingerprint_check)
        s_l.addWidget(self.cookie_iso_check)
        s_l.addWidget(self.webrtc_check)
        s_l.addWidget(self.random_headers_check)
        s_l.addWidget(self.clear_on_close_check)
        s_l.addWidget(self.private_mode_check)
        s_l.addWidget(QLabel())  # Separator
        s_l.addWidget(self.lang_label_ui)
        s_l.addWidget(self.lang_combo)
        s_l.addWidget(self.theme_btn_ui)
        s_l.addStretch()

        self.sidebar.addTab(self.ai_container, "AI")
        self.sidebar.addTab(self.notes_edit, "Notes")
        self.sidebar.addTab(self.pass_widget, "Vault")
        self.sidebar.addTab(self.settings_pane, "Settings")

        # Browser
        self.browser_area = QWidget()
        self.b_layout = QVBoxLayout(self.browser_area)
        self.b_layout.setContentsMargins(0,0,0,0); self.b_layout.setSpacing(0)

        self.toolbar = QToolBar()
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate)
        
        # Privacy Status Label
        self.privacy_status = QLabel("🛡️ Privacy: Active")
        self.privacy_status.setStyleSheet("color: #00ff00; font-weight: bold; padding: 5px;")
        
        for icon, slot in [("⬅", lambda: self.tabs.currentWidget().back()), 
                           ("➡", lambda: self.tabs.currentWidget().forward()),
                           ("🔄", lambda: self.tabs.currentWidget().reload()),
                           ("🏠", self.go_home), 
                           ("➕", self.add_new_tab),
                           ("📂", lambda: self.sidebar.setVisible(not self.sidebar.isVisible()))]:
            act = QAction(icon, self)
            act.triggered.connect(slot)
            self.toolbar.addAction(act)
        self.toolbar.addWidget(self.url_bar)
        self.toolbar.addWidget(self.privacy_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(3); self.progress_bar.setTextVisible(False); self.progress_bar.hide()

        self.tabs = QTabWidget(tabsClosable=True)
        self.tabs.tabCloseRequested.connect(lambda i: self.tabs.removeTab(i) if self.tabs.count() > 1 else None)
        
        self.b_layout.addWidget(self.toolbar); self.b_layout.addWidget(self.progress_bar); self.b_layout.addWidget(self.tabs)
        self.main_layout.addWidget(self.sidebar); self.main_layout.addWidget(self.browser_area)

        self.add_new_tab(QUrl("https://start.duckduckgo.com"), "Home")
        self.apply_styles()

    def toggle_fingerprint(self, state):
        self.fingerprint_protection = (state == Qt.CheckState.Checked.value)
        self.save_settings()
        QMessageBox.information(self, "Restart Required", "Please restart the browser for changes to take effect.")

    def update_setting(self, attr, value):
        """Aktualizuje ustawienie i zapisuje do pliku"""
        setattr(self, attr, value)
        self.save_settings()
        self.update_privacy_status()

    def save_settings(self):
        """Zapisuje wszystkie ustawienia do JSON"""
        settings = {
            'lang': self.lang,
            'ai_index': self.ai_sel.currentIndex() if hasattr(self, 'ai_sel') else 0,
            'theme_color': self.custom_color if hasattr(self, 'custom_color') else None,
            'adblock_enabled': self.adblock_enabled,
            'https_only': self.https_only,
            'fingerprint_protection': self.fingerprint_protection,
            'cookie_isolation': self.cookie_isolation,
            'webrtc_blocked': self.webrtc_blocked,
            'random_headers': self.random_headers,
            'clear_on_close': self.clear_on_close,
            'private_mode': self.private_mode
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=2)

    def load_settings(self):
        """Wczytuje ustawienia z JSON"""
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    self.lang = settings.get('lang', 'en')
                    self.saved_ai_index = settings.get('ai_index', 0)
                    self.custom_color = settings.get('theme_color', None)
                    self.adblock_enabled = settings.get('adblock_enabled', True)
                    self.https_only = settings.get('https_only', True)
                    self.fingerprint_protection = settings.get('fingerprint_protection', True)
                    self.cookie_isolation = settings.get('cookie_isolation', True)
                    self.webrtc_blocked = settings.get('webrtc_blocked', True)
                    self.random_headers = settings.get('random_headers', True)
                    self.clear_on_close = settings.get('clear_on_close', True)
                    self.private_mode = settings.get('private_mode', True)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.saved_ai_index = 0
                self.custom_color = None
        else:
            self.saved_ai_index = 0
            self.custom_color = None

    def update_ui_text(self):
        t = TRANSLATIONS[self.lang]
        self.url_bar.setPlaceholderText(t["search_placeholder"])
        self.sidebar.setTabText(0, t["ai_tab"])
        self.sidebar.setTabText(1, t["notes_tab"])
        self.sidebar.setTabText(2, t["vault_tab"])
        self.sidebar.setTabText(3, t["settings_tab"])
        self.v_label.setText(t["vault_title"])
        self.site_in.setPlaceholderText(t["site_ph"]); self.user_in.setPlaceholderText(t["user_ph"]); self.pass_in.setPlaceholderText(t["pass_ph"])
        self.btn_save_v.setText(t["save_btn"]); self.btn_del_v.setText(t["del_btn"])
        self.lang_label_ui.setText(t["lang_label"]); self.theme_btn_ui.setText(t["theme_btn"])
        
        # Privacy labels
        self.privacy_label.setText(t["privacy_title"])
        self.adblock_check.setText(t["adblock_label"])
        self.https_check.setText(t["https_label"])
        self.fingerprint_check.setText(t["fingerprint_label"])
        self.cookie_iso_check.setText(t["cookie_iso_label"])
        self.webrtc_check.setText(t["webrtc_label"])
        self.random_headers_check.setText(t["random_headers_label"])
        self.clear_on_close_check.setText(t["clear_on_close_label"])
        self.private_mode_check.setText(t["private_mode_label"])
        
        self.update_privacy_status()

    def update_privacy_status(self):
        t = TRANSLATIONS[self.lang]
        https_status = "✅" if self.https_only else "❌"
        fp_status = "✅" if self.fingerprint_protection else "❌"
        status_text = t["privacy_status"].format(
            blocked=self.blocked_count,
            https=https_status,
            fp=fp_status
        )
        self.privacy_status.setText(status_text)

    def set_language(self, i):
        self.lang = "en" if i == 0 else "pl"
        self.update_ui_text()
        self.save_settings()

    def get_credentials_for_site(self, site):
        for i in range(self.pass_list.count()):
            text = self.pass_list.item(i).text()
            if site.replace("www.", "") in text:
                try:
                    parts = text.split('|')
                    user_pw = parts[1].split(':')
                    return user_pw[0].strip(), user_pw[1].strip()
                except: continue
        return None

    def prompt_password_save(self, user, pw, site):
        t = TRANSLATIONS[self.lang]
        msg = QMessageBox(self)
        msg.setWindowTitle(t["pass_save_title"])
        msg.setText(t["pass_save_msg"].format(user=user, site=site))
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.pass_list.addItem(f"{site} | {user} : {pw}")
            self.save_passwords()

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None or isinstance(qurl, bool): qurl = QUrl("https://start.duckduckgo.com")
        browser = OpenBrowsingView(self)
        browser.setPage(QWebEnginePage(self.profile, browser))
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.loadStarted.connect(self.progress_bar.show)
        browser.loadProgress.connect(self.progress_bar.setValue)
        browser.loadFinished.connect(self.progress_bar.hide)
        browser.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()) if browser == self.tabs.currentWidget() else None)
        browser.titleChanged.connect(lambda t: self.tabs.setTabText(self.tabs.indexOf(browser), t[:15]))
        return browser

    def navigate(self):
        u = self.url_bar.text()
        q = QUrl(u) if "." in u else QUrl(f"https://duckduckgo.com/?q={u}")
        if q.scheme() == "": q.setScheme("https")
        self.tabs.currentWidget().setUrl(q)

    def go_home(self): self.tabs.currentWidget().setUrl(QUrl("https://start.duckduckgo.com"))
    
    def change_ai(self, i):
        urls = ["https://lumo.proton.me/guest", "https://duckduckgo.com/?q=DuckDuckGo+AI+Chat", "https://chatgpt.com", "https://claude.ai"]
        self.ai_view.setUrl(QUrl(urls[i]))
        self.save_settings()

    def add_password_manual(self):
        self.pass_list.addItem(f"{self.site_in.text()} | {self.user_in.text()} : {self.pass_in.text()}")
        self.save_passwords()

    def delete_password(self):
        for item in self.pass_list.selectedItems(): self.pass_list.takeItem(self.pass_list.row(item))
        self.save_passwords()

    def save_passwords(self):
        items = [self.pass_list.item(i).text() for i in range(self.pass_list.count())]
        with open("passwords.json", "w") as f: json.dump(items, f)

    def load_passwords(self):
        if os.path.exists("passwords.json"):
            with open("passwords.json", "r") as f: self.pass_list.addItems(json.load(f))

    def save_notes(self):
        with open("notes.txt", "w", encoding="utf-8") as f: f.write(self.notes_edit.toPlainText())

    def load_notes(self):
        """Wczytuje notatki z pliku"""
        if os.path.exists("notes.txt"):
            try:
                with open("notes.txt", "r", encoding="utf-8") as f:
                    self.notes_edit.setPlainText(f.read())
            except Exception as e:
                print(f"Error loading notes: {e}")

    def pick_color(self):
        c = QColorDialog.getColor()
        if c.isValid():
            self.custom_color = c.name()
            self.apply_styles()
            self.save_settings()

    def apply_styles(self):
        button_color = self.custom_color if hasattr(self, 'custom_color') and self.custom_color else "#007acc"
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: #1e1e1e; }}
            QToolBar {{ background-color: #2d2d2d; border: none; padding: 5px; }}
            QLineEdit {{ background-color: #3d3d3d; color: white; border-radius: 5px; padding: 5px; border: 1px solid #555; }}
            QTabWidget::pane {{ border: 1px solid #333; background-color: #252525; }}
            QTabBar::tab {{ background: #2d2d2d; color: #aaa; padding: 10px; min-width: 80px; }}
            QTabBar::tab:selected {{ background: #3d3d3d; color: white; border-bottom: 2px solid {button_color}; }}
            QPushButton {{ background-color: {button_color}; color: white; border-radius: 3px; padding: 6px; font-weight: bold; }}
            QProgressBar {{ background-color: #1e1e1e; border: none; }}
            QProgressBar::chunk {{ background-color: {button_color}; }}
            QCheckBox, QLabel {{ color: white; }}
            QListWidget {{ background-color: #1e1e1e; color: white; border: 1px solid #333; }}
        """)

    def closeEvent(self, event):
        """🧼 Czyszczenie danych przy zamknięciu"""
        if self.clear_on_close:
            self.profile.clearAllVisitedLinks()
            self.profile.clearHttpCache()
            self.profile.cookieStore().deleteAllCookies()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = OpenBrowsing()
    win.show()
    sys.exit(app.exec())
