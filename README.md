# 🚀 LearnSync: Unleashing Collaborative Wisdom

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Welcome to LearnSync! 🌟

LearnSync is more than just a platform; it's a dynamic community designed to transform learning into a collaborative and enjoyable journey. Explore the power of collective wisdom!

## 🌈 Key Features

- **User Account Creation:**
  - Craft your personalized learning haven with just a few clicks! 🚀

- **Room Creation:**
  - Kickstart your learning space! Title it, define the topic, and let the collaborative magic happen! 🌐

- **Room Discovery:**
  - Discover rooms matching your interests through our personalized feed and intelligent search. It's like having a learning genie! 🔍✨

- **Collaborative Environment:**
  - Real-time file sharing, chat, and interactive activities in every room. Because learning is a team sport! 📚💬

## 🚀 Get Started

### 1. Clone the Repository
   ```bash
   git clone https://github.com/VitthalGund/LearnSync.git
   ```

### 2. Navigate to the Project
   ```bash
   cd LearnSync
   ```

### 3. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```

### 4. Apply Database Migrations
   ```bash
   python manage.py migrate
   ```

### 5. Run the Application
   ```bash
   python manage.py runserver
   ```

   Hooray! LearnSync is now live at [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Get ready for a collaborative learning adventure!
Certainly! Here's an updated README section for Dockerizing your Django application:

# Dockerizing LearnSync 🐳

LearnSync is now Dockerized, making deployment and scalability a breeze! Follow these simple steps to run LearnSync using Docker:

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.

## Getting Started

1. **Build the Docker Image:**

   Open a terminal in the root directory of your LearnSync project and run:

   ```bash
   docker build -t learnsync .
   ```

   This command builds a Docker image named `learnsync` based on the provided Dockerfile.

2. **Run the Docker Container:**

   Once the image is built, start the Docker container with:

   ```bash
   docker run -p 8000:8000 -d learnsync
   ```

   This command runs the `learnsync` container in detached mode, mapping port 8000 on your machine to port 8000 in the container.

3. **Access LearnSync:**

   Open your browser and go to [http://localhost:8000](http://localhost:8000). Voilà! LearnSync is up and running!

## Dockerfile Explanation

The Dockerfile included in this project automates the setup process. Here's a brief explanation:

```Dockerfile
# syntax=docker/dockerfile:1
FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EXPOSE 8000
```
Now, deploying LearnSync is as simple as running a couple of Docker commands! If you have any questions or run into issues, feel free to reach out. Happy Dockerizing! 🚀

## 🌐 Tech Stack

- **Python**
- **Django**
- **HTML**
- **CSS**
- **SQL Database**

## 🌐 Contributing

Ready to contribute your brilliance? Check out our [contribution guidelines](CONTRIBUTING.md) and become a part of the LearnSync community! 🤝🚀

## 🚀 Future Improvements

- Streamlining the user onboarding process.
- Exciting community-building features and engaging events for an enhanced learning experience. 🎉🎓

## 🔐 Security and Privacy

Your data is our top priority! LearnSync securely stores user data in an SQL database, ensuring the utmost protection. 🛡️💼

## 📝 License

LearnSync is licensed under the [Apache 2.0 License](LICENSE). Feel free to explore, customize, and share the wisdom! 🌐📚

## ⚠️ Project Status

LearnSync is a showcase project, demonstrating skills and innovation. It's not just a project; it's a commitment to excellence! 🌟

## 🙏 Acknowledgments

Special thanks for considering this project, showcasing real-world problem-solving and technical expertise. Let's make learning together unforgettable! 🚀🎓

### App Preview :
<div align="center">
<table width="100%"> 
<tr>
<td width="50%">      
&nbsp; 
<br>
<p align="center">
  Feed Home
</p>
  <img src="https://github.com/VitthalGund/StudyBuddy/assets/97181033/fa1f1aac-9f62-4ac7-874b-178bef3c539d">

</td> 
<td width="50%">
<br>
<p align="center">
  User Preview
</p>
<img src="https://github.com/VitthalGund/StudyBuddy/assets/97181033/dfbc6149-58e0-4c7d-b3aa-c7a0fe77ef34">


</td>
</table>

<td width="50%">
<br>
<p align="center">
  Room Conversation Preview
</p>
<img src="https://github.com/VitthalGund/StudyBuddy/assets/97181033/caf738e2-bf25-4c30-ab0b-571297ccff4b">

</td>
</table>


