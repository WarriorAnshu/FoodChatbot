# 🍔 Full Stack NLP Food Delivery Chatbot (Pandeyji Eatery)

An end-to-end Conversational AI Food Delivery Chatbot built using **Google Dialogflow**, **FastAPI**, **MySQL**, and **ngrok**. The system provides multi-turn conversational ordering, dynamic cart management (add, remove, complete), real-time order tracking, and relational database persistence.

---

## 📌 Features & Architecture

### 1. **Natural Language Understanding (Dialogflow NLU)**
* **Custom Intents & Context Management**: Supports 5+ intents (`New-order`, `Add-order`, `Remove-order`, `Complete-order`, `Track-Order`) with input/output context tracking (`ongoing-order`, `ongoing-tracking`).
* **Entity Extraction**: Utilizes built-in `@sys.number` and custom `@Food-Item` entities with extensive synonyms and fuzzy matching across 9 menu items.
* **Context Clean-up**: Automatically clears in-memory session caches when a user initiates a `New-order` flow, preventing cart contamination across sessions.

### 2. **Backend Webhook Service (FastAPI & Python)**
* **Asynchronous Routing**: Built with **FastAPI** & **Uvicorn** for high-throughput ASGI request handling.
* **Regex Session Extraction**: Uses robust regular expression parsing (`r"/sessions/([^/]+)"`) to isolate individual user session IDs across webhook payloads.
* **Session Cart State**: Maintains isolated active carts (`inprogress_order`) in memory, enabling seamless item addition, removal validation, and empty-cart checks.

### 3. **Relational Database Management (MySQL)**
* **Schema Design**: Normalized relational tables (`orders`, `order_tracking`, `food_items`).
* **Stored Procedures & UDFs**:
  * `insert_order_item`: Stored procedure for transactional item insertion.
  * `get_total_order_price`: User-Defined Function (UDF) for dynamic bill calculation.
* **Order Tracking Pipeline**: Tracks order state progression (`in progress`, `in transit`, `delivered`).

---

## 🛠️ Tech Stack & Prerequisites

* **Language**: Python 3.11+
* **Framework**: FastAPI, Uvicorn
* **NLP Platform**: Google Dialogflow ES
* **Database**: MySQL Server 8.0+ / MySQL Workbench
* **Tunneling**: ngrok
* **Frontend**: HTML5, CSS3, JavaScript (Embedded iframe Chat Widget)

---

## 📁 Project Structure

```
FoodChatbot/
│
├── main.py            # FastAPI main server & webhook intent routing engine
├── db_helper.py       # MySQL connector, stored procedures, & UDF interface
├── generic_helper.py  # Regex session extraction & string formatting utilities
├── requirements.txt   # Dependencies (fastapi, uvicorn, mysql-connector-python)
│
├── database/          # Database dump SQL scripts (schema & seed data)
│   └── pandeyji_eatery.sql
│
└── frontend/          # Web interface
    ├── index.html     # Food ordering website page
    └── style.css      # UI styles and embedded chatbot iframe styling
```

---

## 🚀 Setup & Installation

### 1. Database Setup (MySQL)
1. Open MySQL Workbench and import `database/pandeyji_eatery.sql`.
2. Ensure the database `pandeyji_eatery` contains the tables `food_items`, `orders`, and `order_tracking`, along with the stored procedure `insert_order_item` and function `get_total_order_price`.
3. Update `DB_CONFIG` credentials in `db_helper.py`:
   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "root",
       "password": "YOUR_MYSQL_PASSWORD",
       "database": "pandeyji_eatery"
   }
   ```

### 2. Backend Setup
1. Clone the repository and navigate into the project directory:
   ```bash
   cd FoodChatbot
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the FastAPI backend server:
   ```bash
   uvicorn main:app --reload
   ```
   *The server will start at `http://127.0.0.1:8000`.*

### 3. Exposing Webhook via ngrok
1. In a second terminal window, run ngrok on port 8000:
   ```bash
   ngrok http 8000
   ```
2. Copy the secure HTTPS forwarding URL (e.g., `https://xxxx.ngrok-free.app`).
3. Open **Dialogflow Console > Fulfillment**, enable Webhook, paste the HTTPS URL with a trailing slash (`https://xxxx.ngrok-free.app/`), and save.

---

## 💬 Conversation Flow Example

```
User:       "Hi, I'd like to start a new order."
Chatbot:    "Starting a new order! What would you like to have? You can specify items and quantities."

User:       "Add 2 pizzas and 1 mango lassi"
Chatbot:    "Current order: Pizza (x2), Mango Lassi (x1). You can add more items or complete the order."

User:       "Remove pizza"
Chatbot:    "Removed Pizza from your order. Current order is: Mango Lassi (x1)."

User:       "That's all"
Chatbot:    "Your order has been completed! Your order ID is 45 and the total amount is $5.00."

User:       "Track order 45"
Chatbot:    "Your order status for order 45 is: in progress"
```

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
