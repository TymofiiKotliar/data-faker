from faker import Faker
import random
import numpy as np

fake = Faker()
Faker.seed(42)       # reproducibility
random.seed(42)
np.random.seed(42)

rows = []
for i in range(1000):  # however many you need
    rows.append({
        "id": i + 1,
        "name": fake.name(),
        "email": fake.email(),
    })

# Then write to SQL
with open("seed.sql", "w") as f:
    for r in rows:
        f.write(f"INSERT INTO guest (id, name, email) VALUES ({r['id']}, '{r['name']}', '{r['email']}');\n")