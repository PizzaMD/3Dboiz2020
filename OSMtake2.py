
import overpy
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import os
api = overpy.Overpass()


# fetch all ways and nodes
result = api.query("""
[out:json]
;
(
  way
    ["highway"]['highway'!='path']['highway'!='steps']['highway'!='footway']['highway'!='escape']['highway'!='service']['highway'!='pedestrian']
    (41.831173,-87.629539,41.839406,-87.623453);
);
out;
>;
out skel qt;
""")

lats = []
lons = []
#print(os.getcwd())

imageFile = cbook.get_sample_data('iitcampus.png')
img = plt.imread(imageFile)
fig, ax = plt.subplots()
ax.set_xlim([-87.629539,-87.623453])
ax.set_ylim([41.831173,41.839406])
ax.imshow(img, extent=[-87.629539,-87.623453,41.831173,41.839406])
for n in result.ways:
    for node in n.nodes:
        #print(str(node.lat))
        lats.append(node.lat)
        lons.append(node.lon)
    plt.plot(lons, lats)
    lats = []
    lons = []
#plt.xlim((-.05,1.05))
#plt.ylim((-.05,1.05))
plt.show()
