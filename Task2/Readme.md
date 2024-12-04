# Creator Metrics API

A FastAPI application for computing, managing, and retrieving creator metrics using PostgreSQL.

## Table of Contents

- Installation
- Database Setup
- Environment Configuration
- Running the Application
  - Using `run.py`
  - Using Docker
- Endpoints and Testing
- ER Diagram

## Installation

### Clone the Repository
```
git clone <repository_url>
cd <repository_name>
```

## Database Setup

Ensure PostgreSQL is installed on your system.

Create a database and user:
```sql
-- Open the SQL CLI and enter the password you set up

-- Replace 'your_username' and 'your_password' with your credentials
CREATE USER your_username WITH PASSWORD 'your_password';
CREATE DATABASE metrics_db;
GRANT ALL PRIVILEGES ON DATABASE metrics_db TO your_username;
ALTER DATABASE metrics_db OWNER TO your_username;
```

Verify access by connecting to the database.

## Environment Configuration

Create a `.env` file in the root directory:
```
DATABASE_URL=postgresql://your_username:password@localhost:5432/metrics_db
```

Replace `your_username` and `password` with your actual credentials.

## Running the Application

### Using `run.py`

Ensure all dependencies are installed:
```
pip install -r requirements.txt
```

Run the application:
```
python run.py
```

The server will start at [http://localhost:8000](http://localhost:8000).

### Using Docker

Ensure Docker and Docker Compose are installed.

Navigate to the project directory.

Build and start the containers:
```
# Build the containers
docker-compose build

# Start the containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the containers
docker-compose down
```
The server will start at [http://localhost:8000](http://localhost:8000).

## Endpoints and Testing

You can test the API using the following `curl` commands. Ensure the server is running.

### Compute Metrics Endpoint:
```
# Basic metrics computation
curl -X POST "http://localhost:8000/api/v1/metrics/compute" \
   -H "accept: application/json" \
   -H "Content-Type: multipart/form-data" \
   -F "profile_file=@./data/profile.csv" \
   -F "posts_file=@./data/posts.csv"

# Error case - Empty files
curl -X POST "http://localhost:8000/api/v1/metrics/compute" \
   -H "accept: application/json" \
   -H "Content-Type: multipart/form-data" \
   -F "profile_file=@/dev/null" \
   -F "posts_file=@/dev/null"
```

### Get Metrics Endpoint:
```
# Retrieve metrics for a specific username
curl -X GET "http://localhost:8000/api/v1/metrics/bo3omar22" \
   -H "accept: application/json"

# Error case - Non-existent username
curl -X GET "http://localhost:8000/api/v1/metrics/nonexistent_user" \
   -H "accept: application/json"
```

### Delete Metrics Endpoint:
```
# Delete metrics for a username
curl -X DELETE "http://localhost:8000/api/v1/metrics/bo3omar22" \
   -H "accept: application/json"

# Error case - Non-existent username
curl -X DELETE "http://localhost:8000/api/v1/metrics/nonexistent_user" \
   -H "accept: application/json"
```

### Health Check Endpoint:
```
# Check API and database health
curl -X GET "http://localhost:8000/api/v1/health" \
   -H "accept: application/json"
```

## ER Diagram

The Entity Relationship (ER) Diagram illustrates the structure of the database and its relationships.
![alt text](https://github.com/Ali-Awais-Safdar/RoutingVisualizationBetweenTwoEndpoints-OSM/blob/master/output.png)
