"""
Vehicle Management System
=========================
A console-based project to manage members, vehicles and vehicle rentals.

Features:
  1. Add a new member
  2. Add a new vehicle
  3. View all members
  4. View all vehicles (with availability)
  5. Rent a vehicle to a member
  6. Return a rented vehicle (rent is calculated automatically)
  7. View rental records (history)

Technology used:
  - Python 3 (no external libraries needed)
  - sqlite3 (built into Python) to store data permanently in a file
  - datetime (built into Python) to work with rental dates

How to run in VS Code:
  Open this file and press the "Run" button, or type in the terminal:
      python vehicle_management.py
"""

import sqlite3                 # Database module: stores our records permanently
from datetime import date      # Used to get today's date for rentals

DB_FILE = "vehicle_management.db"   # The database file created automatically


# ----------------------------------------------------------------------
# DATABASE SETUP
# ----------------------------------------------------------------------
def connect_db():
    """Connect to the database file and create the tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row      # lets us access columns by name
    cur = conn.cursor()

    # Table 1: members (people who can rent vehicles)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            phone     TEXT NOT NULL,
            license_no TEXT NOT NULL
        )""")

    # Table 2: vehicles (available = 1 means free, 0 means currently rented)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_number   TEXT NOT NULL UNIQUE,
            vehicle_type TEXT NOT NULL,
            model        TEXT NOT NULL,
            daily_rate   REAL NOT NULL,
            available    INTEGER NOT NULL DEFAULT 1
        )""")

    # Table 3: rentals (links a member to a vehicle for some dates)
    # return_date stays NULL until the vehicle is returned.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rentals (
            rental_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id   INTEGER NOT NULL,
            vehicle_id  INTEGER NOT NULL,
            rent_date   TEXT NOT NULL,
            return_date TEXT,
            total_cost  REAL,
            FOREIGN KEY (member_id)  REFERENCES members(member_id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
        )""")
    conn.commit()
    return conn


