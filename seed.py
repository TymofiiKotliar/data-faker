from faker import Faker
import random
import numpy as np
from datetime import date, timedelta, datetime

# CONSTANTS
BED_TYPES_ID = range(1, 9)
BED_TYPES = [
    ["Single",          0.90, 0.90, 1],
    ["Single (long)",   0.95, 1.00, 1],
    ["Double",          1.35, 1.90, 2],
    ["Queen",           1.52, 2.03, 2],
    ["King",            1.93, 2.03, 2],
    ["California King", 1.93, 2.13, 2],
    ["Bunk",            0.90, 1.90, 2],
    ["Sofa Bed",        0.40, 1.80, 2],
]

ROOM_TYPES_ID = range(1, 11)
ROOM_TYPES = [
    [False, "Single Standard",  1, 12.00,  45.00],
    [True,  "Single Balcony",   1, 14.00,  55.00],
    [False, "Double Standard",  2, 18.00,  75.00],
    [True,  "Double Balcony",   2, 20.00,  90.00],
    [False, "Superior Double",  2, 25.00, 120.00],
    [True,  "Family Room",      4, 35.00, 160.00],
    [False, "Junior Suite",     2, 30.00, 180.00],
    [True,  "Executive Suite",  2, 45.00, 280.00],
    [False, "Accessible",       2, 22.00,  85.00],
    [True,  "Penthouse",        4, 95.00, 650.00],
]

BEDS_IN_ROOM = [
    [1, 1], [2, 2],
    [3, 3], [3, 4],
    [4, 5],
    [4, 6], [7, 6],
    [5, 7],
    [6, 8],
    [1, 9],
    [6, 10], [8, 10],
]


SERVICES = [
    [True,  "Breakfast",        15.00, "Full buffet breakfast"],
    [True,  "Lunch",            20.00, "Three-course lunch"],
    [True,  "Dinner",           35.00, "Three-course dinner"],
    [True,  "Room Service",     12.00, "In-room dining 24/7"],
    [True,  "Parking",          20.00, "Covered parking per night"],
    [True,  "Airport Transfer", 45.00, "One-way airport shuttle"],
    [True,  "Spa",              60.00, "60-min relaxation treatment"],
    [True,  "Pool Access",      15.00, "Full day pool access"],
    [True,  "Gym Access",       10.00, "Full day gym access"],
    [True,  "Laundry",          12.00, "Per bag laundry service"],
    [True,  "Mini Bar",         30.00, "Pre-stocked mini bar"],
    [False, "Late Checkout",    25.00, "Checkout extension to 2 PM"],
]

INCLUDED_SERVICES = [
    [6,  8, 4],
    [7,  1, 2], [7,  8, 2], [7,  9, 2],
    [8,  1, 2], [8,  8, 2], [8,  9, 2], [8,  11, 1],
    [10, 1, 4], [10, 3, 4], [10, 7, 2],
    [10, 8, 4], [10, 9, 4], [10, 11, 1],
]

# SEED

SEED = 42
fake = Faker()
Faker.seed(SEED)
random.seed(SEED)
np.random.seed(SEED)

# HELPERS

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
        row_data = ", ".join([sql_literal(i)] + [sql_literal(v) for v in row])
        f.write(f"INSERT INTO {table} ({', '.join(colnames)}) VALUES ({row_data});\n")

# For composite-PK tables that have no id column (GuestAddress, IncludedServices)
def write_no_id(f, table, colnames, data):
    f.write(f"\n-- {table} --\n")
    for row in data:
        row_data = ", ".join(sql_literal(v) for v in row)
        f.write(f"INSERT INTO {table} ({', '.join(colnames)}) VALUES ({row_data});\n")

# GENERATE

# Room
ROOM_NUMBERS    = []
ROOMS           = []
ROOM_TYPE_FOR   = {}
ROOM_TYPE_CAP   = {i + 1: ROOM_TYPES[i][2] for i in range(len(ROOM_TYPES))}  # id → capacity
ROOM_TYPE_PRICE = {i + 1: ROOM_TYPES[i][4] for i in range(len(ROOM_TYPES))}  # id → price/night

