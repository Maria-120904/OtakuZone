# Otakuzone

## Project Overview
OtakuZone is a mobile anime-streaming application inspired by the user experience of platforms like Netflix but designed specifically for anime fans and enthusiasts. The app allows users to create accounts, explore anime titles, browse categories, view anime information, and stream episodes directly from their device. It provides an organized, visually appealing, and user-friendly environment focused on simplicity and smooth navigation. An admin role is also included, enabling administrators to manage anime data and maintain the app’s content.

## Problem Statement  
Anime viewers often struggle with scattered sources, disorganized platforms, or websites overloaded with ads and unnecessary features. OtakuZone addresses this problem by offering a dedicated, ad-free, and streamlined anime-viewing experience that focuses on essential user needs: account creation, easy browsing, clear categorization, and direct streaming. By providing an admin-managed catalog and removing unexecuted features such as subscriptions, watch history, and payment methods, the system ensures a manageable and efficient version 1.0 suitable for academic and early deployment purposes.

## Feature List & Scope 
| Feature / Module                                | In Scope (✔) / Out of Scope (✖) |
|-------------------------------------------------|----------------------------------|
| User Account & Profile Management               | ✔                                |
| Anime Browsing & Categories (Explore + Homepage)| ✔                                |
| Anime Streaming & Episode Viewer                | ✔                                |
| Favorites & Downloads Management                | ✔                                |
| Subscription, Payment & Watch History Modules   | ✖                                |

## Architecture Diagram 
```
[ Flet UI layer ]  ↔  [ Services / Controllers ]  ↔  [ SQLite Database ]
                     ↕
        [ Emerging Tech: Interactive Data Visualization ]
``` 

**Folder Structure:**
- `views` – UI screens (login, user, admin, analytics, etc.)
- `services` – business logic, analytics, email, session, security
- `database` – setup and migration scripts
- `config` – configuration files (email, environment)
- `assets` – images, videos, icons
- `main.py` – application entry point

## Data Model 
Example JSON schema for a User Table:  

```json
{
  "id": 1,
  "name": "Admin",
  "username": "admin",
  "email": "admin@otakuzone.com",
  "password": "<hashed>",
  "google_id": "google-uid",
  "birthdate": "YYYY-MM-DD",
  "age": 21,
  "address": "City",
  "gender": "Male",
  "bio": "Anime lover",
  "role": "admin",
  "two_factor_enabled": 1,
  "email_verified": 1,
  "profile_image": "assets/profile/admin.png"
}
```

Example JSON schema for a Anime Table:  

```json
{
  "id": 1,
  "title": "Naruto Shippuden",
  "genre": "Action, Adventure",
  "category": "Completed",
  "description": "Naruto's journey to become Hokage.",
  "image_path": "assets/anime/naruto.png"
}
```

Example JSON schema for a Episode Table:  

```json
{
  "id": 1,
  "anime_id": 1,
  "episode_number": 1,
  "title": "Enter: Naruto Uzumaki!",
  "video_path": "assets/videos/naruto/ep1.mp4",
  "duration": "24:00",
  "upload_date": "2025-12-07"
}
```

Example JSON schema for a Favorite item:  

```json
{
  "id": 1,
  "user_id": 2,
  "anime_id": 1
}
```
All persistent data are stored in a centralized **SQLite database**, initialized via `db_setup.py`.

## Emerging Tech Explanation 
OtakuZone integrates interactive data visualization in the admin dashboard using Plotly and Flet. Unlike static charts, these visualizations reflect live or processed user data, enabling admins to:

- Monitor user growth, engagement, and anime popularity in real time
- Identify trends and anomalies quickly
- Make data-driven decisions with actionable insights

**Why chosen:** Improves usability and allows the system to communicate complex data simply.  

**Integration:**
- Data is queried from the SQLite database via analytics services
- Visualizations are generated using Plotly, converted to images, and embedded in Flet UI
- Admins access analytics through a dedicated dashboard tab, with charts and insights updating dynamically

**Limitations:** 
- Performance may degrade with very large datasets
- Real-time updates depend on refresh frequency
- Advanced analytics (predictive, drill-down) are planned for future releases

