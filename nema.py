import pynmea2

data = "$GNVTG,,T,,M,0.050,N,0.093,K,A*32"
msg = pynmea2.parse(data)
for tap in msg.fields:
    print(tap)