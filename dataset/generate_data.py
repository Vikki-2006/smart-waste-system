import csv
import random
from datetime import datetime, timedelta
import os

def generate_waste_data(filename, num_records=1000):
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    locations = [
        "Downtown Plaza", "Central Park", "Main Street Station",
        "University Campus", "City Mall", "Tech Park",
        "Residential Area A", "Residential Area B", "Hospital Zone",
        "Market Square"
    ]
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # bin_id, location, fill_level, timestamp
        writer.writerow(['bin_id', 'location', 'fill_level', 'timestamp'])
        
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(num_records):
            bin_id = random.randint(1, len(locations))
            location = locations[bin_id - 1]
            # Simulate some cyclic filling pattern: mostly fills up, gets emptied
            # For purely synthetic ML training, let's just generate a spread of data
            fill_level = random.uniform(0.0, 100.0)
            timestamp = (base_time + timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S')
            
            writer.writerow([bin_id, location, round(fill_level, 2), timestamp])
            
    print(f"Generated {num_records} records in {filename}")

if __name__ == "__main__":
    generate_waste_data("waste_data.csv", 2000)
