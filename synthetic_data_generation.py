import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()

# Settings
num_users = 14000
num_weeks = 12
offerings = ['Offering_1', 'Offering_2', 'Offering_3', 'Offering_4']
locations = ['North America', 'Europe', 'Asia', 'South America', 'Africa']
business_units = ['BU1', 'BU2', 'BU3', 'BU4', 'BU5']  # Business units
start_date = "2023-01-01"

# Generate user data
user_ids = [fake.uuid4() for _ in range(num_users)]

# Base number of active users and growth rate per week to reach approximately 50% of total users by the end
base_active_users = 1000  # Starting number of active users
growth_rate = (7000 - base_active_users) / num_weeks  # Incremental number of users to add each week

# Simulate weekly visits with specific timestamps
data = []
start_datetime = pd.to_datetime(start_date)
for i in range(num_weeks):
    week_start = start_datetime + pd.to_timedelta(7 * i, unit='d')
    week_active_users = int(base_active_users + growth_rate * i)  # Increasing number of active users each week
    active_users = np.random.choice(user_ids, size=week_active_users, replace=False)  # Select unique users for activity

    for user_id in active_users:
        # Random number of visits per user
        num_visits = np.random.randint(1, 4)
        for _ in range(num_visits):
            activity_time = week_start + pd.to_timedelta(np.random.randint(0, 168), unit='h') + pd.to_timedelta(np.random.randint(0, 60), unit='m')
            business_unit = random.choice(business_units)  # Randomly assign a business unit
            data.append({
                'Timestamp': activity_time,
                'User_ID': user_id,
                'Offering': np.random.choice(offerings),
                'Location': np.random.choice(locations),
                'Business_Unit': business_unit  # Add business unit data
            })

visits_df = pd.DataFrame(data)

# Save to CSV
visits_df.to_csv('visits_data.csv', index=False)
