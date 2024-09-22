import pynmea2
data = "24 47 4E 56 54 47 2C 2C 54 2C 2C 4D 2C 31 2E 35 30 31 2C 4E 2C 32 2E 37 37 39 2C 4B 2C 44 2A 33 36 0D 0A"
data.encode('utf-8')
msg = pynmea2.parse(data.decode('utf-8'))
print(msg)