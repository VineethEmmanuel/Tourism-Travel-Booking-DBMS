import sqlite3
import os
from datetime import datetime, date

DB_FILE = os.path.join(os.path.dirname(__file__), "travel_tourism.db")
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")

def get_connection():
    """Returns a SQLite connection with foreign key enforcement and row factory."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reset=False):
    """Initializes the database using schema.sql and seeds initial data if needed."""
    if force_reset and os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    db_exists = os.path.exists(DB_FILE)
    conn = get_connection()
    
    with open(SCHEMA_FILE, "r") as f:
        schema_sql = f.read()
        
    conn.executescript(schema_sql)
    conn.commit()
    
    # Check if database has destinations
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Destination;")
    dest_count = cursor.fetchone()[0]
    
    if dest_count == 0:
        seed_data(conn)
        
    conn.close()

def seed_data(conn):
    """Pre-populates the database with realistic sample data across all 13 3NF tables."""
    cursor = conn.cursor()
    
    # 1. Destinations
    destinations = [
        ("Paris", "France", "The City of Light, famous for romantic boulevards, art museums like the Louvre, and iconic Eiffel Tower."),
        ("Kyoto", "Japan", "Ancient imperial capital with thousands of classical Buddhist temples, serene zen gardens, and bamboo groves."),
        ("Rome", "Italy", "The Eternal City steeped in history, home to the Colosseum, Roman Forum, and Vatican City."),
        ("Bali", "Indonesia", "Tropical paradise known for volcanic landscapes, lush rice terraces, sacred sea temples, and wellness retreats."),
        ("Cape Town", "South Africa", "Vibrant coastal jewel nestled under Table Mountain, renowned for penguins at Boulders Beach and scenic wineries."),
        ("Swiss Alps", "Switzerland", "Breathtaking mountain wonderland featuring Zermatt, the Matterhorn, glacier lakes, and scenic rail journeys.")
    ]
    cursor.executemany("INSERT INTO Destination (Name, Country, Description) VALUES (?, ?, ?);", destinations)
    
    # 2. Packages
    packages = [
        (1, "Parisian Romance & Art Discovery", 5, 1450.0),
        (2, "Kyoto Cultural & Zen Odyssey", 7, 2100.0),
        (3, "Classic Rome & Vatican Wonders", 6, 1750.0),
        (4, "Tropical Bali Wellness & Surf", 6, 1200.0),
        (5, "Cape Town & Garden Route Safari", 8, 2600.0),
        (6, "Swiss Alpine Glacier Expedition", 7, 2950.0)
    ]
    cursor.executemany("INSERT INTO Package (Dest_ID, Name, Duration_Days, Base_Price) VALUES (?, ?, ?, ?);", packages)
    
    # 3. Itinerary_Day
    itineraries = [
        # Paris (5 days)
        (1, 1, "Arrival in Paris, private airport transfer, welcome champagne reception overlooking the Seine River."),
        (1, 2, "Guided morning tour of Musée d'Orsay and the Louvre; evening Seine River sunset dinner cruise."),
        (1, 3, "Montmartre bohemian walking tour, Sacré-Cœur basilica, and artisan bakery pastry workshop."),
        (1, 4, "Day excursion to the Palace of Versailles and Marie Antoinette's private gardens."),
        (1, 5, "Eiffel Tower summit visit, leisure shopping along Champs-Élysées, and farewell Michelin-star dinner."),
        # Kyoto (7 days)
        (2, 1, "Arrival at Kansai/Kyoto station, traditional tea ceremony check-in at ryokan."),
        (2, 2, "Fushimi Inari thousand torii gates sunrise hike followed by Kiyomizu-dera temple exploration."),
        (2, 3, "Kinkaku-ji (Golden Pavilion) and Ryoan-ji rock garden meditation with a Zen Buddhist monk."),
        (2, 4, "Arashiyama bamboo forest walk, Iwatayama monkey park, and traditional Sagano scenic train."),
        (2, 5, "Culinary street tasting tour in Nishiki Market and evening Gion geisha district walk."),
        (2, 6, "Day excursion to Nara deer park and Todai-ji Great Buddha temple."),
        (2, 7, "Uji matcha tea plantation masterclass and farewell kaiseki banquet."),
        # Rome (6 days)
        (3, 1, "Arrival in Rome, check-in, sunset walking tour through Piazza Navona and Pantheon."),
        (3, 2, "VIP skip-the-line Colosseum, Roman Forum, and Palatine Hill archaeological journey."),
        (3, 3, "Vatican Museums, Sistine Chapel, and St. Peter's Basilica with an art historian."),
        (3, 4, "Trastevere food crawl, artisanal gelato tasting, and Trevi Fountain wishing tradition."),
        (3, 5, "Day trip to Villa d'Este and Hadrian's Villa in Tivoli."),
        (3, 6, "Appian Way e-bike tour and rooftop farewell dinner overlooking ancient aqueducts."),
        # Bali (6 days)
        (4, 1, "Denpasar airport transfer to Ubud luxury jungle resort, herbal blessing ceremony."),
        (4, 2, "Tegallalang rice terraces sunrise walk, Campuhan ridge hike, and Balinese cooking school."),
        (4, 3, "Tirta Empul holy spring water purification ritual and Gunung Kawi ancient shrines."),
        (4, 4, "Mount Batur sunrise volcanic jeep safari followed by natural hot springs soak."),
        (4, 5, "Transfer to Uluwatu clifftop resort, surf lesson, and Kecak fire dance at sunset."),
        (4, 6, "Beachfront yoga, Ayurvedic spa treatment, and sunset farewell seafood feast."),
        # Cape Town (8 days)
        (5, 1, "Arrival in Cape Town, check-in at Waterfront hotel, panoramic Table Mountain cable car."),
        (5, 2, "Cape Peninsula coastal drive: Chapman's Peak, Cape Point, and Boulders Beach penguins."),
        (5, 3, "Robben Island historical tour and Zeitz MOCAA contemporary African art museum."),
        (5, 4, "Full day Stellenbosch and Franschhoek premier wine and cheese tasting tour."),
        (5, 5, "Transfer to private game reserve for twilight Big Five safari game drive."),
        (5, 6, "Dawn safari tracking lions and elephants, bushveld breakfast, and conservation talk."),
        (5, 7, "Kirstenbosch botanical gardens canopy walkway and sunset catamaran cruise in Camps Bay."),
        (5, 8, "V&A Waterfront shopping and traditional African djembe drumming farewell dinner."),
        # Swiss Alps (7 days)
        (6, 1, "Scenic train transfer from Zurich to Zermatt, car-free alpine village walk."),
        (6, 2, "Gornergrat cogwheel train for iconic Matterhorn panoramic views and glacier trail hike."),
        (6, 3, "Matterhorn Glacier Paradise cable car, ice palace exploration, and fondue lunch."),
        (6, 4, "Panoramic Glacier Express train ride through alpine passes to Interlaken."),
        (6, 5, "Jungfraujoch - Top of Europe rail journey, Sphinx observatory, and Aletsch Glacier."),
        (6, 6, "Lake Brienz turquoise paddle-steamer cruise and Giessbach waterfall hike."),
        (6, 7, "Alpine cheese making masterclass and farewell celebration with Swiss raclette.")
    ]
    cursor.executemany("INSERT INTO Itinerary_Day (Package_ID, Day_Number, Activity) VALUES (?, ?, ?);", itineraries)
    
    # 4. Guides
    guides = [
        ("Jean-Luc Moreau", "+33 6 12 34 56 78", "English, French, Spanish"),
        ("Kenji Takahashi", "+81 90 2345 6789", "English, Japanese"),
        ("Matteo Rossi", "+39 06 9876 5432", "English, Italian, German"),
        ("Wayan Sudarsana", "+62 812 3456 7890", "English, Indonesian"),
        ("Thabo Ndlovu", "+27 82 456 7890", "English, Zulu, Afrikaans"),
        ("Astrid Zimmermann", "+41 79 123 4567", "English, German, French, Italian")
    ]
    cursor.executemany("INSERT INTO Guide (Name, Contact, Language) VALUES (?, ?, ?);", guides)
    
    # 5. Hotels
    hotels = [
        (1, "Le Grand Hôtel Vendôme", 5),
        (1, "Hôtel Montmartre Charme", 4),
        (2, "Kyoto Ryokan Hoshinoya", 5),
        (2, "Gion Miyako Hotel", 4),
        (3, "Hotel de Russie Roma", 5),
        (3, "Navona Grand Palace", 4),
        (4, "Ubud Rainforest Sanctuary", 5),
        (4, "Seminyak Beach Resort", 4),
        (5, "The Silo Waterfront Hotel", 5),
        (5, "Camps Bay Boutique Villa", 4),
        (6, "The Chedi Andermatt", 5),
        (6, "Zermatt Matterhorn Lodge", 4)
    ]
    cursor.executemany("INSERT INTO Hotel (Dest_ID, Name, Star_Rating) VALUES (?, ?, ?);", hotels)
    
    # 6. Transport
    transports = [
        ("Mercedes-Benz Tourismo Coach", 35),
        ("Setra TopClass VIP Bus", 25),
        ("Mercedes-Benz Sprinter Van", 14),
        ("Ford Transit Executive", 10),
        ("Range Rover Alpine Safari 4x4", 6)
    ]
    cursor.executemany("INSERT INTO Transport (Type, Capacity) VALUES (?, ?);", transports)
    
    # 7. Departures
    # Packages:
    # 1: Paris (5d), 2: Kyoto (7d), 3: Rome (6d), 4: Bali (6d), 5: Cape Town (8d), 6: Swiss (7d)
    # Guides: 1: Jean-Luc, 2: Kenji, 3: Matteo, 4: Wayan, 5: Thabo, 6: Astrid
    # Transports: 1: Coach(35), 2: VIP Bus(25), 3: Sprinter(14), 4: Ford(10), 5: RangeRover(6)
    departures = [
        # ID 1: Paris
        (1, 1, 3, "2026-11-01", "2026-11-05", 14, "Scheduled"),
        # ID 2: Kyoto
        (2, 2, 2, "2026-11-10", "2026-11-16", 20, "Scheduled"),
        # ID 3: Rome
        (3, 3, 3, "2026-11-15", "2026-11-20", 12, "Scheduled"),
        # ID 4: Bali
        (4, 4, 4, "2026-11-20", "2026-11-25", 10, "Scheduled"),
        # ID 5: Cape Town (In progress / ongoing)
        (5, 5, 2, "2026-10-10", "2026-10-17", 18, "In Progress"),
        # ID 6: Swiss Alps
        (6, 6, 5, "2026-12-01", "2026-12-07", 6, "Scheduled"),
        # ID 7: Paris future
        (1, 1, 3, "2026-12-10", "2026-12-14", 14, "Scheduled"),
        # ID 8: Rome completed past departure
        (3, 3, 4, "2026-09-01", "2026-09-06", 10, "Completed")
    ]
    cursor.executemany(
        "INSERT INTO Departure (Package_ID, Guide_ID, Transport_ID, Start_Date, End_Date, Max_Capacity, Status) VALUES (?, ?, ?, ?, ?, ?, ?);",
        departures
    )
    
    # 8. Customers
    customers = [
        ("Eleanor Vance", "eleanor.vance@example.com"),
        ("Marcus Aurelius Smith", "marcus.smith@example.com"),
        ("Priya Sharma", "priya.sharma@example.com"),
        ("David Miller", "david.miller@example.com"),
        ("Elena Rostova", "elena.rostova@example.com"),
        ("James Wilson", "james.wilson@example.com")
    ]
    cursor.executemany("INSERT INTO Customer (Name, Email) VALUES (?, ?);", customers)
    
    # 9. Bookings
    # Package 1 base = 1450, Package 2 = 2100, Package 3 = 1750, Package 6 = 2950
    bookings = [
        # Booking 1: Eleanor booked Paris (Depart 1), 2 travellers -> 2 * 1450 = 2900
        (1, 1, "2026-10-01", 2900.0, "Confirmed"),
        # Booking 2: Marcus booked Kyoto (Depart 2), 3 travellers -> 3 * 2100 = 6300
        (2, 2, "2026-10-02", 6300.0, "Confirmed"),
        # Booking 3: Priya booked Rome (Depart 3), 2 travellers -> 2 * 1750 = 3500
        (3, 3, "2026-10-03", 3500.0, "Confirmed"),
        # Booking 4: David booked Swiss (Depart 6), 2 travellers -> 2 * 2950 = 5900
        (4, 6, "2026-10-04", 5900.0, "Confirmed"),
        # Booking 5: Elena booked Paris (Depart 1), 1 traveller -> 1450, then CANCELLED
        (5, 1, "2026-10-05", 1450.0, "Cancelled"),
        # Booking 6: James booked Bali (Depart 4), 2 travellers -> 2 * 1200 = 2400
        (6, 4, "2026-10-06", 2400.0, "Pending Payment")
    ]
    cursor.executemany(
        "INSERT INTO Booking (Cust_ID, Depart_ID, Booking_Date, Total_Amount, Status) VALUES (?, ?, ?, ?, ?);",
        bookings
    )
    
    # 10. Travellers
    travellers = [
        # Booking 1 (Paris)
        (1, "Eleanor Vance", 34),
        (1, "Thomas Vance", 36),
        # Booking 2 (Kyoto)
        (2, "Marcus Aurelius Smith", 42),
        (2, "Lucia Smith", 39),
        (2, "Leo Smith", 12),
        # Booking 3 (Rome)
        (3, "Priya Sharma", 29),
        (3, "Arjun Sharma", 31),
        # Booking 4 (Swiss)
        (4, "David Miller", 45),
        (4, "Sarah Miller", 44),
        # Booking 5 (Cancelled Paris)
        (5, "Elena Rostova", 28),
        # Booking 6 (Bali)
        (6, "James Wilson", 33),
        (6, "Clara Wilson", 30)
    ]
    cursor.executemany("INSERT INTO Traveller (Booking_ID, Name, Age) VALUES (?, ?, ?);", travellers)
    
    # 11. Payments
    payments = [
        # Booking 1 fully paid
        (1, 2900.0, "2026-10-01"),
        # Booking 2 paid deposit + final
        (2, 3000.0, "2026-10-02"),
        (2, 3300.0, "2026-10-05"),
        # Booking 3 fully paid
        (3, 3500.0, "2026-10-03"),
        # Booking 4 deposit paid
        (4, 3000.0, "2026-10-04"),
        # Booking 5 (Elena) had paid before cancelling
        (5, 1450.0, "2026-10-05")
    ]
    cursor.executemany("INSERT INTO Payment (Booking_ID, Amount, Payment_Date) VALUES (?, ?, ?);", payments)
    
    # 12. Cancellations
    cancellations = [
        # Booking 5 cancelled
        (5, "2026-10-08", "Medical emergency - unable to travel internationally.")
    ]
    cursor.executemany("INSERT INTO Cancellation (Booking_ID, Cancel_Date, Reason) VALUES (?, ?, ?);", cancellations)
    
    # 13. Refunds
    refunds = [
        # Cancel ID 1: 1200 refunded out of 1450 paid (after standard 250 administrative fee)
        (1, 1200.0, "Processed")
    ]
    cursor.executemany("INSERT INTO Refund (Cancel_ID, Amount, Status) VALUES (?, ?, ?);", refunds)
    
    conn.commit()

# ============================================================================
# BUSINESS INTEGRITY VERIFICATION ENGINES
# ============================================================================

def dates_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    """Returns True if two date ranges [start1, end1] and [start2, end2] overlap."""
    d_start1 = datetime.strptime(start1, "%Y-%m-%d").date()
    d_end1 = datetime.strptime(end1, "%Y-%m-%d").date()
    d_start2 = datetime.strptime(start2, "%Y-%m-%d").date()
    d_end2 = datetime.strptime(end2, "%Y-%m-%d").date()
    return d_start1 <= d_end2 and d_end1 >= d_start2

def check_guide_conflict(guide_id: int, start_date: str, end_date: str, exclude_depart_id: int = None):
    """
    Checks if a guide is already booked for an overlapping departure.
    Rule: A Guide cannot be double-booked across active departures.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT d.Depart_ID, d.Start_Date, d.End_Date, p.Name as Package_Name, g.Name as Guide_Name
        FROM Departure d
        JOIN Package p ON d.Package_ID = p.Package_ID
        JOIN Guide g ON d.Guide_ID = g.Guide_ID
        WHERE d.Guide_ID = ? AND d.Status != 'Cancelled'
    """
    params = [guide_id]
    if exclude_depart_id:
        query += " AND d.Depart_ID != ?"
        params.append(exclude_depart_id)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    conflicts = []
    for row in rows:
        if dates_overlap(start_date, end_date, row["Start_Date"], row["End_Date"]):
            conflicts.append(dict(row))
            
    return (len(conflicts) > 0, conflicts)

def check_transport_conflict(transport_id: int, start_date: str, end_date: str, exclude_depart_id: int = None):
    """
    Checks if a transport vehicle is already assigned for an overlapping departure.
    Rule: Transport cannot be double-booked across active departures.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT d.Depart_ID, d.Start_Date, d.End_Date, p.Name as Package_Name, t.Type as Transport_Type
        FROM Departure d
        JOIN Package p ON d.Package_ID = p.Package_ID
        JOIN Transport t ON d.Transport_ID = t.Transport_ID
        WHERE d.Transport_ID = ? AND d.Status != 'Cancelled'
    """
    params = [transport_id]
    if exclude_depart_id:
        query += " AND d.Depart_ID != ?"
        params.append(exclude_depart_id)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    conflicts = []
    for row in rows:
        if dates_overlap(start_date, end_date, row["Start_Date"], row["End_Date"]):
            conflicts.append(dict(row))
            
    return (len(conflicts) > 0, conflicts)

def get_departure_occupancy(depart_id: int):
    """
    Returns (booked_travellers, max_capacity, available_seats) for a departure.
    Only counts travellers belonging to non-cancelled bookings.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Max_Capacity FROM Departure WHERE Depart_ID = ?;", (depart_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return (0, 0, 0)
    max_cap = row["Max_Capacity"]
    
    cursor.execute("""
        SELECT COUNT(t.Traveller_ID) as Booked
        FROM Traveller t
        JOIN Booking b ON t.Booking_ID = b.Booking_ID
        WHERE b.Depart_ID = ? AND b.Status != 'Cancelled';
    """, (depart_id,))
    booked = cursor.fetchone()["Booked"]
    conn.close()
    
    available = max(0, max_cap - booked)
    return (booked, max_cap, available)

