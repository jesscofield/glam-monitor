# Glam Orders Monitoring

A containerized monitoring system that tracks database activity for a glam-themed order service.  
The project demonstrates database monitoring using **Prometheus** and **Grafana**, with restricted access for authorized users only.

---

## Project Overview

The system simulates a luxury order service (e.g. cosmetics, perfume, fashion items) and monitors database activity in real time.

Database operations are generated automatically, measured by a custom exporter, collected by Prometheus, and visualized in Grafana dashboards.  
Access to monitoring endpoints is protected via a dedicated authentication service.

---

## Architecture

The project consists of the following services:

- **PostgreSQL** — main database storing orders  
- **Generator (Python)** — simulates application activity by creating and querying orders  
- **Exporter (Python)** — collects database metrics and exposes them in Prometheus format  
- **Prometheus** — collects and stores time-series metrics  
- **Grafana** — visualizes metrics using dashboards  
- **Auth Service (Python + SQLite)** — handles user authentication and token validation  
- **Nginx Gateway** — restricts access to protected services  

All components are containerized and orchestrated using **Docker Compose**.

---

## Implemented Features

- PostgreSQL database running in a Docker container  
- Automatic generation of database activity  
- Custom Prometheus metrics:
  - database request count
  - request latency (histogram)
  - service health status
- Prometheus time-series storage  
- Grafana dashboards with real-time graphs  
- Token-based authorization using a custom authentication service  
- Protected access to monitoring endpoints  
- Incremental development with Git version control  

---

## Metrics Collected

The exporter provides the following metrics:

- `db_requests_total` — total number of database requests  
- `db_request_duration_seconds` — database request latency histogram  
- `app_up` — exporter availability  

These metrics are scraped by Prometheus and visualized in Grafana dashboards.

---

## Grafana Dashboard

The main Grafana dashboard includes:

- Orders per second  
- Database latency (p95)  
- Error rate  
- Exporter status  

The dashboard updates in real time using Prometheus data.

---

## Authorization

Access to monitoring endpoints is restricted using a custom authentication service.

### Demo credentials (local use only)

username: vip
password: 1234


> These credentials are hardcoded for demonstration and testing purposes only.  
> Do not use them in production environments.

### Auth Service Responsibilities

- Stores users in SQLite  
- Issues access tokens  
- Validates tokens via a `/verify` endpoint  

The **Nginx gateway** communicates with this service to allow or deny access to protected endpoints.

---

## Access Points

- **Grafana:**  
  http://localhost:3000  
  (uses Grafana’s built-in authentication)

- **Prometheus UI (protected):**  
  http://localhost:8080/prometheus/

- **Exporter metrics (protected):**  
  http://localhost:8080/metrics/

Only authorized users can access protected endpoints.

---

## How to Run the Project

Make sure **Docker Desktop** is installed and running.

From the project root directory, run:

```bash
docker compose up -d --build