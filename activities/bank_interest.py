from lib import NeoPage

def bank_interest():
    path = '/bank.phtml'
    np = NeoPage(path)
    if np.contains('You have already collected your interest today.'):
        print('Already collected interest today.')
    #elif WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'frmCollectInterest')):
        # Submit the form
    elif np.contains('frmCollectInterest'):
        driver.execute_script('frmCollectInterest.submit()')

        # Wait for the response
        response = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))
        # Parse the response
        data = json.loads(response.text)

        # Print the response
        print(data)
    else:
        print("Error collecting bank interest.")

if __name__ == '__main__':
    bank_interest()
