import xml.etree.ElementTree as et
import xml.dom.minidom as md
import json as js
import math
import matplotlib.pyplot as plt
import numpy as np

#opening json file and extracting data
input_file = open('graphs.json', 'r')
json_decode=js.load(input_file)
nodes = json_decode['corridors']['nodes']
edges = json_decode['corridors']['edges']

x_coor = []
y_coor = []
#1 pixel represents 8.3 cm
k = 1.0/8.3 
#separation distance between nodes is 300 cm
separation_distance = 300*k 
x = []
y = []

#adding node coordinates to lists
for coordinate in nodes:
    x_coor.append(coordinate[0])
    y_coor.append(coordinate[1])


#calculating node coordinates
def calculate_coordinates(x1, x2, y1, y2, d1, d2):
    lam = d1/d2
    xCoor = (x1 + lam * x2) / (1 + lam)
    yCoor = (y1 + lam * y2) / (1 + lam)

    x.append(xCoor)
    y.append(yCoor)

for edge in edges:
    distance = math.sqrt(math.pow((x_coor[edge[0]-1]-x_coor[edge[1]-1]), 2) + math.pow((y_coor[edge[0]-1]-y_coor[edge[1]-1]), 2))

    if distance >= separation_distance:
        dist1 = 0
        dist2 = distance
        num = math.floor(distance/separation_distance)
        rest = distance - (num*separation_distance)

        if rest < (200 * k):
            num -= 1
        elif rest >= (500 * k):
            num += 1

        if num >= 1:
            rest = distance - (num * separation_distance)
            dist1 += (rest / 2)
            dist2 -= dist1
        elif num == 0:
            if distance >= separation_distance:
                dist1 = dist2 = distance/2
        calculate_coordinates(x_coor[edge[0] - 1], x_coor[edge[1] - 1], y_coor[edge[0] - 1], y_coor[edge[1] - 1], dist1, dist2)

        while num >= 1:
            rest = distance - (num * separation_distance)
            dist1 += separation_distance
            dist2 -= separation_distance
            num -= 1
            calculate_coordinates(x_coor[edge[0] - 1], x_coor[edge[1] - 1], y_coor[edge[0] - 1], y_coor[edge[1] - 1], dist1, dist2)

    elif distance < separation_distance and distance > 100:
        dist1 = dist2 = distance/2
        calculate_coordinates(x_coor[edge[0]-1], x_coor[edge[1]-1], y_coor[edge[0] - 1], y_coor[edge[1] - 1], dist1, dist2)

#removing node duplicates
data = zip(x,y)
data_set = set(data)
x = []
y = []
data_list = list(data_set)
for i in range(len(data_set)):
    x.append(data_list[i][0])
    y.append(data_list[i][1])

print len(x)
print len(y)
plt.plot(x, y, 'ro')
plt.show()

#parsing xml file, creating xml structure (mote tag)
tree = et.parse('simulation.csc')
root = tree.getroot()

simulation = root.find('simulation')
plugin_config = root.findall('plugin')[3].find('plugin_config')

for i in range(len(x)):
    mote = et.SubElement(simulation, 'mote')
    breakpoints = et.SubElement(mote, 'breakpoints')
    interface_config = et.SubElement(mote, 'interface_config')
    interface_config.text = 'org.contikios.cooja.interfaces.Position'
    x_coor = et.SubElement(interface_config, 'x')
    y_coor = et.SubElement(interface_config, 'y')
    z_coor = et.SubElement(interface_config, 'z')
    x_coor.text = str(x[i])
    y_coor.text = str(y[i])
    z_coor.text = '0.0'
    interface_config = et.SubElement(mote, 'interface_config')
    interface_config.text = 'org.contikios.cooja.mspmote.interfaces.MspClock'
    deviation = et.SubElement(interface_config, 'deviation')
    deviation.text = '1.0'
    interface_config = et.SubElement(mote, 'interface_config')
    interface_config.text = 'org.contikios.cooja.mspmote.interfaces.MspMoteID'
    mote_id = et.SubElement(interface_config, 'id')
    mote_id.text = str(i + 1)
    motetype_identifier = et.SubElement(mote, 'motetype_identifier')
    motetype_identifier.text = 'sky1'
    mote_tag = et.SubElement(plugin_config, 'mote')
    mote_tag.text = str(i)

xmlstr = md.parseString(et.tostring(root)).toprettyxml(indent="   ")
with open("layout.csc", "w") as f:
    f.write(xmlstr)
