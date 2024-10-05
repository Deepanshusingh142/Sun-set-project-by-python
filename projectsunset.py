import csv
import requests
from datetime import datetime, timedelta

CSV_FILE = 'deepanshu.csv'

def load_users():
    users = {}
    try:
        with open(CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)  
            for row in reader:
                users[row[0]] = row[1]
    except FileNotFoundError:
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Email', 'Password'])  
    return users

def save_user(email, password):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([email, password])

def login():
    users = load_users()
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    
    if email in users and users[email] == password:
        print("Login successful!")
        return email
    else:
        print("Invalid credentials.")
        return None

def create_account():
    users = load_users()
    email = input("Enter your email: ")
    if email in users:
        print("An account with this email already exists.")
        return
    password = input("Enter a password: ")
    save_user(email, password)
    print("Account created successfully!")

def get_coordinates(city):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "SunriseSunsetApp/1.0"
    }
    try:
        response = requests.get(base_url, params=params, headers=headers)
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            print(f"Could not find coordinates for {city}")
            return None
    except requests.RequestException:
        print("Error occurred while fetching coordinates")
        return None

def get_sun_data(city):
    coords = get_coordinates(city)
    if not coords:
        return None

    lat, lng = coords
    base_url = "https://api.sunrise-sunset.org/json"
    params = {
        "lat": lat,
        "lng": lng,
        "formatted": 0
    }

    try:
        res = requests.get(base_url, params=params)
        data = res.json()
        if data['status'] == 'OK':
            results = data['results']
            return {
                'sunrise': datetime.fromisoformat(results['sunrise']),
                'sunset': datetime.fromisoformat(results['sunset']),
                'day_length': timedelta(seconds=float(results['day_length'])),
                'solar_noon': datetime.fromisoformat(results['solar_noon'])
            }
        else:
            print("Error fetching sunset/sunrise data.")
            return None
    except requests.RequestException:
        print("Network error while fetching sunset/sunrise data.")
        return None

def display_sun_data(city, data):
    print(f"\nSun data for {city}:")
    print(f"Sunrise Time: {data['sunrise'].strftime('%I:%M:%S %p')} UTC")
    print(f"Sunset Time: {data['sunset'].strftime('%I:%M:%S %p')} UTC")
    print(f"Day Length: {data['day_length']}")
    print(f"Solar Noon: {data['solar_noon'].strftime('%I:%M:%S %p')} UTC")

def main():
    print("Welcome to the Sunrise and Sunset Times App")

    while True:
        choice = input("\n1. Login\n2. Create Account\n3. Exit\nEnter your choice: ")

        if choice == '1':
            if login():
                while True:
                    city = input("\nEnter a city name (or 'q' to quit): ")
                    if city.lower() == 'q':
                        break
                    data = get_sun_data(city)
                    if data:
                        display_sun_data(city, data)
        elif choice == '2':
            create_account()
        elif choice == '3':
            print("Thank you for using the app. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()