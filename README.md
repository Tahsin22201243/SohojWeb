# 💼 Sohoj Biniyog

### 🏦 A Crowdfunding and Investment Platform

**Sohoj Biniyog** is a web-based platform that connects **small business owners** with **potential investors**.  
It allows entrepreneurs to create funding campaigns while enabling investors to browse, analyze, and invest securely.

---

## 🧩 Project Overview

| Role | Description |
|------|--------------|
| **Business Owners** | Create and manage funding campaigns |
| **Investors** | Browse campaigns and invest |
| **Admin (optional)** | Approve and monitor campaigns |

---

## 🚀 Core Features

- Dual login system (**Investor / Business Owner**)
- Campaign creation & management
- Secure investment transactions
- Investment tracking & history
- Admin dashboard (optional)
- Selenium-based automated testing

---

## 🧠 Technology Stack

| Component | Technology |
|------------|-------------|
| **Frontend** | HTML • CSS • JavaScript |
| **Backend** | Django (Python) |
| **Database** | SQLite / PostgreSQL |
| **Testing** | Selenium + Python WebDriver |
| **Version Control** | GitHub |

---

---

## ⚙️ Technologies Used

| Category | Tools / Frameworks |
|-----------|--------------------|
| **Language** | Python / JavaScript |
| **Framework** | Django / Flask (if applicable) |
| **Frontend** | HTML, CSS, JS |
| **Database** | SQLite / PostgreSQL |
| **Version Control** | Git + GitHub |
| **Testing** | Selenium / PyTest |
| **Deployment** | Localhost / Render / Vercel / Heroku |

---

## 🚀 Getting Started

### 🔧 Prerequisites
Make sure you have the following installed:
- Python 3.x
- Git
- pip (Python package installer)
- Virtual environment (optional but recommended)

### ⚙️ Setup Instructions

```bash
# Clone this repository
git clone https://github.com/Tahsin22201243/UAP-3.2.git

# Navigate into the folder
cd UAP-3.2/Software

# Install dependencies
pip install -r requirements.txt

# Run the application (example)
python app.py

## 🧪 Selenium Testing Overview

- Automated testing for all major modules: login, campaign, and investment.
- Implemented with **Python + Selenium WebDriver**.
- Locator strategies used: `By.ID`, `By.NAME`, `By.XPATH`, `By.CSS_SELECTOR`.

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("http://127.0.0.1:8000/login/")
driver.find_element(By.NAME, "email").send_keys("test@demo.com")
driver.find_element(By.NAME, "password").send_keys("123456")
driver.find_element(By.ID, "loginBtn").click()

# 📸 Project Screenshots

### 🧩 Home & About
| | |
|--|--|
| ![Home](https://drive.google.com/drive/u/0/folders/1Sa8eomEN0FlsmqAIXfsCeJ0IU0l3Q25B) | ![About](https://drive.google.com/drive/u/0/folders/1Sa8eomEN0FlsmqAIXfsCeJ0IU0l3Q25B) |

### 🧩 Contact & Register
| | |
|--|--|
| ![Contact](https://drive.google.com/drive/u/0/folders/1Sa8eomEN0FlsmqAIXfsCeJ0IU0l3Q25B) | ![Register](https://drive.google.com/drive/u/0/folders/1Sa8eomEN0FlsmqAIXfsCeJ0IU0l3Q25B) |

### 🧩 Login & Dashboard
| | |
|--|--|
| ![Login](https://drive.google.com/drive/u/0/folders/1Sa8eomEN0FlsmqAIXfsCeJ0IU0l3Q25B) |

[![Watch  Investment Workflow ]([https://img.youtube.com/vi/YOUR_THUMBNAIL_CODE/0.jpg)](https://drive.google.com/file/d/1AbCdEfGHIJKLmnopQRsTuVWxyz12345/view?usp=sharing](https://drive.google.com/drive/u/0/folders/1Sa8eomEN0FlsmqAIXfsCeJ0IU0l3Q25B))

---

.

