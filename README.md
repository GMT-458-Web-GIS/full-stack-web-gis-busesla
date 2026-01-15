# 🎓 Hacettepe Community Event Portal (Web-GIS)

A full-stack Web-GIS application designed for student communities at Hacettepe University Beytepe Campus to manage spatial event data, fully compliant with the **GMT 458** final assignment criteria.

## 🎯 Project Objectives
Developed between **January 12-16, 2026**, this project focuses on managing heterogeneous spatial data in a NoSQL environment with role-based access control and full CRUD capabilities on a geographical point layer.

## 🚀 Requirement Fulfillment Matrix

| Requirement | Weight | Status | Technical Implementation |
| :--- | :---: | :---: | :--- |
| **Authentication** | 15% | ✅ | Secure Sign-up/Login system with OTP verification. |
| **Managing User Types** | 20% | ✅ | STUDENT, COMMUNITY_LEADER, and ADMIN roles with RBAC. |
| **NoSQL Database** | 25% | ✅ | MongoDB Atlas utilized for heterogeneous data management. |
| **Performance (Indexing)** | 25% | ✅ | `2dsphere` (R-Tree) index for spatial query optimization. |
| **Performance Testing** | 25% | ✅ | Load and Stress testing conducted to monitor response times. |
| **CRUD Operations** | 15% | ✅ | Full spatial CRUD on geographical point layers. |
| **API Development** | 25% | ✅ | Swagger-documented API with Postman validation. |
| **GitHub Management** | 10% | ✅ | 5+ commits on different days via GitHub Classroom. |

## 📸 Procedures & Implementation Details

### 1. User Authentication & Verification
The portal uses a secure authentication flow. Users register with Hacettepe credentials and must verify their account using a 6-digit OTP code sent via the system.
> **Screenshot 1 & 2:**
> ![Login Page](1.png)
> ![OTP Verification](2.png)

### 2. Role-Based Access Control (RBAC)
The system supports three distinct user types managed in a NoSQL backend. Permissions are dynamically adjusted: Students can only view, while Admins/Leaders can manage data.
* **STUDENT:** View-only access.
* **ADMIN/LEADER:** Full management rights.
> **Screenshot 3 & 6:**
> ![Community Selection](3.png)
> ![MongoDB Roles](6.png)

### 3. Spatial Data Infrastructure (GIS CRUD)
Admins can interactively add event locations on the campus map using a modern UI modal. Data is stored as GeoJSON features in MongoDB.
* **Automated Logic:** If an image URL is not provided, the system defaults to the community-specific logo.
> **Screenshot 4 & 5:**
> ![Map Interface](4.png)
> ![Add Event Modal](5.png)

### 4. API Development & Validation
The backend API exposes spatial and non-spatial resources, fully documented via **Swagger UI** and rigorously tested using **Postman** for all HTTP methods (GET, POST, PUT, DELETE).
> **Screenshot 11 (Swagger):**
> ![Swagger UI](11.png)
> **Screenshots 7, 8, 9, 10 (Postman Testing):**
> ![Postman GET](7.png) | ![Postman PUT](8.png) | ![Postman POST](9.png) | ![Postman DELETE](10.png)

### 5. Performance Monitoring & Stress Testing
To observe the impact of indexing and system stability, performance tests were conducted. We monitored response times under various load conditions to ensure the FastAPI backend remains resilient.
* **Indexing:** Implementation of `2dsphere` index reduced spatial query latency.
* **Stress Test:** Monitored variation in response times under concurrent user simulation.
> **Screenshot 12 & 13:**
> ![Response Time Graph](12.png)
> ![Stress Test Results](13.png)

### 6. Deployment & Future Work (AWS)
The project is architected for cloud scalability. Preliminary configurations for AWS EC2 instances have been established to support live deployment.
> **Screenshot 14:**
> ![AWS Instance Summary](14.png)

## 🛠️ Tech Stack
* **Backend:** FastAPI (Python), Uvicorn.
* **Frontend:** Leaflet.js, Vanilla JS (ES6+), Modern CSS.
* **Database:** MongoDB Atlas (NoSQL), Motor (Async Driver).
* **Security:** Passlib (Bcrypt), OTP Verification.

## 📦 Installation
1. **Backend:** `cd backend` -> `python -m uvicorn main:app --reload`
2. **Frontend:** Open `index.html` via **Live Server**.

---
**Developer:** Busesla | 
