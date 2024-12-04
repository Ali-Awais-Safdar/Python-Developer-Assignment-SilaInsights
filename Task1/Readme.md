# School Management System

This repository contains a FastAPI-based School Management System for managing students, teachers, and subjects. It also supports functionalities like CSV uploads and error handling.

## Features

- CRUD Operations for:
  - Subjects
  - Teachers
  - Students
- CSV Upload for bulk operations.
- Pagination for efficient data handling.
- Error Handling with informative responses.
- REST API endpoints for integration.
- Dockerized Environment for easy deployment.

## Table of Contents

- Prerequisites
- Setup Instructions
- Running the Project
- API Endpoints
  - Subject Operations
  - Teacher Operations
  - Student Operations
  - CSV Upload
  - Testing Error Cases
- Entity Relationship Diagram
- Contributing
- License

## Prerequisites

- Python 3.9 or later
- Docker and Docker Compose installed

## Setup Instructions

### Clone the Repository
```
git clone <repository_url>
cd <repository_name>
```

### Install Dependencies
Using `requirements.txt`:
```
pip install -r requirements.txt
```
Alternatively, use Docker (see below).

## Running the Project

### Using Docker (Recommended)
Build the Docker image:
```
docker-compose build
```

Start the container:
```
docker-compose up
```

Access the FastAPI app at: [http://localhost:8000](http://localhost:8000)

### Running Locally (Without Docker)
Run the FastAPI app:
```
python run.py
```

Access the app at [http://localhost:8000](http://localhost:8000)

## API Endpoints

### 1. Subject Operations
**Create Subjects**
```
curl -X POST "http://localhost:8000/subjects/" -H "Content-Type: application/json" -d '{"name": "Mathematics"}'
```

**Get All Subjects (with Pagination)**
```
curl "http://localhost:8000/subjects/?page=1&page_size=10"
```

**Get Specific Subject**
```
curl "http://localhost:8000/subjects/1"
```

**Update Subject**
```
curl -X PUT "http://localhost:8000/subjects/1" -H "Content-Type: application/json" -d '{"name": "Advanced Mathematics"}'
```

**Partially Update Subject**
```
curl -X PATCH "http://localhost:8000/subjects/1" -H "Content-Type: application/json" -d '{"name": "Pure Mathematics"}'
```

### 2. Teacher Operations
**Create Teacher**
```
curl -X POST "http://localhost:8000/teachers/" -H "Content-Type: application/json" -d '{
    "name": "John Doe",
    "email": "john.doe@school.com",
    "subject_ids": [1, 2]
}'
```

**Get All Teachers (with Pagination)**
```
curl "http://localhost:8000/teachers/?page=1&page_size=10"
```

**Get Specific Teacher**
```
curl "http://localhost:8000/teachers/1"
```

**Update Teacher**
```
curl -X PUT "http://localhost:8000/teachers/1" -H "Content-Type: application/json" -d '{
    "name": "John Smith",
    "email": "john.smith@school.com",
    "subject_ids": [1, 2, 3]
}'
```

### 3. Student Operations
**Create Student**
```
curl -X POST "http://localhost:8000/students/" -H "Content-Type: application/json" -d '{
    "name": "Alice Johnson",
    "email": "alice@student.com",
    "subject_ids": [1, 2]
}'
```

**Get All Students (with Pagination)**
```
curl "http://localhost:8000/students/?page=1&page_size=10"
```

**Get Specific Student**
```
curl "http://localhost:8000/students/1"
```

### 4. CSV Upload
**Create a Test CSV File**

Example CSV content:
```csv
student_name,student_email,subject_ids,teacher_name,teacher_email
Bob Smith,bob@student.com,"1,2",Jane Doe,jane@school.com
Carol Jones,carol@student.com,"2,3",Jane Doe,jane@school.com
```

**Upload the CSV File**
```
curl -X POST "http://localhost:8000/upload-csv/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.csv"
```

### 5. Testing Error Cases
**Non-Existent Subject**
```
curl "http://localhost:8000/subjects/999"
```

**Invalid Subject IDs**
```
curl -X POST "http://localhost:8000/teachers/" -H "Content-Type: application/json" -d '{
    "name": "Invalid Teacher",
    "email": "invalid@school.com",
    "subject_ids": [999, 998]
}'
```

## Entity Relationship Diagram
The Entity Relationship (ER) Diagram provides an overview of the database structure.
![alt text](https://github.com/Ali-Awais-Safdar/Python-Developer-Assignment-SilaInsights/blob/master/Task1/erDiagram/schema.png)