def check_capacity_available(depart_id: int, num_travellers: int):
    """Verifies that adding num_travellers will not exceed Max_Capacity."""
    booked, max_cap, available = get_departure_occupancy(depart_id)
    if booked + num_travellers > max_cap:
        return (False, booked, max_cap, available, f"Overbooking prevented! Requested {num_travellers} seats, but only {available} of {max_cap} remain.")
    return (True, booked, max_cap, available, "")

def check_refund_integrity(booking_id: int, requested_amount: float):
    """
    Ensures total refunds for a booking do not exceed total payments made.
    Rule: Total Refund amounts cannot exceed the corresponding Payment amounts for a booking.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Total paid
    cursor.execute("SELECT COALESCE(SUM(Amount), 0.0) as Total_Paid FROM Payment WHERE Booking_ID = ?;", (booking_id,))
    total_paid = cursor.fetchone()["Total_Paid"]
    
    # Total already refunded or approved
    cursor.execute("""
        SELECT COALESCE(SUM(r.Amount), 0.0) as Total_Refunded
        FROM Refund r
        JOIN Cancellation c ON r.Cancel_ID = c.Cancel_ID
        WHERE c.Booking_ID = ? AND r.Status IN ('Approved', 'Processed');
    """, (booking_id,))
    total_refunded = cursor.fetchone()["Total_Refunded"]
    conn.close()
    
    max_refundable = max(0.0, total_paid - total_refunded)
    if requested_amount > max_refundable:
        return (
            False,
            total_paid,
            total_refunded,
            max_refundable,
            f"Financial Integrity Violation: Requested refund of ${requested_amount:,.2f} exceeds remaining refundable payments (${max_refundable:,.2f}). Total Paid: ${total_paid:,.2f}, Already Refunded: ${total_refunded:,.2f}."
        )
    return (True, total_paid, total_refunded, max_refundable, "")

# ============================================================================
# TRANSACTIONAL DATA OPERATIONS
# ============================================================================

def create_booking_with_travellers(cust_id: int, depart_id: int, booking_date: str, travellers_data: list):
    """
    Atomically creates a booking and records travellers.
    Validates capacity control prior to insertion inside an ACID transaction.
    travellers_data: list of dicts [{'name': '...', 'age': 30}, ...]
    """
    num_travellers = len(travellers_data)
    if num_travellers == 0:
        return (False, "At least one traveller must be registered for a booking.", None)
        
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Capacity lock check
        cursor.execute("SELECT d.Max_Capacity, p.Base_Price, d.Status FROM Departure d JOIN Package p ON d.Package_ID = p.Package_ID WHERE d.Depart_ID = ?;", (depart_id,))
        depart_row = cursor.fetchone()
        if not depart_row:
            return (False, "Departure not found.", None)
            
        if depart_row["Status"] == "Cancelled":
            return (False, "Cannot book a cancelled departure.", None)
            
        max_cap = depart_row["Max_Capacity"]
        base_price = depart_row["Base_Price"]
        
        cursor.execute("""
            SELECT COUNT(t.Traveller_ID) as Booked
            FROM Traveller t
            JOIN Booking b ON t.Booking_ID = b.Booking_ID
            WHERE b.Depart_ID = ? AND b.Status != 'Cancelled';
        """, (depart_id,))
        current_booked = cursor.fetchone()["Booked"]
        
        available = max_cap - current_booked
        if current_booked + num_travellers > max_cap:
            return (False, f"Capacity limit exceeded! Only {available} seat(s) available on this departure.", None)
            
        total_amount = base_price * num_travellers
        
        # 2. Insert Booking
        cursor.execute("""
            INSERT INTO Booking (Cust_ID, Depart_ID, Booking_Date, Total_Amount, Status)
            VALUES (?, ?, ?, ?, 'Confirmed');
        """, (cust_id, depart_id, booking_date, total_amount))
        booking_id = cursor.lastrowid
        
        # 3. Insert Travellers
        for t in travellers_data:
            cursor.execute("""
                INSERT INTO Traveller (Booking_ID, Name, Age)
                VALUES (?, ?, ?);
            """, (booking_id, t["name"], int(t["age"])))
            
        conn.commit()
        return (True, f"Booking #{booking_id} successfully confirmed for {num_travellers} traveller(s)! Total: ${total_amount:,.2f}", booking_id)
    except Exception as e:
        conn.rollback()
        return (False, f"Database transaction failed: {str(e)}", None)
    finally:
        conn.close()

def record_payment(booking_id: int, amount: float, payment_date: str):
    """Records a payment for a booking with validation."""
    if amount <= 0:
        return (False, "Payment amount must be greater than zero.")
        
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Total_Amount, Status FROM Booking WHERE Booking_ID = ?;", (booking_id,))
        b_row = cursor.fetchone()
        if not b_row:
            return (False, "Booking not found.")
            
        cursor.execute("SELECT COALESCE(SUM(Amount), 0.0) as Paid FROM Payment WHERE Booking_ID = ?;", (booking_id,))
        paid_so_far = cursor.fetchone()["Paid"]
        
        cursor.execute("""
            INSERT INTO Payment (Booking_ID, Amount, Payment_Date)
            VALUES (?, ?, ?);
        """, (booking_id, amount, payment_date))
        
        # If fully paid and was pending, mark confirmed
        if (paid_so_far + amount) >= b_row["Total_Amount"] and b_row["Status"] == "Pending Payment":
            cursor.execute("UPDATE Booking SET Status = 'Confirmed' WHERE Booking_ID = ?;", (booking_id,))
            
        conn.commit()
        return (True, f"Payment of ${amount:,.2f} recorded successfully.")
    except Exception as e:
        conn.rollback()
        return (False, f"Payment failed: {str(e)}")
    finally:
        conn.close()

def cancel_booking_and_request_refund(booking_id: int, cancel_date: str, reason: str, refund_amount: float = None):
    """
    Cancels a booking and creates a Cancellation and Refund record adhering to financial integrity.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Status, Total_Amount FROM Booking WHERE Booking_ID = ?;", (booking_id,))
        b_row = cursor.fetchone()
        if not b_row:
            return (False, "Booking not found.")
        if b_row["Status"] == "Cancelled":
            return (False, "Booking is already cancelled.")
            
        # Check total payments made
        cursor.execute("SELECT COALESCE(SUM(Amount), 0.0) as Paid FROM Payment WHERE Booking_ID = ?;", (booking_id,))
        total_paid = cursor.fetchone()["Paid"]
        
        if refund_amount is None:
            # Default refund is total paid
            refund_amount = total_paid
            
        if refund_amount > total_paid:
            return (False, f"Financial Integrity Error: Refund amount (${refund_amount:,.2f}) cannot exceed total paid (${total_paid:,.2f}).")
            
        # 1. Update booking status
        cursor.execute("UPDATE Booking SET Status = 'Cancelled' WHERE Booking_ID = ?;", (booking_id,))
        
        # 2. Insert Cancellation
        cursor.execute("""
            INSERT INTO Cancellation (Booking_ID, Cancel_Date, Reason)
            VALUES (?, ?, ?);
        """, (booking_id, cancel_date, reason))
        cancel_id = cursor.lastrowid
        
        # 3. Insert Refund record if paid > 0 or requested > 0
        refund_id = None
        if refund_amount > 0:
            cursor.execute("""
                INSERT INTO Refund (Cancel_ID, Amount, Status)
                VALUES (?, ?, 'Requested');
            """, (cancel_id, refund_amount))
            refund_id = cursor.lastrowid
            
        conn.commit()
        msg = f"Booking #{booking_id} cancelled successfully."
        if refund_id:
            msg += f" Refund #{refund_id} for ${refund_amount:,.2f} has been submitted for approval."
        return (True, msg)
    except Exception as e:
        conn.rollback()
        return (False, f"Cancellation failed: {str(e)}")
    finally:
        conn.close()

