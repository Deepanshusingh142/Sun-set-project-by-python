import csv
import re
import hashlib
import requests
from datetime import datetime, timedelta
import os
CSV_FILE = 'deepanshu.csv'
MAX_ATTEMPTS = 5
API_KEY = '277bc106e0bd6a190f8bcd18514304b6'   

def valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def valid_passwd(pwd):
    if len(pwd) < 8: return False
    if not re.search(r'[A-Z]', pwd): return False
    if not re.search(r'[a-z]', pwd): return False
    if not re.search(r'\d', pwd): return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd): return False
    return True

def hash_passwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def load_users():
    users = {}
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users[row['email']] = {
                    'passwd': row['password'],
                    'sec_q': row['security_question']
                }
    return users

def save_users(users):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['email', 'password', 'security_question'])
        writer.writeheader()
        for email, data in users.items():
            writer.writerow({
                'email': email,
                'password': data['passwd'],
                'security_question': data['sec_q']
            })

def create_account():
    users = load_users()
    while True:
        email = input("Enter your email: ")
        if not valid_email(email):
            print("Invalid email format. Please try again.")
            continue
        if email in users:
            print("An account with this email already exists. Please use a different email.")
            continue
        break

    while True:
        pwd = input("Enter your password: ")
        if not valid_passwd(pwd):
            print("Password does not meet the requirements.")
            continue
        break

    sec_q = input("Enter a security question: ")
    sec_ans = input("Enter the answer to your security question: ")

    users[email] = {
        'passwd': hash_passwd(pwd),
        'sec_q': f"{sec_q}: {sec_ans}"
    }
    save_users(users)
    print("Account created successfully!")

def login():
    users = load_users()
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        email = input("Enter your email: ")
        if not valid_email(email):
            print("Invalid email format. Please try again.")
            continue

        pwd = input("Enter your password: ")

        if email in users and users[email]['passwd'] == hash_passwd(pwd):
            print("Login successful!")
            return email
        else:
            attempts += 1
            print(f"Invalid credentials. {MAX_ATTEMPTS - attempts} attempts remaining.")

    print("Maximum login attempts exceeded. Exiting...")
    exit()

def reset_password():
    users = load_users()
    email = input("Enter your email:  ")
    if email in users:
        sec_q, correct_ans = users[email]['sec_q'].split(': ')
        ans = input(f"Answer your security question: {sec_q} ")
        if ans.lower() == correct_ans.lower():
            while True:
                new_pwd = input("Enter your new password: ")
                if valid_passwd(new_pwd):
                    users[email]['passwd'] = hash_passwd(new_pwd)
                    save_users(users)
                    print("Password reset successful.")
                    break
                else:
                    print("Password does not meet the requirements.")
        else:
            print("Incorrect security answer. Reset failed.")
    else:
        print("Email not found.")

def geocode(city):
    base_url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city, "appid": API_KEY, "limit": 1}

    try:
        res = requests.get(base_url, params=params)
        data = res.json()
        if data:
            return data[0]['lat'], data[0]['lon']
        else:
            print(f"Couldn't find coordinates for {city}.")
            return None
    except requests.RequestException:
        print("Network error while geocoding.")
        return None

def get_sun_data(city):
    coords = geocode(city)
    if not coords: return None

    lat, lon = coords
    base_url = "https://api.sunrise-sunset.org/json"
    params = {"lat": lat, "lng": lon, "formatted": 0}

    try:
        res = requests.get(base_url, params=params)
        data = res.json()
        if data['status'] == 'OK':
            results = data['results']
            return {
                'sunrise': datetime.fromisoformat(results['sunrise']),
                'sunset': datetime.fromisoformat(results['sunset']),
                'day_length': results['day_length'],
                'solar_noon': datetime.fromisoformat(results['solar_noon'])
            }
        else:
            print("Error fetching sunset/sunrise data.")
            return None
    except requests.RequestException:
        print("Network error while fetching sunset/sunrise data.")
        return None

def adjust_time(utc_time, offset):
    return utc_time + timedelta(hours=offset)

def main():
    print("Welcome to the Sunrise and Sunset Times App")

    while True:
        choice = input("1. Login\n2. Create Account\n3. Forgot Password\n4. Exit\nEnter your choice: ")

        if choice == '1':
            user_email = login()
            if user_email:
                while True:
                    city = input("Enter a city name (or 'q' to quit): ")
                    if city.lower() == 'q': break
                    data = get_sun_data(city)
                    if data:
                        try:
                            offset = float(input("Enter your UTC offset (e.g., 2 for UTC+2, -5 for UTC-5): "))
                        except ValueError:
                            print("Invalid offset. Using UTC time.")
                            offset = 0

                        sunrise = adjust_time(data['sunrise'], offset)
                        sunset = adjust_time(data['sunset'], offset)
                        solar_noon = adjust_time(data['solar_noon'], offset)

                        print(f"Sunrise: {sunrise.strftime('%H:%M:%S')}")
                        print(f"Sunset: {sunset.strftime('%H:%M:%S')}")
                        print(f"Day Length: {data['day_length']} seconds")
                        print(f"Solar Noon: {solar_noon.strftime('%H:%M:%S')}")
        elif choice == '2':
            create_account()
        elif choice == '3':
            reset_password()
        elif choice == '4':
            print("Thank you for using the app. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
