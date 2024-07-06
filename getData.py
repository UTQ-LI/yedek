import time

import get_data

get_data.Start().StartAll()


print("Location Data:")
for key, value in get_data.Tuple.getLocationTuple.items():
    if value is None:
        print(f'{key}: {value}')
    else:
        print(f'{key}:')
        for i in value:
            print(f'\t{key}: {i}')

print("Regedit Data:")
for key, value in get_data.Tuple.getRegeditTuple.items():
    if value is None:
        print(f'{key}: {value}')
    else:
        print(f'{key}:')
        for i in value:
            print(f'\t{key}: {i}')