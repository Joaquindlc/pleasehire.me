# pleasehire.me 🚀
> **An Intelligent Job Extraction Bot & Toolkit for Developers**

`pleasehire.me` is a desktop automation tool built in Python that streamlines tech job hunting. Utilizing an asynchronous, multi-threaded architecture with a **Tkinter GUI** and **Playwright**, the application orchestrates secure session handshakes and scans technical job listings (such as LinkedIn and CompuTrabajo) to generate clean, technical stack summaries in real-time.

---

## 🛠️ Features
- **Cross-Platform Portability:** Out-of-the-box support for Windows, Linux, and macOS (fully tested and optimized for Python 3.13).
- **Secure Visual Handshake (New User Mode):** Implements a safe, human-driven 120-second authentication gate. No plain-text passwords or credentials are ever stored or transmitted.
- **Robust DOM Orchestration:** Uses dynamic, hybrid element selectors (`data-occludable-job-id`, `.scaffold-layout__list-item`) to remain stable against platform layout variations.
- **Clean Console Analytics:** Outputs a standardized, formatted text block aligning job titles and company fields for immediate visibility.

---

## 🚀 Quick Start for Evaluators

Follow these simple steps to install and test the platform on your local machine:

### 1. Clone the Repository
Clone the production branch of the project and navigate to the directory:

    git clone -b prod <YOUR_GITHUB_REPOSITORY_URL>
    cd pleasehire-me

### 2. Set Up a Virtual Environment (Recommended)
Isolate dependencies to prevent script execution policies or permission flags from interrupting the installation:

* **On Windows (PowerShell / Command Prompt):**

    python -m venv venv
    .\venv\Scripts\activate.bat

* **On macOS / Linux:**

    python3 -m venv venv
    source venv/bin/activate

### 3. Install Requirements
Install all locked dependencies, featuring Python 3.13 stability patches (including greenlet compatibility fixes):

    pip install -r requirements.txt

### 4. Provision Browser Binaries
Playwright requires sandboxed instances of browser engines. Provision the isolated Chromium binary with:

    python -m playwright install chromium

### 5. Run the Core Orchestrator
Launch the Tkinter GUI control frame:

    python main.py

---

## 💡 How to Test the Flow

1. **Input Your Target Stack:** In the Tkinter GUI window, input your keywords separated by spaces (e.g., `Salesforce React Node Developer`).
2. **Execute the Engine:** Click on **"Launch Engine 🚀"**.
3. **Complete the Authentication Gate:** A visible browser window will open. Type `https://linkedin.com/` in the address bar, sign in manually with your account, and wait in your main feed until the 120-second countdown safely exports your persistent session data into a local `auth.json` file.
4. **Analyze the Results:** Watch the background automation loop through your technical keywords and output the formatted data summary directly to your terminal.

---

## 🔒 Security & Best Practices

- **Session Protection:** All tokens and cookies generated during runtime are contained strictly within your local `auth.json` environment. This file is actively restricted via `.gitignore` to prevent deployment leaks.
- **Anti-Scraping Resilience:** Features calculated page stabilization intervals (`time.sleep`) to mimic organic navigation and respect remote platform rate limits.

---
*Developed as a Final Graduation Project for Stanford University's Code in Place 2026 course.*