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
| ![Home](Software/InvestPic/Home.jpeg) | ![About](https://i.imgur.com/efgh456.png) |

### 🧩 Contact & Register
| | |
|--|--|
| ![Contact](https://i.imgur.com/ijkl789.png) | ![Register](https://i.imgur.com/mnop012.png) |

### 🧩 Login & Dashboard
| | |
|--|--|
| ![Login](https://i.imgur.com/qrst345.png) | ![Dashboard](https://i.imgur.com/uvwx678.png) |

---

.

