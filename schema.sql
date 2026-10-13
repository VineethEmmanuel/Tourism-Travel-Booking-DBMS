-- ============================================================================
-- TOURISM PACKAGE & TRAVEL BOOKING DBMS
-- Relational Schema adhering strictly to Third Normal Form (3NF)
-- Database Engine: SQLite 3
-- ============================================================================

PRAGMA foreign_keys = ON;

-- 1. Destination
CREATE TABLE IF NOT EXISTS Destination (
    Dest_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL UNIQUE,
    Country TEXT NOT NULL,
    Description TEXT NOT NULL
);

-- 2. Package
CREATE TABLE IF NOT EXISTS Package (
    Package_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Dest_ID INTEGER NOT NULL,
    Name TEXT NOT NULL,
    Duration_Days INTEGER NOT NULL CHECK(Duration_Days > 0),
    Base_Price REAL NOT NULL CHECK(Base_Price >= 0),
    FOREIGN KEY (Dest_ID) REFERENCES Destination(Dest_ID) ON DELETE RESTRICT
);

-- 3. Itinerary_Day
CREATE TABLE IF NOT EXISTS Itinerary_Day (
    Itin_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Package_ID INTEGER NOT NULL,
    Day_Number INTEGER NOT NULL CHECK(Day_Number > 0),
    Activity TEXT NOT NULL,
    FOREIGN KEY (Package_ID) REFERENCES Package(Package_ID) ON DELETE CASCADE,
    UNIQUE(Package_ID, Day_Number)
);

-- 4. Guide
CREATE TABLE IF NOT EXISTS Guide (
    Guide_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Contact TEXT NOT NULL,
    Language TEXT NOT NULL
);

-- 5. Hotel
CREATE TABLE IF NOT EXISTS Hotel (
    Hotel_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Dest_ID INTEGER NOT NULL,
    Name TEXT NOT NULL,
    Star_Rating INTEGER NOT NULL CHECK(Star_Rating BETWEEN 1 AND 5),
    FOREIGN KEY (Dest_ID) REFERENCES Destination(Dest_ID) ON DELETE RESTRICT
);

-- 6. Transport
CREATE TABLE IF NOT EXISTS Transport (
    Transport_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Type TEXT NOT NULL,
    Capacity INTEGER NOT NULL CHECK(Capacity > 0)
);

-- 7. Departure
CREATE TABLE IF NOT EXISTS Departure (
    Depart_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Package_ID INTEGER NOT NULL,
    Guide_ID INTEGER NOT NULL,
    Transport_ID INTEGER NOT NULL,
    Start_Date TEXT NOT NULL, -- ISO-8601 YYYY-MM-DD
    End_Date TEXT NOT NULL,   -- ISO-8601 YYYY-MM-DD
    Max_Capacity INTEGER NOT NULL CHECK(Max_Capacity > 0),
    Status TEXT NOT NULL CHECK(Status IN ('Scheduled', 'In Progress', 'Completed', 'Cancelled')),
    FOREIGN KEY (Package_ID) REFERENCES Package(Package_ID) ON DELETE RESTRICT,
    FOREIGN KEY (Guide_ID) REFERENCES Guide(Guide_ID) ON DELETE RESTRICT,
    FOREIGN KEY (Transport_ID) REFERENCES Transport(Transport_ID) ON DELETE RESTRICT,
    CHECK(End_Date >= Start_Date)
);

-- 8. Customer
CREATE TABLE IF NOT EXISTS Customer (
    Cust_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE
);

-- 9. Booking
CREATE TABLE IF NOT EXISTS Booking (
    Booking_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Cust_ID INTEGER NOT NULL,
    Depart_ID INTEGER NOT NULL,
    Booking_Date TEXT NOT NULL, -- ISO-8601 YYYY-MM-DD
    Total_Amount REAL NOT NULL CHECK(Total_Amount >= 0),
    Status TEXT NOT NULL CHECK(Status IN ('Confirmed', 'Pending Payment', 'Completed', 'Cancelled')),
    FOREIGN KEY (Cust_ID) REFERENCES Customer(Cust_ID) ON DELETE RESTRICT,
    FOREIGN KEY (Depart_ID) REFERENCES Departure(Depart_ID) ON DELETE RESTRICT
);

-- 10. Traveller
CREATE TABLE IF NOT EXISTS Traveller (
    Traveller_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Booking_ID INTEGER NOT NULL,
    Name TEXT NOT NULL,
    Age INTEGER NOT NULL CHECK(Age >= 0),
    FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID) ON DELETE CASCADE
);

-- 11. Payment
CREATE TABLE IF NOT EXISTS Payment (
    Payment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Booking_ID INTEGER NOT NULL,
    Amount REAL NOT NULL CHECK(Amount > 0),
    Payment_Date TEXT NOT NULL, -- ISO-8601 YYYY-MM-DD
    FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID) ON DELETE RESTRICT
);

-- 12. Cancellation
CREATE TABLE IF NOT EXISTS Cancellation (
    Cancel_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Booking_ID INTEGER NOT NULL UNIQUE,
    Cancel_Date TEXT NOT NULL, -- ISO-8601 YYYY-MM-DD
    Reason TEXT NOT NULL,
    FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID) ON DELETE RESTRICT
);

-- 13. Refund
CREATE TABLE IF NOT EXISTS Refund (
    Refund_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Cancel_ID INTEGER NOT NULL,
    Amount REAL NOT NULL CHECK(Amount >= 0),
    Status TEXT NOT NULL CHECK(Status IN ('Requested', 'Approved', 'Processed', 'Rejected')),
    FOREIGN KEY (Cancel_ID) REFERENCES Cancellation(Cancel_ID) ON DELETE RESTRICT
);

-- Indexes for join speed & date range conflict lookups
CREATE INDEX IF NOT EXISTS idx_departure_schedule ON Departure (Guide_ID, Transport_ID, Start_Date, End_Date);
CREATE INDEX IF NOT EXISTS idx_booking_cust ON Booking (Cust_ID);
CREATE INDEX IF NOT EXISTS idx_booking_depart ON Booking (Depart_ID);
CREATE INDEX IF NOT EXISTS idx_traveller_booking ON Traveller (Booking_ID);
CREATE INDEX IF NOT EXISTS idx_payment_booking ON Payment (Booking_ID);
CREATE INDEX IF NOT EXISTS idx_cancellation_booking ON Cancellation (Booking_ID);
CREATE INDEX IF NOT EXISTS idx_refund_cancellation ON Refund (Cancel_ID);
