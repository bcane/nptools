from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import getpass
import pickle

# Set up Firefox driver
print("Initalizing web driver....")
options = Options()
#options.add_argument("--headless")
options.set_preference("permissions.default.image", 2)
driver = webdriver.Firefox(options=options)
print("Waiting to login...")
    
# Go to Neopets login page
driver.get("https://www.neopets.com/login/")
    
# Enter username and password
wait = WebDriverWait(driver, 60)
wait.until(EC.presence_of_element_located((By.ID, 'loginUsername')))
print(driver.title)

# Read cookie from file
try:
    with open('nptools.cookies', 'rb') as f:
        cookie = pickle.load(f)
except FileNotFoundError:
        print('Cookie file not found!')
        cookie = None

if cookie is not None:
    # Add the cookie to the webdriver
    for c in cookie:
        driver.add_cookie(c)

    # Refresh the page
    driver.refresh()

    # Check if the cookie is expired
    if driver.get_cookie('expired'):
        print('Cookie is expired!')
        cookie = None
    else:
        print('Cookie is valid!')

    # Get username and password from user

if cookie is None or driver.get_cookie('neologin') is None:
    
    username = input("Username: >")
    password = getpass.getpass("Password: >")
    
    username_field = driver.find_element(By.ID, "loginUsername")
    username_field.send_keys(username)
    
    password_field = driver.find_element(By.ID, "loginPassword")
    password_field.send_keys(password)
    
    # Click login button
    login_button = driver.find_element(By.ID, "loginButton")
    login_button.click()
    print("Attempt to login...")

else:
    print('Attempt to login with cookie...')
    driver.refresh()
    
wait = WebDriverWait(driver, 60)
# Wait for page to load
    
wait.until(EC.presence_of_element_located((By.ID, 'npanchor')))
print("Login sucessful")
# Store the cookie
cookie = driver.get_cookies()
pickle.dump(cookie, open('nptools.cookies',"wb"))

# Close driver
driver.close()