def schedule_departure(package_id: int, guide_id: int, transport_id: int, start_date: str, end_date: str, max_capacity: int, status="Scheduled"):
    """
    Schedules a new departure after performing guide & transport conflict checks.
    """
    # 1. Date validity
    if end_date < start_date:
        return (False, "End Date cannot be earlier than Start Date.")
        
    # 2. Transport capacity validation
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Capacity, Type FROM Transport WHERE Transport_ID = ?;", (transport_id,))
    t_row = cursor.fetchone()
    if not t_row:
        conn.close()
        return (False, "Selected transport asset does not exist.")
    if max_capacity > t_row["Capacity"]:
        conn.close()
        return (False, f"Departure Max Capacity ({max_capacity}) exceeds vehicle '{t_row['Type']}' limit ({t_row['Capacity']} passengers).")
    conn.close()
    
    # 3. Guide conflict check
    has_g_conflict, g_conflicts = check_guide_conflict(guide_id, start_date, end_date)
    if has_g_conflict:
        c = g_conflicts[0]
        return (False, f"Guide Conflict! {c['Guide_Name']} is already booked on Departure #{c['Depart_ID']} ({c['Package_Name']}) from {c['Start_Date']} to {c['End_Date']}.")
        
    # 4. Transport conflict check
    has_t_conflict, t_conflicts = check_transport_conflict(transport_id, start_date, end_date)
    if has_t_conflict:
        c = t_conflicts[0]
        return (False, f"Transport Conflict! Vehicle {c['Transport_Type']} is already in service on Departure #{c['Depart_ID']} ({c['Package_Name']}) from {c['Start_Date']} to {c['End_Date']}.")
        
    # 5. Insert Departure
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Departure (Package_ID, Guide_ID, Transport_ID, Start_Date, End_Date, Max_Capacity, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (package_id, guide_id, transport_id, start_date, end_date, max_capacity, status))
        depart_id = cursor.lastrowid
        conn.commit()
        return (True, f"Departure #{depart_id} successfully scheduled from {start_date} to {end_date}!")
    except Exception as e:
        conn.rollback()
        return (False, f"Failed to schedule departure: {str(e)}")
    finally:
        conn.close()

