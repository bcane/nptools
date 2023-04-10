#!/usr/bin/env python3
import lib

def jelly():
    path = '/jelly/jelly.phtml'
    np = lib.NeoPage(path)
    driver.find_element_by_class_name("m20").form.submit()
    np.post(path, type='get_jelly')
    if np.contains('You take some'):
        prize = np.search(r'You take some <b>(.*?)</b>')[1]
        print(f"Giant Jelly: Got {prize}")
    elif np.contains('You cannot take more than one'):
        print("Already got jelly today.")
    else:
        print("Error getting giant jelly.")

if __name__ == '__main__':
    jelly()
