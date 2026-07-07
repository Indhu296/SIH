# 🌿 Digital Farm Management Portal

**Monitoring Maximum Residue Limits (MRL) and Antimicrobial Usage (AMU) in Livestock**

> Smart India Hackathon 2024 Project

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
cd farm_portal
pip install -r requirements.txt
```

### 2. Run the application
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## 🔐 Demo Login Credentials

| Role   | Username | Password   |
|--------|----------|------------|
| Admin  | admin    | admin123   |
| Farmer | farmer1  | farmer123  |
| Farmer | farmer2  | farmer123  |

---

## 📁 Project Structure

```
farm_portal/
├── app.py                  ← Flask application (routes + models)
├── requirements.txt        ← Python dependencies
├── README.md
├── static/
│   ├── css/
│   │   └── style.css       ← Green agriculture theme
│   └── js/
│       └── main.js         ← Animations & UI interactions
└── templates/
    ├── base.html           ← Layout (navbar + footer)
    ├── home.html           ← Landing page
    ├── about.html          ← About page
    ├── login.html          ← Authentication
    ├── dashboard.html      ← Admin/Farmer dashboard with charts
    ├── livestock.html      ← Livestock list + search/filter
    ├── livestock_form.html ← Add/Edit livestock
    ├── mrl.html            ← MRL monitoring with progress bars
    ├── mrl_form.html       ← Add/Edit MRL record
    ├── amu.html            ← AMU tracking table
    ├── amu_form.html       ← Add/Edit AMU record
    ├── reports.html        ← Charts + analytics
    └── contact.html        ← Contact form + FAQ
```

---

## ✨ Features

- 🐄 **Livestock Management** — Add, Edit, Delete with CRUD
- 🔬 **MRL Monitoring** — Auto status: Safe / Warning / Exceeded
- 💊 **AMU Tracking** — Drug prescriptions + withdrawal period tracking
- 📊 **Dashboard Charts** — Chart.js doughnut + bar charts
- 🚨 **Real-time Alerts** — Flash banners for exceeded MRL
- 🔍 **Search & Filter** — All tables support search and filter
- 🔐 **Role-based Login** — Admin and Farmer roles
- 📱 **Responsive Design** — Mobile + desktop
- 🎨 **Green Agriculture Theme** — Bootstrap 5 extended

---

## 🛠 Tech Stack

| Layer     | Technology          |
|-----------|---------------------|
| Backend   | Python Flask 3.0    |
| Database  | SQLite + SQLAlchemy |
| Frontend  | Bootstrap 5 + CSS3  |
| Charts    | Chart.js 4.4        |
| Icons     | Bootstrap Icons     |