def update_refund_status(refund_id: int, new_status: str):
    """Admin tool to approve, process, or reject a refund."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Verify financial integrity if approving or processing
        if new_status in ("Approved", "Processed"):
            cursor.execute("""
                SELECT r.Amount, c.Booking_ID
                FROM Refund r
                JOIN Cancellation c ON r.Cancel_ID = c.Cancel_ID
                WHERE r.Refund_ID = ?;
            """, (refund_id,))
            row = cursor.fetchone()
            if row:
                b_id = row["Booking_ID"]
                req_amt = row["Amount"]
                
                cursor.execute("SELECT COALESCE(SUM(Amount), 0.0) as Paid FROM Payment WHERE Booking_ID = ?;", (b_id,))
                total_paid = cursor.fetchone()["Paid"]
                
                cursor.execute("""
                    SELECT COALESCE(SUM(Amount), 0.0) as Other_Refunds
                    FROM Refund r2
                    JOIN Cancellation c2 ON r2.Cancel_ID = c2.Cancel_ID
                    WHERE c2.Booking_ID = ? AND r2.Refund_ID != ? AND r2.Status IN ('Approved', 'Processed');
                """, (b_id, refund_id))
                other_refunds = cursor.fetchone()["Other_Refunds"]
                
                if (other_refunds + req_amt) > total_paid:
                    conn.close()
                    return (False, f"Financial rule violation: Approved refunds (${other_refunds + req_amt:,.2f}) would exceed payments (${total_paid:,.2f}).")
                    
        cursor.execute("UPDATE Refund SET Status = ? WHERE Refund_ID = ?;", (new_status, refund_id))
        conn.commit()
        return (True, f"Refund #{refund_id} updated to '{new_status}'.")
    except Exception as e:
        conn.rollback()
        return (False, f"Update failed: {str(e)}")
    finally:
        conn.close()

# ============================================================================
# QUERY & REPORT HELPERS
# ============================================================================

def get_all_destinations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Destination ORDER BY Name;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_packages():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, d.Name as Dest_Name, d.Country
        FROM Package p
        JOIN Destination d ON p.Dest_ID = d.Dest_ID
        ORDER BY p.Package_ID;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_package_details(package_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, d.Name as Dest_Name, d.Country, d.Description as Dest_Description
        FROM Package p
        JOIN Destination d ON p.Dest_ID = d.Dest_ID
        WHERE p.Package_ID = ?;
    """, (package_id,))
    pkg = cursor.fetchone()
    if not pkg:
        conn.close()
        return None
    pkg_dict = dict(pkg)
    
    cursor.execute("SELECT * FROM Itinerary_Day WHERE Package_ID = ? ORDER BY Day_Number;", (package_id,))
    pkg_dict["itinerary"] = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM Hotel WHERE Dest_ID = ? ORDER BY Star_Rating DESC;", (pkg_dict["Dest_ID"],))
    pkg_dict["hotels"] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return pkg_dict

