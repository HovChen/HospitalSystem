# **HospitalSystem**

A hospital management system developed as part of the HDU SE homework. Built with **Flask** and **MySQL**.

## **Features**

- 🛡️ **User Management**: Authentication and role-based authorization.
- 👩‍⚕️ **Patient Management**: Add, update, and view patient records.
- 🩺 **Doctor Management**: Manage doctor details.
- 📅 **Appointment Management**: Schedule and manage appointments.
- 📊 **Database Initialization**: Scripts for easy setup and seeding.

## **Prerequisites**

Ensure the following are installed on your system:

- ✅ Python 3.x
- ✅ MySQL
- ✅ pip (Python package manager)

## **Installation**

### **1. Clone the repository**

```bash
git clone https://github.com/HovChen/HospitalSystem.git
cd HospitalSystem
```

### **2. Install dependencies**

```bash
pip install -r requirements.txt
```

### **3. Configure MySQL**

1. Set up your MySQL server.

2. Create a database:

   ```sql
   CREATE DATABASE hospital;
   ```

3. Import the schema:

   ```bash
   mysql -u <your_username> -p hospital < database_schema.sql
   ```

4. Update `config.py` with your MySQL details:

   ```python
   MYSQL_HOST = 'your_host'
   MYSQL_USER = 'your_username'
   MYSQL_PASSWORD = 'your_password'
   MYSQL_DB = 'hospital'
   
   SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
   ```

   **Note**: The `SECRET_KEY` and email configurations (if used) should also be set in the `config.py` file. The values can be pulled from environment variables or specified directly.

### **4. Configure Email (Optional)**

If you plan to use email functionality (for example, sending notifications), ensure the following settings are updated in the `config.py`:

```python
MAIL_SERVER = 'your_mail_server'
MAIL_PORT = 25  # Change port if needed
MAIL_USE_TLS = True  # Set to True if using TLS
MAIL_USERNAME = 'your_email_username'
MAIL_PASSWORD = 'your_email_password'
```

### **5. Initialize the database**

Run the initialization script:

```bash
python init_db.py
```

## **Run the Project**

Start the Flask server:

```bash
python app.py
```

Visit the app in your browser: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## **Project Structure**

```plaintext
HospitalSystem/
├── models/         # Database models
├── routes/         # Application routes (endpoints)
├── static/         # Static files (CSS, JS, images)
├── templates/      # HTML templates
├── app.py          # Main app entry point
├── config.py       # Configuration file
├── init_db.py      # Database initialization script
├── requirements.txt# Dependencies
└── README.md       # Documentation
```

## **Usage**

1. Run the server: `python app.py`.
2. Open the browser: [http://127.0.0.1:5000/](http://127.0.0.1:5000/).
3. Start managing patients, doctors, and appointments!

## **Contributing**

Contributions are welcome! Follow these steps:

1. Fork the repo.
2. Create a branch: `git checkout -b feature-name`.
3. Commit changes: `git commit -m 'Add new feature'`.
4. Push to branch: `git push origin feature-name`.
5. Open a pull request.

## **License**

Licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### 🎉 Happy Coding!
