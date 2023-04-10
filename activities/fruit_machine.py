#!/usr/bin/env python3

import lib

path = '/desert/fruit/index.phtml'

def fruit_machine():
    np = lib.NeoPage(path)
    button = driver.find_element_by_xpath("//input[@value='Spin, spin, spin!']")
    if button is not None:
        button.click()
        print(f'Fruit machine: {prize}')
    elif np.contains('already had your free spin'):
        print('Fruit machine: Already played.')
    else:
        print('Fruit machine: Error!')

if __name__ == '__main__':
    fruit_machine()
