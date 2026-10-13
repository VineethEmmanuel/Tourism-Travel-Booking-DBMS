# ✈️ Wanderlust — Tourism Package & Travel Booking DBMS

A fully functional, interactive **web-based Simulator and Management System** for a Tourism & Travel Booking database, built with Python + Streamlit + SQLite.

---

## 🚀 Quick Start (Zero Config)

```bash
# 1. Navigate into the project directory
cd /path/to/DBMS

# 2. Create a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install streamlit pandas plotly

# 4. Launch the application
streamlit run app.py
```

App will open at: **http://localhost:8501**

---

## 🏗️ Architecture Overview

```
DBMS/
├── app.py            ← Streamlit multi-role web application (UI)
├── db.py             ← SQLite engine, business rules & query helpers
├── schema.sql        ← 13-entity 3NF DDL schema definition
├── test_system.py    ← Comprehensive integrity & lifecycle test suite
├── travel_tourism.db ← SQLite database (auto-created on first run)
└── README.md
```

---

## 🗄️ Database Schema — 13 Core Entities (3NF)

All 13 tables strictly adhere to **Third Normal Form (3NF)**:

| # | Relation | Primary Key | Foreign Keys |
|---|----------|-------------|--------------|
| 1 | **Destination** | Dest_ID | — |
| 2 | **Package** | Package_ID | Dest_ID → Destination |
| 3 | **Itinerary_Day** | Itin_ID | Package_ID → Package |
| 4 | **Guide** | Guide_ID | — |
| 5 | **Hotel** | Hotel_ID | Dest_ID → Destination |
| 6 | **Transport** | Transport_ID | — |
| 7 | **Departure** | Depart_ID | Package_ID, Guide_ID, Transport_ID |
| 8 | **Customer** | Cust_ID | — |
| 9 | **Booking** | Booking_ID | Cust_ID, Depart_ID |
| 10 | **Traveller** | Traveller_ID | Booking_ID → Booking |
| 11 | **Payment** | Payment_ID | Booking_ID → Booking |
| 12 | **Cancellation** | Cancel_ID | Booking_ID → Booking |
| 13 | **Refund** | Refund_ID | Cancel_ID → Cancellation |

---

## 🛡️ Business Integrity Rules Enforced

### 1. Capacity Control (Overbooking Prevention)
- Total Traveller registrations per Departure cannot exceed Max_Capacity
- Enforced atomically inside a database transaction at booking creation

### 2. Guide Double-Booking Prevention
- A Guide cannot be assigned to two departures with overlapping Start_Date / End_Date
- Validated before every Departure INSERT

### 3. Transport Asset Conflict Prevention
- A Transport vehicle cannot be assigned to overlapping departures

### 4. Financial Integrity
- Total Refund amounts cannot exceed total Payment amounts for a booking
- Validated on refund creation and status update actions

---

## 👤 User Roles

### Administrator (Travel Agent)
- Executive KPI Dashboard — Revenue metrics, seat utilization, departure overview
- Departure Scheduler — Schedule tours with real-time conflict checking
- Catalog Manager — CRUD for Destinations, Packages, Itineraries, Hotels, Transport, Guides
- Bookings & Refunds — Full booking log and refund adjudication queue
- SQL Console — Live SQL query executor with schema browser

### Customer (Lead Traveller)
- Package Discovery — Browse destinations with itineraries and hotel options
- Booking Flow — Select departure, register traveller roster, confirm with capacity check
- My Trips — Payment history, add payments, cancel booking and request refund

### Tour Guide (Read-Only)
- Assigned Departures — Conflict-free view of all scheduled/active tours
- Passenger Manifest — Full traveller roster with lead customer contact
- Daily Itinerary — Activity guide for each tour day

---

## 🌍 Pre-Loaded Seed Data

| Category | Count | Examples |
|----------|-------|---------|
| Destinations | 6 | Paris, Kyoto, Rome, Bali, Cape Town, Swiss Alps |
| Packages | 6 | Parisian Romance, Kyoto Zen Odyssey, Alpine Expedition... |
| Itinerary Days | 39 | Full day-by-day activities for each 5-8 day tour |
| Guides | 6 | Jean-Luc Moreau, Kenji Takahashi, Astrid Zimmermann... |
| Hotels | 12 | 4-5 star properties per destination |
| Transport | 5 | Luxury coaches, VIP buses, sprinter vans |
| Departures | 8 | Spanning Nov 2026 – Dec 2026 |
| Customers | 6 | Eleanor Vance, Marcus Smith, Priya Sharma... |
| Bookings | 6 | Including 1 cancelled with refund record |

---

## 🧪 Running Tests

```bash
source .venv/bin/activate
python3 test_system.py -v
```

9 tests, all passing — covering overbooking prevention, guide/transport conflict detection,
financial integrity, full customer lifecycle, and guide portal correctness.

---

## 🔄 Database Reset

Click "Reset & Reseed Database" in the sidebar, or run:

```python
import db
db.init_db(force_reset=True)
```
