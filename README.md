## 🌐 WebChat API

The WebChat API is a real-time chat application backend built using Django and Django Rest Framework. It allows users to send messages instantly to a group, supporting features such as text-based communication, user authentication, and real-time updates. The API provides endpoints for administrators to create topics for rooms, manage rooms (create, read, update, delete), and for authenticated users to join rooms, send and read messages, update their profiles, and more.

### 🔧 Technologies Used:
- Django and Django Rest Framework for schema design and APIs.
- MySQL for database storage.
- Gunicorn for serving the Django application.
- Python-dotenv for managing environment variables.
- Other dependencies listed in the `requirements.txt` file.

### 🚀 Features:
- User authentication and authorization.
- Real-time messaging in group chat rooms.
- CRUD operations for rooms and messages.
- Custom UI for better user experience.
- API documentation provided in OpenAPI Spec v3 format.
- Deployment-ready configuration.

### 📁 Repository Structure (Only a brief overview):
- `README.md`: Contains project information, setup guide, and usage instructions.
- `requirements.txt`: Lists all Python dependencies required to run the project.
- `.env`: Example file for environment variables. Rename to `.env` and fill in the actual values.
- `base/api`: Main Django project directory.
  - `urls.py`: URL configuration for the project.
  - `views.py`: Contains view functions for handling API requests.
  - `models.py`: Defines the database models for rooms, messages, users, etc.
  - `serializers.py`: Serializers for converting model instances to JSON data.

## 🛠️ Setup Guide

Follow these steps to set up the project locally:

### 1. Clone the Repository

Clone the repository to your local machine using Git:

```bash
git clone https://github.com/VitthalGund/webchat-api.git
```

### 2. Navigate to the Project Directory

Move into the project directory that you just cloned:

```bash
cd webchat-api
```

### 3. Install Dependencies

Install the required Python dependencies listed in the `requirements.txt` file. It's recommended to use a virtual environment to manage dependencies:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory of the project. This file will contain sensitive information and configuration variables. Add the following environment variables to the `.env` file:

```plaintext
SECRET_KEY=<your_secret_key>
DATABASE_URL=mysql://<username>:<password>@<host>/<database_name>
ENGINE=<your_database_engine>
NAME=<your_database_name>
USER=<your_database_username>
PASSWORD=<your_database_password>
HOST=<your_database_host>
PORT=<your_database_port>
```

Replace `<your_secret_key>` with a secure secret key for Django's cryptographic signing. Update the `DATABASE_URL` with your MySQL database connection details. Fill in the details for `ENGINE`, `NAME`, `USER`, `PASSWORD`, `HOST`, and `PORT` according to your MySQL database configuration.

### 5. Run Migrations

Apply database migrations to set up the database schema:

```bash
python manage.py migrate
```

### 6. Start the Development Server

Start the Django development server to run the project locally:

```bash
python manage.py runserver
```

By default, the server will run on `http://127.0.0.1:8000/`.

### 7. Explore the API

You can now explore and interact with the WebChat API. Use the provided API routes to create, update, and delete chat rooms, send messages, manage user authentication, and more.



## 🛣️ API Routes

### Public Routes

#### User Authentication

- `POST /api/login`: User login.
  - **Request Format**:
    ```json
    {
      "email": "user@example.com",
      "password": "password123"
    }
    ```
  - **Headers**:
    ```
    Content-Type: application/json
    ```

- `POST /api/register`: User registration.
  - **Request Format**:
    ```json
    {
      "name":"name",
      "username": "username",
      "email": "user@example.com",
      "password1": "password123"
      "password2": "password123"
    }
    ```
  - **Headers**:
    ```
    Content-Type: application/json
    ```

#### General Information

- `GET /api/count`: Get the count of chat rooms.
  - **Headers**:
    ```
    Content-Type: application/json
    ```

- `GET /api/topics`: Get list of topics.
  - **Headers**:
    ```
    Content-Type: application/json
    ```

- `GET /api/activity`: Get activity details.
  - **Headers**:
    ```
    Content-Type: application/json
    ```

### Project Routes (Authorization Required)

#### Chat Rooms

- `GET /api/rooms`: Get all chat rooms.
  - **Headers**:
    ```
    Content-Type: application/json
    Authorization: Bearer <access_token>
    ```

- `GET /api/room/<int:pk>`: Get details of a specific chat room.
  - **Headers**:
    ```
    Content-Type: application/json
    Authorization: Bearer <access_token>
    ```

- `POST /api/logout`: User logout.
  - **Headers**:
    ```
    Content-Type: application/json
    Authorization: Bearer <access_token>
    ```

- `GET /api/send/<str:pk>`: Send a message to a chat room.
  - **Headers**:
    ```
    Content-Type: application/json
    Authorization: Bearer <access_token>
    ```

#### User Management

- `GET /api/profile/<str:pk>`: Get user profile details.
  - **Headers**:
    ```
    Content-Type: application/json
    Authorization: Bearer <access_token>
    ```

- `POST /api/create-room`: Create a new chat room.
  - **Request Format**:
    ```json
    {
      "host": "host_id",
      "topic": "topic_name",
      "name": "room_name",
      "description": "room_description"
    }
    ```
  - **Headers**:
    ```
    Content-Type: application/json
    Authorization: Bearer <access_token>
    ```

- `PUT /api/update-room/<str:pk>`: Update an existing chat room.
  - **Request Format**:
    ```json
    {
      "name": "updated_room_name",
      "topic": "updated_topic_name",
      "description": "updated_room_description"
    }
    ```
  - **Headers**:
    ```
    Content-Type: application/json
    Authorization: Bearer <access_token>
    ```

- `DELETE /api/delete-room/<str:pk>`: Delete a chat room.
  - **Headers**:
    ```
    Content-Type: application/json
    Authorization: Bearer <access_token>
    ```

- `DELETE /api/delete-message/<str:pk>`: Delete a message.
  - **Headers**:
    ```
    Content-Type: application/json
    Authorization: Bearer <access_token>
    ```

- `POST /api/update-user`: Update user details.
  - **Request Format**:
    ```json
    {
      "email": "new_email@example.com",
      "username": "new_username"
    }
    ```
  - **Headers**:
    ```
    Content-Type: application/json
    Authorization: Bearer <access_token>
    ```

## 📋 Request Formats

- **GET /api/rooms**: No request data required.
- **GET /api/count**: No request data required.
- **GET /api/topics**: No request data required.
- **GET /api/activity**: No request data required.


### 📧 Contact:
For any inquiries or feedback, feel free to contact the me.