floor_layout = {
    1: ([1, 2],    10),   # single rooms
    2: ([1, 2],    10),
    3: ([3, 4, 5], 10),   # double rooms
    4: ([3, 4, 5], 10),
    5: ([6, 9],     8),   # family + accessible
    6: ([7, 8],     6),   # suites
    7: ([10],        2),  # penthouse
}
for floor, (types, count) in floor_layout.items():
    for n in range(1, count + 1):
        rn = floor * 100 + n
        rt = random.choice(types)
        ROOM_NUMBERS.append(rn)
        ROOMS.append([floor, rt, 'free'])
        ROOM_TYPE_FOR[rn] = rt

# Guest
GUEST_COUNT    = 1000
GUESTS         = []
used_passports = set()

for _ in range(GUEST_COUNT):
    first_name = fake.first_name()[:60]
    last_name  = fake.last_name()[:60]
    dob        = fake.date_of_birth(minimum_age=18, maximum_age=80)
    email      = fake.unique.email()
    phone      = fake.numerify('+## ### ### ####')
    while True:
        passport = fake.bothify('??#######').upper()
        if passport not in used_passports:
            used_passports.add(passport)
            break
    GUESTS.append([first_name, last_name, dob, email, phone, passport])

GUEST_IDS = list(range(1, GUEST_COUNT + 1))

# ── Address ───────────────────────────────────────────────────────────────────
# (locale, has_administrative_region)
LOCALE_MAP = {
    "United States":  ("en_US", True),
    "United Kingdom": ("en_GB", False),
    "Germany":        ("de_DE", False),
    "France":         ("fr_FR", False),
    "Italy":          ("it_IT", False),
    "Spain":          ("es_ES", False),
    "Netherlands":    ("nl_NL", False),
    "Poland":         ("pl_PL", False),
    "Czech Republic": ("cs_CZ", False),
    "Slovakia":       ("sk_SK", False),
    "Ukraine":        ("uk_UA", False),
    "Brazil":         ("pt_BR", True),
    "Australia":      ("en_AU", True),
    "Canada":         ("en_CA", True),
    "Sweden":         ("sv_SE", False),
    "Norway":         ("no_NO", False),
    "Denmark":        ("da_DK", False),
}

# Pre-build one Faker per locale
locale_fakers = {}
for locale, _ in LOCALE_MAP.values():
    lf = Faker(locale)
    lf.seed_instance(SEED)
    locale_fakers[locale] = lf

COUNTRIES = list(LOCALE_MAP.keys())
# Weighted — biased toward more common travel origins
COUNTRY_WEIGHTS = [20, 15, 10, 10, 8, 8, 5, 5, 5, 5, 5, 4, 4, 4, 2, 2, 2]

ADDRESS    = []
ADDRESS_ID = range(1, 1001)

for _ in ADDRESS_ID:
    country            = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS)[0]
    locale, has_region = LOCALE_MAP[country]
    lf                 = locale_fakers[locale]

    region = None
    if has_region and random.random() > 0.25:
        try:
            region = lf.state()[:85]
        except AttributeError:
            pass

    try:
        street = lf.street_name()[:60]
    except AttributeError:
        street = fake.street_name()[:60]   # fallback to en_US

    try:
        postcode = lf.postcode()[:9]
    except AttributeError:
        postcode = fake.postcode()[:9]

    ADDRESS.append([
        country,
        region,
        lf.city()[:168],
        street,
        fake.building_number(),
        fake.secondary_address()[:10] if random.random() > 0.08 else None,
        postcode,
    ])

# GuestAddress
GUEST_ADDRESS  = []
shuffled_addrs = list(range(1, 1001))
random.shuffle(shuffled_addrs)

for idx, guest_id in enumerate(GUEST_IDS):
    primary = shuffled_addrs[idx]
    GUEST_ADDRESS.append([guest_id, primary])
    if random.random() < 0.20:
        secondary = random.choice(shuffled_addrs)
        if secondary != primary:
            GUEST_ADDRESS.append([guest_id, secondary])

# PaymentMethod
PAYMENT_METHODS = []
PM_ID = 1
guest_payment_map = {}

