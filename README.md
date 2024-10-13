# Pair Connect 💻  

## Table of Contents

- [Project Overview 🤝](#project-overview-)
- [Installation 🛠️](#installation-)
    - [Requirements](#requirements-)
- [Project Structure 💻](#project-structure-)
- [Technologies 🚀](#technologies-)
- [Usage 🔥](#usage-)
- [Contribution ✨](#contribution-)
- [Authors 👩‍💻](#authors-)
- [Demo 👓](#demo-)

## Project Overview 🤝

**Pair Connect** is a platform where developers can connect with each other for pair programming sessions based on their skills, programming languages, and project preferences. Users can browse available sessions, join them, and collaborate on real-time coding projects, enhancing both learning and productivity.

The backend is built using Django and Django REST Framework, and the frontend integrates the API to display session suggestions based on the user's skills and preferences.

### Key Features
- User registration and authentication with Djoser and JWT.
- Profile management, including skills, programming languages, and experience level.
- Session recommendations based on user profile (frontend, backend, or full-stack).
- Creation and management of pair programming sessions.
- Integration of Cloudinary for profile image storage.
- Email notifications system for being update about the sessions.

## Installation 🛠️

### Requirements

- [Python 3.x](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/)
- [Git](https://git-scm.com/)

1. Clone the backend repository:

    ```bash
    git clone https://github.com/your-username/pair_connect_back
    ```

2. Create and activate a virtual environment:

    ```bash
    cd pair_connect_back
    python -m venv env
    source env/bin/activate  # On Windows use: env\Scripts\activate
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your PostgreSQL database and update the credentials in the `settings.py` file.

5. Run the migrations and start the server:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    ```

## Project Structure 💻

The project follows a standard structure for Django applications with modular organization to handle user profiles, sessions, and other features.

### Backend Folder Structure

```plaintext
/
├── pair_connect
│   ├── projects/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── ...
│   ├── skills/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── ...
│   ├── users/
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── ...
│   ├── manage.py
│   ├── requirements.txt
│   └── README.md
```
### Frontend Folder Structure
```plaintext
/
├── public/
│   ├── index.html
│   └── ...
├── src/
│   ├── assets/
│   │   └── images/
│   ├── components/
│   │   ├── Navbar/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Navbar.styles.js
│   │   │   └── index.js
│   │   ├── Button/
│   │   │   ├── Button.jsx
│   │   │   └── index.js
│   │   ├── ProfileCard/
│   │   │   ├── ProfileCard.jsx
│   │   │   └── index.js
│   │   └── SessionCard/
│   │       ├── SessionCard.jsx
│   │       └── index.js
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Profile.jsx
│   │   ├── Sessions.jsx
│   │   ├── CreateSession.jsx
│   │   └── ...
│   ├── services/
│   │   ├── api.js
│   │   └── sessionService.js
│   ├── context/
│   │   └── AuthContext.js
│   ├── App.js
│   ├── index.js
│   └── styles/
│       └── globalStyles.js

```

## Technologies 🚀

### Technologies Backend


The backend of **Pair Connect** is built using the following key technologies:

- **[Python 3.x](https://www.python.org/)**: A high-level programming language that serves as the core of the backend.
- **[Django 5.1.1](https://www.djangoproject.com/)**: A high-level Python web framework that promotes rapid development and clean, pragmatic design.
- **[Django REST Framework 3.15.2](https://www.django-rest-framework.org/)**: A powerful and flexible toolkit for building Web APIs.
- **[PostgreSQL 15](https://www.postgresql.org/)**: A robust, open-source relational database management system used to store data.
- **[Djoser 2.2.3](https://djoser.readthedocs.io/en/latest/)**: Provides a set of Django Rest Framework views to handle user authentication.
- **[Cloudinary 1.41.0](https://cloudinary.com/)**: A cloud-based service for managing images and videos.
- **[SimpleJWT 5.3.1](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)**: A JSON Web Token authentication backend for Django REST Framework.
- **[Psycopg2 2.9.9](https://www.psycopg.org/)**: The most popular PostgreSQL adapter for Python, essential for database connectivity.
- **[Pytest 8.3.3](https://pytest.org/)**: A robust testing framework for Python.

These key technologies provide a solid foundation for the backend, ensuring secure authentication, efficient database management, and a robust API for **Pair Connect**.


### Technologies Frontend

The frontend of **Pair Connect** is built using the following key technologies:

- **[React 18.3.1](https://reactjs.org/)**: A JavaScript library for building user interfaces.
- **[React Router DOM 6.26.2](https://reactrouter.com/en/main)**: A library for handling routing in React applications.
- **[Tailwind CSS 3.4.12](https://tailwindcss.com/)**: A utility-first CSS framework for styling.
- **[Axios 1.7.7](https://axios-http.com/)**: A promise-based HTTP client for making API requests.
- **[React Hook Form 7.53.0](https://react-hook-form.com/)**: A performant, flexible form library for handling forms in React.
- **[Radix UI](https://www.radix-ui.com/)**: A set of accessible, unstyled components for building high-quality web interfaces.
- **[Vitest 2.1.1](https://vitest.dev/)**: A blazing-fast unit testing framework for Vite and other frontend projects.
- **[Vite 5.4.8](https://vitejs.dev/)**: A next-generation frontend build tool.

These core technologies provide the foundation for building a responsive, modular, and fast frontend for **Pair Connect**, ensuring efficient development and user experience.


## Usage 🔥
To start the backend server, make sure the virtual environment is activated, and run the following command:
```bash
python manage.py runserver
```

## Contribution ✨
Fork the repository.

Create a new branch for your feature:

```bash
git checkout -b feature/new-feature
```
Commit your changes:

```bash
git commit -m 'Add new feature'
```
Push your branch:

```bash
git push origin feature/new-feature
```
Open a pull request.

## Authors 👩‍💻
This project was created by:    

- Helena López (https://github.com/helopgom)
- Esther P. Sarasua (https://github.com/Fire-Fairy84)
- Valentina Toni (https://github.com/ItalianCookieMonster)  
- Lynn Poh (https://github.com/Dpoetess) 
- Paola Franco (https://github.com/0795PAO)
- Jessica Arroyo (https://github.com/jess-ar)  


## Demo 👓
Here are some screenshots of the Pair Connect application:

Home

User Profile Page

Session Suggestions

My projects