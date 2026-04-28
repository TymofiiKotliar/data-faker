from faker import Faker
import random
import numpy as np

# CONSTANTS
BED_TYPES_ID = range(0,8)
BED_TYPES = [
    ["Single", 0.90, 0.90, 1],
    ["Single (long)", 0.95, 1.00, 1],
    ["Double", 1.35, 1.90, 2],
    ["Queen", 1.52, 2.03, 2],
    ["King", 1.93, 2.03, 2],
    ["California King", 1.93, 2.13, 2],
    ["Bunk", 0.90, 1.90, 2],
    ["Sofa Bed", 0.40, 1.80, 2],
]

ROOM_TYPES_ID = range(0,10)
ROOM_TYPES = [
    [False, "Single Standard", 1, 12.00, 45.00],
    [True,  "Single Balcony", 1, 14.00, 55.00],
    [False, "Double Standard", 2, 18.00, 75.00],
    [True,  "Double Balcony", 2, 20.00, 90.00],
    [False, "Superior Double", 2, 25.00, 120.00],
    [True,  "Family Room", 4, 35.00, 160.00],
    [False, "Junior Suite", 2, 30.00, 180.00],
    [True,  "Executive Suite", 2, 45.00, 280.00],
    [False, "Accessible", 2, 22.00, 85.00],
    [True,  "Penthouse", 4, 95.00, 650.00],
]

# Set SEED
SEED = 42
fake = Faker()
Faker.seed(SEED)
random.seed(SEED)
np.random.seed(SEED)

# Helper Functions
def sql_escape(s: str) -> str:
    return s.replace("'", "''")
def sql_literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    return f"'{sql_escape(str(value))}'"

def write(f, table, colnames, id_list, data):
    f.write(f"\n-- {table} --\n")

    for i, row in zip(id_list, data):
        row_data = [sql_literal(i)] + [sql_literal(value) for value in row]
        row_data = ", ".join(row_data)
        columns = ", ".join(colnames)
        f.write(
            f"INSERT INTO {table} ({columns}) VALUES ({row_data});\n"
        )

# GENERATE
ADDRESS = []
ADDRESS_ID = range(1000)
for i in ADDRESS_ID:
    ADDRESS.append([
        fake.country(),
        fake.state() if random.random() > 0.25 else None,
        fake.city(),
        fake.street_address(),
        fake.building_number(),
        fake.secondary_address() if random.random() > 0.08 else None,
        fake.postalcode()
    ])



# WRITE
with open("seed.sql", "w", encoding="utf-8", newline="\n") as f:
    # Write BedType
    write(
        f,
        "BedType",
        ["id", "label", "height", "width", "capacity"],
        BED_TYPES_ID,
        BED_TYPES,
    )

    # Write RoomType
    write(
        f,
        "RoomType",
        ["id", "balcony", "label", "capacity", "square_meters", "price_per_night"],
        ROOM_TYPES_ID,
        ROOM_TYPES,
    )

    # Write Address
    write(f,
          "Address",
          ["id", "country", "region", "city", "street", "building_number", "apartment_number", "postal_code"],
          ADDRESS_ID,
          ADDRESS)