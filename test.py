import xml.etree.ElementTree as ET 
import matplotlib.pyplot as plt

tree = ET.parse("cayuga.xml")
root = tree.getroot()

print(root.tag)
print(root.attrib)

latCoords = []
longCoords = []
trackIDList = []

print(root.attrib["version"])

for child in root.findall("way"):
    if child.attrib["id"] == "440159416":
        for subChild in child:
            try:
                trackIDList.append(subChild.attrib["ref"])
            except KeyError as e:
                pass

for child in root:
    try:
        if child.attrib["id"] in trackIDList:
            latCoords.append(float(child.attrib["lat"]))
            longCoords.append(float(child.attrib["lon"]))
    except KeyError:
        pass

plt.xlim(42.8978570, 42.9074530)
plt.ylim(-79.8639860, -79.8493090)
plt.plot(latCoords,longCoords)
plt.show()