# ----------------------------------------------------------------------
# HELPER FUNCTIONS FOR SAFE INPUT
# ----------------------------------------------------------------------
def ask_text(prompt):
    """Keep asking until the user types something (not empty)."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  Input cannot be empty. Try again.")


def ask_number(prompt, as_float=False):
    """Keep asking until the user types a valid positive number."""
    while True:
        try:
            value = float(input(prompt)) if as_float else int(input(prompt))
            if value > 0:
                return value
            print("  Please enter a number greater than 0.")
        except ValueError:
            print("  That is not a valid number. Try again.")


# ----------------------------------------------------------------------
# MEMBER FUNCTIONS
# ----------------------------------------------------------------------
def add_member(conn):
    """Feature 1: Add a new member to the database."""
    print("\n--- Add New Member ---")
    name = ask_text("Name: ")
    phone = ask_text("Phone: ")
    license_no = ask_text("Driving licence number: ")

    # '?' placeholders protect against SQL injection
    conn.execute("INSERT INTO members (name, phone, license_no) VALUES (?, ?, ?)",
                 (name, phone, license_no))
    conn.commit()
    print(f"Member '{name}' added successfully.")


def view_members(conn):
    """Feature 3: Show all members in a table."""
    print("\n--- All Members ---")
    rows = conn.execute("SELECT * FROM members").fetchall()
    if not rows:
        print("No members found.")
        return
    print(f"{'ID':<5}{'Name':<20}{'Phone':<15}{'Licence No':<15}")
    for r in rows:
        print(f"{r['member_id']:<5}{r['name']:<20}{r['phone']:<15}{r['license_no']:<15}")


# ----------------------------------------------------------------------
# VEHICLE FUNCTIONS
# ----------------------------------------------------------------------
def add_vehicle(conn):
    """Feature 2: Add a new vehicle to the fleet."""
    print("\n--- Add New Vehicle ---")
    reg = ask_text("Registration number (e.g. TS09AB1234): ").upper()
    vtype = ask_text("Type (Car / Bike / Truck / Van): ").title()
    model = ask_text("Model (e.g. Honda City): ")
    rate = ask_number("Rent per day: ", as_float=True)

    try:
        conn.execute(
            "INSERT INTO vehicles (reg_number, vehicle_type, model, daily_rate) "
            "VALUES (?, ?, ?, ?)", (reg, vtype, model, rate))
        conn.commit()
        print(f"Vehicle '{reg}' added successfully.")
    except sqlite3.IntegrityError:
        # reg_number is UNIQUE, so a duplicate raises this error
        print("A vehicle with this registration number already exists.")


def view_vehicles(conn):
    """Feature 4: Show all vehicles and whether they are available."""
    print("\n--- All Vehicles ---")
    rows = conn.execute("SELECT * FROM vehicles").fetchall()
    if not rows:
        print("No vehicles found.")
        return
    print(f"{'ID':<5}{'Reg No':<14}{'Type':<8}{'Model':<18}{'Rate/Day':<10}{'Status'}")
    for r in rows:
        status = "Available" if r["available"] else "Rented"
        print(f"{r['vehicle_id']:<5}{r['reg_number']:<14}{r['vehicle_type']:<8}"
              f"{r['model']:<18}{r['daily_rate']:<10.2f}{status}")


# ----------------------------------------------------------------------
# RENTAL FUNCTIONS
# ----------------------------------------------------------------------
def rent_vehicle(conn):
    """Feature 5: Rent an available vehicle to a member."""
    print("\n--- Rent a Vehicle ---")
    member_id = ask_number("Enter member ID: ")
    member = conn.execute("SELECT * FROM members WHERE member_id = ?",
                          (member_id,)).fetchone()
    if member is None:
        print("Member not found. Add the member first.")
        return

    # Show only vehicles that are free
    free = conn.execute("SELECT * FROM vehicles WHERE available = 1").fetchall()
    if not free:
        print("Sorry, no vehicles are available right now.")
        return
    print("Available vehicles:")
    for v in free:
        print(f"  ID {v['vehicle_id']}: {v['reg_number']} - {v['model']} "
              f"({v['vehicle_type']}) @ {v['daily_rate']:.2f}/day")

    vehicle_id = ask_number("Enter vehicle ID to rent: ")
    vehicle = conn.execute(
        "SELECT * FROM vehicles WHERE vehicle_id = ? AND available = 1",
        (vehicle_id,)).fetchone()
    if vehicle is None:
        print("Invalid choice or the vehicle is not available.")
        return

    # Save the rental with today's date and mark the vehicle as rented
    today = date.today().isoformat()          # format: YYYY-MM-DD
    conn.execute("INSERT INTO rentals (member_id, vehicle_id, rent_date) "
                 "VALUES (?, ?, ?)", (member_id, vehicle_id, today))
    conn.execute("UPDATE vehicles SET available = 0 WHERE vehicle_id = ?",
                 (vehicle_id,))
    conn.commit()
    print(f"{vehicle['model']} rented to {member['name']} on {today}.")


def return_vehicle(conn):
    """Feature 6: Return a vehicle and calculate the total rent."""
    print("\n--- Return a Vehicle ---")

    # Find all rentals that are still open (return_date is empty)
    active = conn.execute("""
        SELECT r.rental_id, r.rent_date, m.name, v.vehicle_id,
               v.reg_number, v.model, v.daily_rate
        FROM rentals r
        JOIN members  m ON m.member_id  = r.member_id
        JOIN vehicles v ON v.vehicle_id = r.vehicle_id
        WHERE r.return_date IS NULL""").fetchall()
    if not active:
        print("No vehicles are currently rented out.")
        return
    for a in active:
        print(f"  Rental {a['rental_id']}: {a['reg_number']} ({a['model']}) "
              f"- {a['name']} since {a['rent_date']}")

    rental_id = ask_number("Enter rental ID to return: ")
    rental = next((a for a in active if a["rental_id"] == rental_id), None)
    if rental is None:
        print("Invalid rental ID.")
        return

    # Number of days = today - rent date (minimum 1 day is charged)
    start = date.fromisoformat(rental["rent_date"])
    days = max(1, (date.today() - start).days)
    total = days * rental["daily_rate"]

    conn.execute("UPDATE rentals SET return_date = ?, total_cost = ? "
                 "WHERE rental_id = ?",
                 (date.today().isoformat(), total, rental_id))
    conn.execute("UPDATE vehicles SET available = 1 WHERE vehicle_id = ?",
                 (rental["vehicle_id"],))
    conn.commit()
    print(f"Vehicle returned. Days: {days}, Total rent: {total:.2f}")


def view_rentals(conn):
    """Feature 7: Show the complete rental history."""
    print("\n--- Rental Records ---")
    rows = conn.execute("""
        SELECT r.rental_id, m.name, v.reg_number, r.rent_date,
               r.return_date, r.total_cost
        FROM rentals r
        JOIN members  m ON m.member_id  = r.member_id
        JOIN vehicles v ON v.vehicle_id = r.vehicle_id
        ORDER BY r.rental_id""").fetchall()
    if not rows:
        print("No rental records yet.")
        return
    print(f"{'ID':<5}{'Member':<18}{'Vehicle':<14}{'Rented':<12}{'Returned':<12}{'Cost'}")
    for r in rows:
        returned = r["return_date"] or "Not yet"
        cost = f"{r['total_cost']:.2f}" if r["total_cost"] is not None else "-"
        print(f"{r['rental_id']:<5}{r['name']:<18}{r['reg_number']:<14}"
              f"{r['rent_date']:<12}{returned:<12}{cost}")


# ----------------------------------------------------------------------
# MAIN MENU
# ----------------------------------------------------------------------
def main():
    """Show the menu repeatedly until the user chooses Exit."""
    conn = connect_db()

    # Dictionary maps the menu choice to the function that should run.
    # This avoids a long if/elif chain and keeps the code clean.
    actions = {
        "1": add_member,
        "2": add_vehicle,
        "3": view_members,
        "4": view_vehicles,
        "5": rent_vehicle,
        "6": return_vehicle,
        "7": view_rentals,
    }

    while True:
        print("\n===== VEHICLE MANAGEMENT SYSTEM =====")
        print("1. Add new member")
        print("2. Add new vehicle")
        print("3. View all members")
        print("4. View all vehicles")
        print("5. Rent a vehicle")
        print("6. Return a vehicle")
        print("7. View rental records")
        print("8. Exit")
        choice = input("Enter your choice (1-8): ").strip()

        if choice == "8":
            print("Thank you for using the system. Goodbye!")
            break
        elif choice in actions:
            actions[choice](conn)     # call the matching function
        else:
            print("Invalid choice. Please enter a number from 1 to 8.")

    conn.close()


# This line makes sure main() runs only when we run this file directly
if __name__ == "__main__":
    main()
