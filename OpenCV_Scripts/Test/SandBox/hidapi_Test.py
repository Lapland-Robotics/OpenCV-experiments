from __future__ import print_function

import hid
import time

print("Opening the device")

h = hid.device()
h.open(25403, 173601) # A Microsoft wireless combo keyboard & mouse

print("Manufacturer: %s" % h.get_manufacturer_string())
print("Product: %s" % h.get_product_string())
print("Serial No: %s" % h.get_serial_number_string())

#try:
#    while True:
#        d = h.read(64)
#        if d:
#            print('read: "{}"'.format(d))
#finally:
#    print("Closing the device")
h.close()