for guest_id in GUEST_IDS:
    n = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
    guest_payment_map[guest_id] = []
    for _ in range(n):
        exp_date = fake.date_between(start_date='today', end_date='+5y')
        raw      = fake.credit_card_number()[:16].ljust(16, '0')
        card_num = ' '.join(raw[i:i+4] for i in range(0, 16, 4))
        cvc      = fake.numerify('###')
        PAYMENT_METHODS.append([guest_id, exp_date, card_num, cvc])
        guest_payment_map[guest_id].append(PM_ID)
        PM_ID += 1

# Reservation + PaymentRecord
# These are generated together because PaymentRecord references Reservation IDs
# that are only known at generation time.
START_DATE = date(2024, 1, 1)
END_DATE   = date(2026, 8, 1)
TODAY      = date(2026, 4, 28)

# Pareto weights: ~20% of guests receive ~80% of reservations
pareto_w  = np.random.pareto(1.5, GUEST_COUNT) + 1
pareto_w /= pareto_w.sum()

RESERVATIONS    = []
PAYMENT_RECORDS = []
res_id = 1
pr_id  = 1

for room_num in ROOM_NUMBERS:
    rt_id    = ROOM_TYPE_FOR[room_num]
    max_cap  = ROOM_TYPE_CAP[rt_id]
    price_pn = ROOM_TYPE_PRICE[rt_id]
    cursor   = START_DATE

    while cursor < END_DATE:
        cursor += timedelta(days=random.randint(0, 14))
        if cursor >= END_DATE:
            break

        stay      = timedelta(days=random.randint(1, 21))
        check_in  = cursor
        check_out = cursor + stay
        if check_out > END_DATE:
            break

        guest_id = int(np.random.choice(GUEST_IDS, p=pareto_w))

        if check_out <= TODAY:
            status = 'inactive'
        elif check_in <= TODAY:
            status = 'active'
        else:
            status = 'reserved'

        days_before  = random.randint(1, 90)
        created_date = check_in - timedelta(days=days_before)
        created_ts   = f"{created_date} {random.randint(8, 22):02d}:{random.randint(0, 59):02d}:00+00"
        checkin_ts   = f"{check_in} 14:00:00+00"
        checkout_ts  = f"{check_out} 11:00:00+00"
        total_guests = random.randint(1, max_cap)

        RESERVATIONS.append([
            guest_id, room_num, created_ts, checkin_ts, checkout_ts, status, total_guests
        ])

        # PaymentRecord
        pms       = guest_payment_map.get(guest_id, [])
        pay_type  = random.choices(['Card', 'Cash'], weights=[75, 25])[0]
        pm_choice = random.choice(pms) if pay_type == 'Card' and pms else None
        p_status  = 'completed' if status == 'inactive' else random.choice(['pending', 'completed'])
        amount    = round(stay.days * price_pn, 2)

        PAYMENT_RECORDS.append([
            res_id, pm_choice, None,
            created_ts, 'receiving', p_status,
            amount, 'Room charge', pay_type
        ])
        pr_id += 1

        # PaymentRecord
        if random.random() < 0.40:
            svc_id     = random.randint(1, len(SERVICES))
            svc_amount = round(SERVICES[svc_id - 1][2] * random.randint(1, 3), 2)
            PAYMENT_RECORDS.append([
                res_id, pm_choice, svc_id,
                created_ts, 'receiving', p_status,
                svc_amount, 'Additional service', pay_type
            ])
            pr_id += 1

        # PaymentRecord
        if status == 'inactive' and random.random() < 0.05:
            refund = round(amount * random.uniform(0.1, 0.5), 2)
            PAYMENT_RECORDS.append([
                res_id, pm_choice, None,
                created_ts, 'refund', 'completed',
                refund, 'Partial refund', pay_type
            ])
            pr_id += 1

        cursor = check_out
        res_id += 1

RES_COUNT = res_id - 1

# Review
REVIEWS      = []
inactive_ids = [i + 1 for i, r in enumerate(RESERVATIONS) if r[5] == 'inactive']
reviewed_ids = random.sample(inactive_ids, k=int(len(inactive_ids) * 0.30))