def get_all_departures(filter_package_id=None, status_filter=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT d.*, p.Name as Package_Name, p.Base_Price, p.Duration_Days,
               dest.Name as Dest_Name, dest.Country,
               g.Name as Guide_Name, g.Language as Guide_Language, g.Contact as Guide_Contact,
               t.Type as Transport_Type, t.Capacity as Transport_Capacity,
               (
                   SELECT COUNT(tr.Traveller_ID)
                   FROM Traveller tr
                   JOIN Booking b ON tr.Booking_ID = b.Booking_ID
                   WHERE b.Depart_ID = d.Depart_ID AND b.Status != 'Cancelled'
               ) as Booked_Seats
        FROM Departure d
        JOIN Package p ON d.Package_ID = p.Package_ID
        JOIN Destination dest ON p.Dest_ID = dest.Dest_ID
        JOIN Guide g ON d.Guide_ID = g.Guide_ID
        JOIN Transport t ON d.Transport_ID = t.Transport_ID
        WHERE 1=1
    """
    params = []
    if filter_package_id:
        query += " AND d.Package_ID = ?"
        params.append(filter_package_id)
    if status_filter:
        query += " AND d.Status = ?"
        params.append(status_filter)
        
    query += " ORDER BY d.Start_Date ASC;"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        d["Available_Seats"] = max(0, d["Max_Capacity"] - d["Booked_Seats"])
        result.append(d)
    return result

def get_customer_bookings(cust_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, d.Start_Date, d.End_Date, d.Status as Depart_Status,
               p.Name as Package_Name, dest.Name as Dest_Name, dest.Country,
               g.Name as Guide_Name, g.Contact as Guide_Contact,
               COALESCE((SELECT SUM(Amount) FROM Payment WHERE Booking_ID = b.Booking_ID), 0.0) as Total_Paid,
               c.Cancel_Date, c.Reason as Cancel_Reason,
               r.Refund_ID, r.Amount as Refund_Amount, r.Status as Refund_Status
        FROM Booking b
        JOIN Departure d ON b.Depart_ID = d.Depart_ID
        JOIN Package p ON d.Package_ID = p.Package_ID
        JOIN Destination dest ON p.Dest_ID = dest.Dest_ID
        JOIN Guide g ON d.Guide_ID = g.Guide_ID
        LEFT JOIN Cancellation c ON b.Booking_ID = c.Booking_ID
        LEFT JOIN Refund r ON c.Cancel_ID = r.Cancel_ID
        WHERE b.Cust_ID = ?
        ORDER BY b.Booking_ID DESC;
    """, (cust_id,))
    rows = cursor.fetchall()
    
    bookings_list = []
    for row in rows:
        b_dict = dict(row)
        cursor.execute("SELECT * FROM Traveller WHERE Booking_ID = ?;", (b_dict["Booking_ID"],))
        b_dict["travellers"] = [dict(t) for t in cursor.fetchall()]
        cursor.execute("SELECT * FROM Payment WHERE Booking_ID = ? ORDER BY Payment_Date;", (b_dict["Booking_ID"],))
        b_dict["payments"] = [dict(p) for p in cursor.fetchall()]
        bookings_list.append(b_dict)
        
    conn.close()
    return bookings_list

