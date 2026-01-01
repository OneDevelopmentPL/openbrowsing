# OpenBrowsing 🛡️ Privacy-Focused Browser

OpenBrowsing is a **privacy-first web browser**, designed to protect users from tracking, fingerprinting, and unnecessary data collection, while providing a fast and modern browsing experience.

---

## Features

- **Ad & Tracker Blocking** – built-in filters block ads, trackers, and analytics scripts.  
- **HTTPS-Only Modw** – automatically converts HTTP sites to HTTPS.  
- **Anti-Fingerprinting (RFP)** – masks canvas, WebGL, audio, fonts, RAM, CPU cores, and timers.  
- **Cookie Isolation** – cookies are isolated per domain to prevent cross-site tracking.  
- **WebRTC Leak Protection** – prevents IP leaks via WebRTC.  
- **Random Headers & User-Agent Spoofing** – reduces fingerprinting risk.  
- **Private Browsing & Auto-Clear** – optional private mode and automatic clearing of history, cookies, and cache on exit.  
- **Local Password Manager** – stores passwords locally with optional autofill.  
- **Customizable UI** – dark mode, scaling, fullscreen, zoom adjustments.  
- **Download Manager** – list of downloads, notifications, quick access to folder.  
- **Bookmarks & History Management** – view, add, and remove bookmarks and history.  
- **Multiple Tabs & Shortcuts** – full support for multiple tabs and common keyboard shortcuts.

---

## Comparison with OneWeb

| Feature | OpenBrowsing | OneWeb |
|---------|--------------|--------|
| Ad & Tracker Blocking | ✅ Built-in filters | ⚠ Not included |
| HTTPS-Only | ✅ Automatic | ⚠ Not included |
| Anti-Fingerprinting | ✅ Canvas, WebGL, Audio, Fonts, Hardware | ⚠ Not included |
| Cookie Isolation | ✅ Per-domain cookies | ⚠ Default WebEngine behavior |
| WebRTC Leak Protection | ✅ IP leak blocked | ⚠ Not included |
| Private Mode & Auto-Clear | ✅ ✅ | ⚠ Limited |
| Local Password Manager | ✅ Local storage | ⚠ Not included |
| Customizable UI | ✅ Dark mode, zoom, fullscreen | ⚠ Basic styling |
| Download Manager | ✅ List, notifications | ✅ Yes |
| Bookmarks & History | ✅ Full management | ✅ Full management |
| Multiple Tabs & Shortcuts | ✅ ✅ | ✅ ✅ |
| Focus on Privacy | ✅ Strong emphasis | ⚠ Limited |

---

## Installation

**Requirements:** Python 3.11+, PyQt6, PyQt6-WebEngine  

```bash
git clone https://github.com/YourUsername/OpenBrowsing.git
cd OpenBrowsing
python -m pip install -r requirements.txt
python browser.py
```

## Notes:

- Compatible with Windows, Linux, and macOS.
- Runs on PyQt6's QWebEngine (Chromium-based).
- Optional: adjust settings in config.json for advanced privacy options.

## Usage

- Open the browser and navigate using the URL bar.
- Use Ctrl+T for a new tab, Ctrl+W to close, and Ctrl+Shift+Del to clear browsing data.
- Access bookmarks and history via the toolbar or shortcuts (Ctrl+B, Ctrl+H).
- Download files via the download manager and access the folder directly.
- Use private browsing mode to avoid saving history and cookies.

## License

### OpenBrowsing is licensed under **MIT License**. Free for personal and commercial use. Contributions are welcome.

## Contributing

1. Fork the repository.
2. Create a new branch:
```bash
git checkout -b feature-name.
```
3. Make your changes and commit: git commit -am 'Add feature'.
4. Push to the branch:
```bash
git push origin feature-name.
```
5. Create a pull request.

## We welcome bug reports, feature requests, and pull requests. Please follow the code style and test before submitting.

# OpenBrowsing 🛡️ Prywatna przeglądarka

OpenBrowsing to **przeglądarka skupiona na prywatności**, chroniąca przed śledzeniem, fingerprintingiem i niepotrzebnym zbieraniem danych, zapewniając szybkie i nowoczesne przeglądanie.

---

## Funkcje

- Blokowanie reklam i trackerów  
- Automatyczne HTTPS  
- Ochrona przed fingerprintingiem (Canvas, WebGL, Audio, sprzęt)  
- Izolacja ciasteczek per domena  
- Ochrona WebRTC (blokada wycieku IP)  
- Tryb prywatny i automatyczne czyszczenie danych  
- Lokalny menedżer haseł  
- Personalizacja UI: ciemny motyw, zoom, pełny ekran  
- Menedżer pobierania  
- Historia i zakładki  
- Wiele kart i skróty klawiszowe

---

## Porównanie z OneWeb

| Funkcja | OpenBrowsing | OneWeb |
|---------|--------------|--------|
| Blokowanie reklam | ✅ | ⚠ Nie |
| HTTPS-Only | ✅ | ⚠ Nie |
| Anti-Fingerprinting | ✅ | ⚠ Nie |
| Izolacja ciasteczek | ✅ | ⚠ Domyślne |
| WebRTC Leak | ✅ | ⚠ Nie |
| Tryb prywatny | ✅ | ⚠ Ograniczony |
| Menedżer haseł | ✅ | ⚠ Nie |
| UI | ✅ | ⚠ Prosty |
| Pobieranie | ✅ | ✅ |
| Zakładki i historia | ✅ | ✅ |
| Prywatność | ✅ | ⚠ Ograniczona |

---

## Instalacja

Wymagania: Python 3.11+, PyQt6, PyQt6-WebEngine  

```bash
git clone https://github.com/YourUsername/OpenBrowsing.git
cd OpenBrowsing
python -m pip install -r requirements.txt
python browser.py
