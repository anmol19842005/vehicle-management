# Vehicle Management System

A menu-driven console application in Python to manage members, a fleet
of vehicles, and the rentals that connect them. All data is stored
permanently in an SQLite database, so no external library or database
server is needed.

Developed during a six-week Python training at Techlive Solutions
as part of B.Tech CSE, MRSPTU Bathinda.

## Features
1. Add a new member
2. Add a new vehicle
3. View all members
4. View all vehicles with availability
5. Rent a vehicle to a member
6. Return a vehicle (rent is calculated automatically)
7. View rental history

## Highlights
- Input validation for empty text and invalid numbers
- Parameterised SQL queries to prevent SQL injection
- UNIQUE constraint to block duplicate registration numbers
- Availability flag to prevent renting a vehicle twice
- Rent rule: max(1, days) x daily rate

## Technology
- Python 3.7 or later
- sqlite3 and datetime (both built into Python)

## How to run
python vehicle_management.py

The database file vehicle_management.db is created automatically
on the first run.

## Database tables
- members (member_id, name, phone, license_no)
- vehicles (vehicle_id, reg_number, vehicle_type, model, daily_rate, available)
- rentals (rental_id, member_id, vehicle_id, rent_date, return_date, total_cost)

## Author
Anmol Preet Singh