def get_guide_roster(guide_id: int):
    """Returns departures and full passenger manifests assigned to a guide."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.*, p.Name as Package_Name, p.Package_ID, dest.Name as Dest_Name,
               t.Type as Transport_Type, t.Capacity as Transport_Capacity,
               (
                   SELECT COUNT(tr.Traveller_ID)
                   FROM Traveller tr
                   JOIN Booking b ON tr.Booking_ID = b.Booking_ID
                   WHERE b.Depart_ID = d.Depart_ID AND b.Status != 'Cancelled'
               ) as Booked_Seats
        FROM Departure d
        JOIN Package p ON d.Package_ID = p.Package_ID
        JOIN Destination dest ON p.Dest_ID = dest.Dest_ID
        JOIN Transport t ON d.Transport_ID = t.Transport_ID
        WHERE d.Guide_ID = ?
        ORDER BY d.Start_Date ASC;
    """, (guide_id,))
    departures = [dict(r) for r in cursor.fetchall()]
    
    for dep in departures:
        dep["Available_Seats"] = max(0, dep["Max_Capacity"] - dep["Booked_Seats"])
        # Fetch itinerary
        cursor.execute("SELECT Day_Number, Activity FROM Itinerary_Day WHERE Package_ID = ? ORDER BY Day_Number;", (dep["Package_ID"],))
        dep["itinerary"] = [dict(i) for i in cursor.fetchall()]
        
        # Fetch traveller manifest
        cursor.execute("""
            SELECT tr.Traveller_ID, tr.Name as Traveller_Name, tr.Age,
                   b.Booking_ID, c.Name as Lead_Customer, c.Email as Contact_Email
            FROM Traveller tr
            JOIN Booking b ON tr.Booking_ID = b.Booking_ID
            JOIN Customer c ON b.Cust_ID = c.Cust_ID
            WHERE b.Depart_ID = ? AND b.Status != 'Cancelled'
            ORDER BY tr.Traveller_ID ASC;
        """, (dep["Depart_ID"],))
        dep["manifest"] = [dict(m) for m in cursor.fetchall()]
        
    conn.close()
    return departures