## Setup & Run Instructions  
1. Clone the repository:  
```bash
git clone https://github.com/Maria-120904/OtakuZone.git
cd OtakuZone
```  
2. Create and activate a virtual environment:  
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```  
3. Install dependencies:  
```bash
pip install -r requirements.txt
```  
4. Initialize the database:  
```bash
python init_db.py
```  
5. Run the application:  
```bash
python main.py
```  
**Supported Platforms:** Windows, Linux (Python 3.13 recommended)  

## Testing Summary 
**How to Run Tests:**
- Manual testing is performed by running the app and verifying all user and admin flows.
- To test, launch the app with:
```bash
python main.py
```  
- Log in as both user and admin.
- Check all navigation routes, authentication, anime management, favorites, and analytics dashboard.
- Confirm window resizing and UI responsiveness.

## Team Roles & Contribution Matrix  
| Contributor | Role / Responsibilities | Contributions / Modules |
|-------------|------------------------|------------------------|
| Recierdo Ma. Francheska (Maria-120904) | Backend logic / Core logic / Project lead/ Data model | Flet UI, main app flow, SQLite schema, init_db scripts |
| Namia Erica Denese (ericadenesenamia)| UI / Documentation | Flet UI, Documentation & README |
| Villaruel Jahn Mariz| Testing | Test scripts|

## Risk / Constraints & Future Enhancements  
**Risks / Constraints:**  
- Limited content since the anime database is manually managed by admin
- No payment system or premium subscription implemented
- No watch history tracking, which may reduce personalized recommendations
- Streaming performance may vary depending on user’s internet connection
- App currently operates with local data structures; no cloud-based syncing

**Future Enhancements:**  
- Add premium subscription system with secure payment integration
- Implement watch history tracking and personalized recommendations
- Integrate external anime APIs for automatic content updates
- Add offline mode with smarter download management
- Enhance admin dashboard with analytics and bulk content-upload tools

## Individual Reflection 

**Recierdo Ma. Francheska (Maria-120904):**  
As the project lead and the main developer for the backend and core logic of OtakuZone, my responsibilities centered on designing the overall flow of the application, structuring the data model, and ensuring that both the user and admin functionalities worked smoothly. I also handled major parts of the UI, which required balancing aesthetics with functionality to make sure users could navigate the app without confusion. One of the biggest challenges I faced was integrating multiple components—login system, anime browsing, streaming interface, and admin controls—into one cohesive system while maintaining performance and usability. Working on the documentation also helped me clearly outline every feature, constraint, and requirement, allowing the project to stay organized from start to finish. This project improved my skills in backend development, interface design, and system planning. It also taught me how to manage time, divide tasks, and guide a team toward completing a shared goal. Overall, the experience strengthened my understanding of how to connect logic, design, and teamwork to build a functional application.

**Namia Erica Denese (ericadenesenamia):**
My primary role in the development of OtakuZone was focused on documentation. I was responsible for organizing and writing the project’s requirements, descriptions, and supporting materials to ensure that every part of the system was clearly explained. This included helping build the SRS, identifying the scope, outlining the features, and making sure that each section accurately reflected what our team developed. Although I was not directly involved in coding, I contributed by making the project understandable, traceable, and easier to present. One of the challenges I encountered was translating technical processes into clear and readable documentation while making sure it stayed consistent with the actual implementation. Through this experience, I gained a deeper appreciation for how essential documentation is in keeping the project aligned and helping the team communicate effectively. It improved my technical writing skills, attention to detail, and my understanding of how software components work together. Overall, this project taught me the importance of accuracy, clarity, and teamwork in delivering a complete and professional output.

**Villaruel Jahn Mariz**
As the team member responsible for testing and quality assurance, my main task was to ensure that OtakuZone worked smoothly across all its modules. I focused on checking the correctness of the login system, anime browsing features, category navigation, and the “Watch Now” functionality. I also tested the profile settings, favorites, and downloads to confirm that each feature performed as expected. One of the challenges I faced was identifying bugs that appeared only during certain user flows, which required patience and repeated testing. Creating test cases helped me structure my approach, making it easier to track issues and verify fixes. Through this project, I strengthened my skills in debugging, analyzing errors, and evaluating the user experience from different perspectives. It also taught me how important systematic testing is for improving the reliability and usability of an application. Overall, this experience made me more detail-oriented, improved my problem-solving skills, and gave me a better understanding of how each component contributes to a fully functional system

---

## Acknowledgments  
- Acknowledgments: Flet framework, SQLite, and open-source inspirations  