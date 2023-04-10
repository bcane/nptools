from lib import NeoPage

path = '/pirates/anchormanagement.phtml'

def anchor_management():
    np = NeoPage(path)
    if np.contains('form-fire-cannon'):
        driver.findElement(By.ID,'form-fire-cannon').submit()
        prize = driver.find_element_by_css_selector("span.prize-item-name").text
        print(f'Blasted krawken; got {prize}')
    elif np.contains('safe from sea monsters for one day'):
        print('Already did anchor management.')
    else:
        print("Couldn't find anchor management.")

if __name__ == '__main__':
    anchor_management()
