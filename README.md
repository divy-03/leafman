
# Leafman - A Mini Leave Management System 🌿

![Leafman Admin CLI Banner](./logo.png)

Leafman is a full-stack, API-driven leave management system designed for small to medium-sized startups. It features a robust **FastAPI** backend, a **PostgreSQL** database, and two distinct, Metasploit-style command-line interfaces for different user roles: one for employees and one for administrators.

This project was built to demonstrate not just technical skills in backend development and deployment, but also a strong focus on product thinking, user experience, and handling real-world edge cases.

---

## ✨ Features

The system is split into two primary interfaces, providing a tailored experience for each user role.

#### For Employees (`leafman.py`)
A clean and simple interface for everyday tasks.
- 👤 **Login/Logout:** Secure session management.
- 📋 **View Balances:** Check current leave balances for all categories (e.g., Casual, Earned).
- 📜 **View History:** See a beautifully formatted table of past and pending leave requests.
- ✈️ **Apply for Leave:** An interactive prompt that shows available leave types before you apply.
- ℹ️ **`whoami`:** Display your own user profile.

#### For Admins (`leafman-admin.py`)
A powerful console for system management and oversight.
- ✅ **Includes all Employee features.**
- ➕ **User Management:** Create new employee or admin users (`adduser`).
- 👀 **View All Requests:** Show all requests in the system (`show all_requests`) or filter for pending ones (`show pending`).
- 👍 **Approve/Reject:** Approve or reject pending leave requests with optional notes.
- 🍃 **Manage Leave Types:** Create new leave categories for the whole company (`add_leavetype`).
- 🏢 **Manage Departments:** Create new company departments (`add_dept`).

---

## 🛠️ Tech Stack & Architecture

- **Backend:** **FastAPI** (Python 3.11)
- **Database:** **PostgreSQL**
- **ORM:** **SQLAlchemy** with **Alembic** for migrations
- **CLI:** Python's built-in `cmd` module
- **Deployment:** **Docker** & **Coolify** on a GCP instance
- **CI/CD:** Managed via GitHub webhooks to Coolify

### High-Level Architecture
The system uses a standard stateless API architecture, containerized for portability and easy deployment.


## 🚀 Getting Started

You can run this project locally for development or deploy it to a server with Docker.

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git
- A running PostgreSQL instance

### 1. Backend Setup (Local Development)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/nightmare-tech/leafman
    cd leafman
    ```

2.  **Create a `.env` file:**
    Create a file named `.env` in the root directory and add your local database URL.
    ```
    # .env
    DATABASE_URL="postgresql://user:password@localhost:5432/leave_db"
    JWT_SECRET_KEY="a_very_strong_and_secret_key_for_local_development"
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run Database Migrations:**
    This creates all the necessary tables in your database. You only need to run this once.
    ```bash
    alembic upgrade head
    ```

5.  **Seed the Database (First Time Only):**
    This script will interactively prompt you to create the first Admin user and default Leave Types/Departments.
    ```bash
    python seed.py
    ```

6.  **Run the FastAPI Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000/docs`.

### 2. Deployment (Coolify)
The project is ready for one-click deployment on Coolify.
1.  Push the repository to GitHub.
2.  In Coolify, create a new **PostgreSQL** database service.
3.  Create a new **Application** resource, linking it to your GitHub repository and selecting the **Dockerfile** build pack.
4.  In the application's **Storage** tab, connect it to the PostgreSQL database. Rename the auto-generated environment variable key to `DATABASE_URL`.
5.  Add your `JWT_SECRET_KEY` as an environment variable.
6.  Set the **Port** in the **Configuration -> Network** section to `80`.
7.  Deploy! Once running, connect to the container's **Terminal** in the Coolify UI to run `alembic upgrade head` and `python seed.py`.

### 3. CLI Usage

Both CLIs are designed to be run from your local machine, connecting to either your local server or the deployed production server.

1.  **Configure the API URL:**
    In the project root, edit the `.env` file and set the `LEAFMAN_API_URL`.
    ```
    # .env - for production
    LEAFMAN_API_URL="http://leafman.your-coolify-url.sslip.io"
    ```

2.  **Run the desired CLI:**
    ```bash
    # For the admin console
    python leafman-admin.py

    # For the employee interface
    python leafman.py
    ```

---

## 📸 Screenshots

#### Admin Console: Viewing All Requests
![Admin CLI](./leafman-admin-cli.png) 

#### Employee CLI: Applying for Leave
![Employee CLI](./leafman-cli.png) 

---

## 🔮 Future Improvements
-   **Advanced Leave Logic:** Implement yearly rollover scripts for EL and lapsing logic for CL.
-   **Notifications:** Integrate email or Slack notifications for leave approvals/rejections.
-   **Web Frontend:** Build a simple React or Vue.js frontend to complement the CLIs.
-   **Reporting:** Add endpoints for HR to generate reports on leave patterns.
