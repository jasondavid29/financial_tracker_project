💼 **Financial Tracker**

**Financial Tracker** is a web application that allows users to efficiently track their income, expenses, and budgets. With a visually appealing dashboard and user-friendly interface, it offers features like transaction history, category-based filtering, export options, and graphical insights.

---

🔑 **Features**

- **User Authentication**: Users can register, log in, and log out securely.
- **Add Income & Expenses**: Users can add, edit, and delete their financial records.
- **View Summary**: Monthly and category-wise summaries using charts and tables.
- **Budget Limit Alerts**: Users can set monthly budgets and receive alerts when limits are reached.
- **Export Options**: Download reports as CSV or PDF for offline access.
- **Responsive Design**: The application is optimized for desktop and mobile devices.

---

🗂️ **Project Structure**

- `static/` - Contains static files like CSS, JavaScript, and images.
- `templates/` - Contains HTML templates for various pages.
- `finance/` - Contains Django app files including models, views, urls, and forms.

---

⚙️ **How to Run the Project**

**1. Clone the repository:**
git clone https://github.com/yourusername/financial-tracker.git
cd financial-tracker

**2. Create and activate a virtual environment:**
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

**3. Install the dependencies:**
pip install -r requirements.txt

**4. Run the migrations:**
python manage.py makemigrations
python manage.py migrate

**5. Create a superuser:**
python manage.py createsuperuser

**6. Run the development server:**
python manage.py runserver

**7. Access the application:**
Open a web browser and go to:
http://127.0.0.1:8000

---

📌 **Usage**
**Registration and Login**
1. Navigate to the registration page to create an account.

2. Login to access the dashboard with all financial features.

**Dashboard**
1. Use the Add Income/Expense forms to record transactions.

2. View summaries in the form of charts (pie/bar).

3. Filter transactions by category or date using dropdown filters.

4. Download your data using the Export CSV/PDF buttons.

---

🌐 **LIVE DEMO**

🔗 [Click here to try the live app] -> (https://financial-tracker-project.onrender.com/) 