for r_id in reviewed_ids:
    res        = RESERVATIONS[r_id - 1]
    checkout_d = datetime.strptime(res[4][:10], "%Y-%m-%d").date()
    review_d   = checkout_d + timedelta(days=random.randint(0, 14))
    created_ts = f"{review_d} {random.randint(8, 22):02d}:{random.randint(0, 59):02d}:00+00"
    rating     = random.choices(range(1, 11), weights=[1, 1, 2, 2, 3, 5, 8, 12, 10, 6])[0]
    desc       = fake.paragraph(nb_sentences=2)[:1000] if random.random() < 0.70 else None
    REVIEWS.append([r_id, created_ts, rating, desc])



# WRITE
with open("seed.sql", "w", encoding="utf-8", newline="\n") as f:
    f.write("BEGIN;\n")

    write(f, "BedType",
          ["id", "label", "height", "width", "capacity"],
          BED_TYPES_ID, BED_TYPES)

    write(f, "RoomType",
          ["id", "balcony", "label", "capacity", "square_meters", "price_per_night"],
          ROOM_TYPES_ID, ROOM_TYPES)

    write(f, "BedsInRoom",
          ["id", "bed_type_id", "room_type_id"],
          range(1, len(BEDS_IN_ROOM) + 1), BEDS_IN_ROOM)

    write(f, "Room",
          ["room_number", "floor", "room_type_id", "status"],
          ROOM_NUMBERS, ROOMS)

    write(f, "Service",
          ["id", "active", "label", "price", "description"],
          range(1, len(SERVICES) + 1), SERVICES)

    write_no_id(f, "IncludedServices",          # composite PK — no id column
                ["room_type_id", "service_id", "quantity"],
                INCLUDED_SERVICES)

    write(f, "Guest",
          ["id", "first_name", "last_name", "date_of_birth", "email", "phone_number", "passport_number"],
          range(1, GUEST_COUNT + 1), GUESTS)

    write(f, "Address",
          ["id", "country", "region", "city", "street", "building_number", "apartment_number", "postal_code"],
          ADDRESS_ID, ADDRESS)

    write_no_id(f, "GuestAddress",              # composite PK — no id column
                ["guest_id", "address_id"],
                GUEST_ADDRESS)

    write(f, "PaymentMethod",
          ["id", "guest_id", "expiration_date", "card_number", "cvc_cvv"],
          range(1, PM_ID), PAYMENT_METHODS)

    write(f, "Reservation",
          ["id", "guest_id", "room_id", "created_at", "check_in", "check_out", "status", "total_guests_number"],
          range(1, RES_COUNT + 1), RESERVATIONS)

    write(f, "Review",
          ["id", "reservation_id", "created_at", "rating", "description"],
          range(1, len(REVIEWS) + 1), REVIEWS)

    write(f, "PaymentRecord",
          ["id", "reservation_id", "payment_method_id", "service_id", "created_at",
           "transaction_type", "transaction_status", "amount", "description", "payment_type"],
          range(1, pr_id), PAYMENT_RECORDS)

    # Resetting SERIAL sequences is necessary because we inserted explicit IDs.
    # Without this, the next INSERT (e.g. during manual testing) would try id=1
    # and collide with existing data.
    f.write("\n-- Reset sequences after explicit ID inserts --\n")
    for tbl, col in [
        ("bedtype", "id"), ("roomtype", "id"), ("bedsinroom", "id"),
        ("service", "id"), ("guest", "id"), ("address", "id"),
        ("paymentmethod", "id"), ("reservation", "id"),
        ("review", "id"), ("paymentrecord", "id"),
    ]:
        f.write(f"SELECT setval('{tbl}_{col}_seq', (SELECT MAX({col}) FROM {tbl}));\n")

    f.write("\nCOMMIT;\n")

print(
    f"✓ {GUEST_COUNT} guests | {len(ROOM_NUMBERS)} rooms | {RES_COUNT} reservations | "
    f"{len(REVIEWS)} reviews | {len(PAYMENT_RECORDS)} payment records"
)