def get_kpi_summary():
    """Generates overall DBMS metrics for the Administrator dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Booking;")
    total_bookings = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Booking WHERE Status = 'Confirmed';")
    active_bookings = cursor.fetchone()[0]
    
    cursor.execute("SELECT COALESCE(SUM(Amount), 0.0) FROM Payment;")
    gross_revenue = cursor.fetchone()[0]
    
    cursor.execute("SELECT COALESCE(SUM(Amount), 0.0) FROM Refund WHERE Status IN ('Approved', 'Processed');")
    total_refunds = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Departure WHERE Status IN ('Scheduled', 'In Progress');")
    active_departures = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Traveller;")
    total_travellers = cursor.fetchone()[0]
    
    # Capacity stats
    cursor.execute("""
        SELECT SUM(d.Max_Capacity) as Total_Cap,
               (SELECT COUNT(t.Traveller_ID) FROM Traveller t JOIN Booking b ON t.Booking_ID = b.Booking_ID JOIN Departure d2 ON b.Depart_ID = d2.Depart_ID WHERE d2.Status IN ('Scheduled', 'In Progress') AND b.Status != 'Cancelled') as Filled_Seats
        FROM Departure d
        WHERE d.Status IN ('Scheduled', 'In Progress');
    """)
    cap_row = cursor.fetchone()
    total_cap = cap_row["Total_Cap"] or 1
    filled_seats = cap_row["Filled_Seats"] or 0
    utilization = (filled_seats / total_cap * 100) if total_cap > 0 else 0
    
    conn.close()
    return {
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "gross_revenue": gross_revenue,
        "net_revenue": gross_revenue - total_refunds,
        "total_refunds": total_refunds,
        "active_departures": active_departures,
        "total_travellers": total_travellers,
        "utilization_pct": round(utilization, 1)
    }

def add_destination(name: str, country: str, description: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Destination (Name, Country, Description) VALUES (?, ?, ?);", (name.strip(), country.strip(), description.strip()))
        conn.commit()
        return (True, f"Destination '{name}' created successfully with ID #{cursor.lastrowid}.")
    except Exception as e:
        conn.rollback()
        return (False, f"Error creating destination: {str(e)}")
    finally:
        conn.close()

def add_package(dest_id: int, name: str, duration_days: int, base_price: float):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Package (Dest_ID, Name, Duration_Days, Base_Price) VALUES (?, ?, ?, ?);", (dest_id, name.strip(), duration_days, base_price))
        conn.commit()
        return (True, f"Package '{name}' created successfully with ID #{cursor.lastrowid}.")
    except Exception as e:
        conn.rollback()
        return (False, f"Error creating package: {str(e)}")
    finally:
        conn.close()

def add_itinerary_day(package_id: int, day_number: int, activity: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Itinerary_Day (Package_ID, Day_Number, Activity) VALUES (?, ?, ?);", (package_id, day_number, activity.strip()))
        conn.commit()
        return (True, f"Day {day_number} added to Package #{package_id}.")
    except Exception as e:
        conn.rollback()
        return (False, f"Error adding itinerary day: {str(e)}")
    finally:
        conn.close()

def add_hotel(dest_id: int, name: str, star_rating: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Hotel (Dest_ID, Name, Star_Rating) VALUES (?, ?, ?);", (dest_id, name.strip(), star_rating))
        conn.commit()
        return (True, f"Hotel '{name}' ({star_rating}★) added successfully.")
    except Exception as e:
        conn.rollback()
        return (False, f"Error adding hotel: {str(e)}")
    finally:
        conn.close()

def add_transport(transport_type: str, capacity: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Transport (Type, Capacity) VALUES (?, ?);", (transport_type.strip(), capacity))
        conn.commit()
        return (True, f"Transport asset '{transport_type}' (Capacity: {capacity}) added successfully.")
    except Exception as e:
        conn.rollback()
        return (False, f"Error adding transport: {str(e)}")
    finally:
        conn.close()

def add_guide(name: str, contact: str, language: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Guide (Name, Contact, Language) VALUES (?, ?, ?);", (name.strip(), contact.strip(), language.strip()))
        conn.commit()
        return (True, f"Tour Guide '{name}' added successfully.")
    except Exception as e:
        conn.rollback()
        return (False, f"Error adding guide: {str(e)}")
    finally:
        conn.close()

def add_customer(name: str, email: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Customer (Name, Email) VALUES (?, ?);", (name.strip(), email.strip().lower()))
        conn.commit()
        return (True, cursor.lastrowid, f"Customer profile created for {name}.")
    except Exception as e:
        conn.rollback()
        return (False, None, f"Error creating customer: {str(e)}")
    finally:
        conn.close()

def get_all_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customer ORDER BY Name;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_guides():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Guide ORDER BY Name;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_transports():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Transport ORDER BY Capacity DESC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_hotels():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.*, d.Name as Dest_Name
        FROM Hotel h
        JOIN Destination d ON h.Dest_ID = d.Dest_ID
        ORDER BY d.Name, h.Star_Rating DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_departure_status(depart_id: int, new_status: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Departure SET Status = ? WHERE Depart_ID = ?;", (new_status, depart_id))
        conn.commit()
        return (True, f"Departure #{depart_id} status updated to '{new_status}'.")
    except Exception as e:
        conn.rollback()
        return (False, f"Update failed: {str(e)}")
    finally:
        conn.close()

def get_all_bookings_admin():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.Booking_ID, b.Booking_Date, b.Total_Amount, b.Status as Booking_Status,
               c.Cust_ID, c.Name as Customer_Name, c.Email as Customer_Email,
               d.Depart_ID, d.Start_Date, d.End_Date, d.Status as Depart_Status,
               p.Name as Package_Name, dest.Name as Dest_Name,
               (SELECT COUNT(*) FROM Traveller t WHERE t.Booking_ID = b.Booking_ID) as Traveller_Count,
               COALESCE((SELECT SUM(pm.Amount) FROM Payment pm WHERE pm.Booking_ID = b.Booking_ID), 0.0) as Paid_Amount
        FROM Booking b
        JOIN Customer c ON b.Cust_ID = c.Cust_ID
        JOIN Departure d ON b.Depart_ID = d.Depart_ID
        JOIN Package p ON d.Package_ID = p.Package_ID
        JOIN Destination dest ON p.Dest_ID = dest.Dest_ID
        ORDER BY b.Booking_ID DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_refunds_admin():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.Refund_ID, r.Amount as Refund_Amount, r.Status as Refund_Status,
               c.Cancel_ID, c.Cancel_Date, c.Reason as Cancel_Reason,
               b.Booking_ID, b.Total_Amount as Booking_Total,
               cust.Name as Customer_Name, cust.Email as Customer_Email,
               p.Name as Package_Name,
               COALESCE((SELECT SUM(pm.Amount) FROM Payment pm WHERE pm.Booking_ID = b.Booking_ID), 0.0) as Paid_Amount
        FROM Refund r
        JOIN Cancellation c ON r.Cancel_ID = c.Cancel_ID
        JOIN Booking b ON c.Booking_ID = b.Booking_ID
        JOIN Customer cust ON b.Cust_ID = cust.Cust_ID
        JOIN Departure d ON b.Depart_ID = d.Depart_ID
        JOIN Package p ON d.Package_ID = p.Package_ID
        ORDER BY r.Refund_ID DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_schema_tables_info():
    """Returns table names and their column definitions for the live schema viewer."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    tables = [r[0] for r in cursor.fetchall()]
    
    info = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        cols = [dict(c) for c in cursor.fetchall()]
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fks = [dict(fk) for fk in cursor.fetchall()]
        info[table] = {
            "columns": cols,
            "row_count": count,
            "foreign_keys": fks
        }
    conn.close()
    return info

def run_raw_sql(query: str):
    """Executes a read-only or authorized query and returns columns and rows."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        if cursor.description:
            cols = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            conn.close()
            return (True, cols, [list(r) for r in rows], f"Query executed successfully ({len(rows)} row(s) returned).")
        else:
            conn.commit()
            conn.close()
            return (True, [], [], "Query executed successfully (no result set returned).")
    except Exception as e:
        conn.close()
        return (False, [], [], f"SQL Error: {str(e)}")

