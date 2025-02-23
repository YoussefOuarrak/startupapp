# HubValue - Startup Evaluation Platform

## 🛠️ Tech Stack
- **Backend:** Django (Python 3.12) + SQLite
- **Frontend:** Bootstrap or Tailwind CSS
- **Libraries:** OpenPyxl (Excel file processing)

##  Installation & Setup
### 1️⃣ Clone the Repository
```sh
 git clone https://github.com/youssefouar/hubvalue.git
 cd hubvalue
```

### 2️⃣ Create a Virtual Environment (Conda)
```sh
conda create -n hubvalue python=3.12
conda activate hubvalue
```

### 3️⃣ Install Dependencies
```sh
pip install django openpyxl  
pip install pyparsing
pip install django-jsonfield
```

### 4️⃣ Setup Django Project
```sh
django-admin startproject startupapp
cd startupapp
```

### 5️⃣ Run Migrations & Start Server
```sh
python manage.py migrate
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` to see the app running.

##  Key Design Decisions

### JSONFields with SQLite
- **Scalability** – JSONFields allow dynamic fields without requiring database migrations.
- **Efficient Storage** – Avoids unnecessary NULL columns for startups with varying numbers of founders, social media links, or videos.
- **Future-Proof** – Supports additional fields without modifying the database schema.

