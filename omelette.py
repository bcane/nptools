#!/usr/bin/env python3

import lib

path = '/prehistoric/omelette.phtml'

def omelette():
    np = lib.NeoPage(path)
    np.post(path, 'type=get_omelette')
    if np.contains('You cannot take more than'):
        print('Omelette: Already took today.')
        return
    elif np.contains('You approach'):
        prize = np.search(r'You approach.*images.neopets.com/items/(.*?)\'')[1]
        print(f'Omelette: Got item with image {prize}')
    else:
        print('Omelette: Error.')

if __name__ == '__main__':
    omelette()
