# Aforro Backend - Order & Inventory Management System

### 🚀 Technical Overview

This project is a containerized Django REST application designed to handle inventory management and product discovery.

---
## 🛠 Setup & Installation

### Prerequisites
* Docker Desktop

### Step 1: Clone and Build
Navigate to the project root and run:

``` bash
docker-compose up --build
```
### Step 2: Initialize Database
Run the following commands to setup the database and create your admin account:

``` bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```
### Step 3: Seed Data
Populate the system with 1,000+ products to test the search and performance:

``` bash
docker-compose exec web python manage.py seed_data
```

---

## 📡 Sample API Requests
### 1. Create Order (POST)
**URL**: http://127.0.0.1:8000/orders/

``` JSON
{
  "store_id": 1,
  "items": [
    { "product_id": 4, "quantity_requested": 5 }
  ]
}
```
### 2. Product Search (GET)
**URL**: http://127.0.0.1:8000/api/search/products/?q=phone&sort=price_asc

### 3. Search Autocomplete (GET)
**URL**: http://127.0.0.1:8000/api/search/suggest/?q=ho

---

## 🧠 Caching & Async Logic
### 1. Redis Caching
We cache search results for 5 minutes.
To prevent the database from doing the same heavy work every time a user searches for the same keyword.

### 2. Celery (Async Tasks)
Order confirmations are sent in the background.
The user shouldn't have to wait for an email to be sent before seeing their "Order Confirmed" screen.
We use transaction.on_commit so the background task only triggers if the order is successfully saved to the database.

---

## 📈 Scalability Considerations:

### More Workers: 
Right now, we have one "Web" container and one "Celery" container. We can simply add more copies of these to handle more traffic without changing the code.

### Specialized Search :

Currently, we use the standard database to search for words. As the product list grows, we can move this to a dedicated search engine to make it fast.

### Database Read Replicas:

Most users just "Browse" (Read) rather than "Buy" (Write). We can create "copy" databases that only handle search requests, leaving the main database free to process orders.

### Rate Limiting:

To prevent bots or single users from crashing the server, we can add a limit on how many requests a person can make per minute.
