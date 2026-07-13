import requests
import json

base_url = "http://localhost:8000/api"
email = "testadmin@prospectassist.com"
password = "supersecurepassword123"

def run_tests():
    print("Testing Registration...")
    try:
        reg_res = requests.post(f"{base_url}/auth/register", json={"email": email, "password": password})
        if reg_res.status_code == 200:
            print("[+] Registration successful")
        elif reg_res.status_code == 400:
            print("[+] Registration successful (user already exists)")
        else:
            print(f"[-] Registration failed: {reg_res.status_code} - {reg_res.text}")
            return
            
        print("\nTesting Login...")
        login_res = requests.post(f"{base_url}/auth/login", json={"email": email, "password": password})
        if login_res.status_code == 200:
            print("[+] Login successful")
            token = login_res.json()["access_token"]
        else:
            print(f"[-] Login failed: {login_res.status_code} - {login_res.text}")
            return
            
        print("\nTesting Protected Dashboard Endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        dash_res = requests.get(f"{base_url}/dashboard", headers=headers)
        if dash_res.status_code == 200:
            print("[+] Dashboard access successful")
        else:
            print(f"[-] Dashboard access failed: {dash_res.status_code} - {dash_res.text}")
            
    except Exception as e:
        print(f"[-] Connection error: {e}. Is the backend running?")

if __name__ == "__main__":
    run_tests()
