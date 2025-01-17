from __future__ import print_function
import math
import pyproj
import csv
import laspy
import scipy
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn import preprocessing
import mpl_toolkits.mplot3d
from matplotlib import path

R = 6378137
f_inv = 298.257224
f = 1.0 / f_inv
e2 = 1 - (1 - f) * (1 - f)

def fill_Tuple():
    file = open('fuse_to_obj.csv', newline = '')
    reader = csv.reader(file)

    header = next(reader)
    data = []

    for row in reader:
        lat = float(row[0])
        long = float(row[1])
        alt = float(row[2])
        inten = float(row[3])

        data.append([lat, long, alt, inten])
    file.close()

    return data

def gps_to_ecef_pyproj(lat, lon, alt):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    x, y, z = pyproj.transform(lla, ecef, lon, lat, alt, radians=False)

    return x, y, z

def gps_to_ecef(latitude, longitude, altitude):
    # (lat, lon) in WSG-84 degrees
    # h in meters
    cosLat = math.cos(latitude * math.pi / 180)
    sinLat = math.sin(latitude * math.pi / 180)

    cosLong = math.cos(longitude * math.pi / 180)
    sinLong = math.sin(longitude * math.pi / 180)

    c = 1 / math.sqrt(cosLat * cosLat + (1 - f) * (1 - f) * sinLat * sinLat)
    s = (1 - f) * (1 - f) * c

    x = (R*c + altitude) * cosLat * cosLong
    y = (R*c + altitude) * cosLat * sinLong
    z = (R*s + altitude) * sinLat

    return x, y, z

# ecef2enu
def ecef_to_enu(x, y, z, latRef, longRef, altRef):

    cosLatRef = math.cos(latRef * math.pi / 180)
    sinLatRef = math.sin(latRef * math.pi / 180)

    cosLongRef = math.cos(longRef * math.pi / 180)
    sinLongRef = math.sin(longRef * math.pi / 180)

    cRef = 1 / math.sqrt(cosLatRef * cosLatRef + (1 - f) * (1 - f) * sinLatRef * sinLatRef)

    x0 = (R*cRef + altRef) * cosLatRef * cosLongRef
    y0 = (R*cRef + altRef) * cosLatRef * sinLongRef
    z0 = (R*cRef*(1-e2) + altRef) * sinLatRef

    xEast = (-(x-x0) * sinLongRef) + ((y-y0)*cosLongRef)

    yNorth = (-cosLongRef*sinLatRef*(x-x0)) - (sinLatRef*sinLongRef*(y-y0)) + (cosLatRef*(z-z0))

    zUp = (cosLatRef*cosLongRef*(x-x0)) + (cosLatRef*sinLongRef*(y-y0)) + (sinLatRef*(z-z0))

    return xEast, yNorth, zUp

def geodetic_to_enu(lat, lon, h, lat_ref, lon_ref, h_ref):
    x, y, z = gps_to_ecef(lat, lon, h)

    return ecef_to_enu(x, y, z, lat_ref, lon_ref, h_ref)

data = fill_Tuple()
newData = []

def run_test():
    for pt in data:

        #xPy,yPy,zPy = gps_to_ecef_pyproj(pt[0], pt[1], pt[2])   
        #xF,yF,zF = gps_to_ecef(pt[0], pt[1], pt[2])

        #print("pyproj (XYZ)\t = ", xPy, yPy, zPy)
        #print("ECEF (XYZ)\t = ", xF, yF, zF)

        #latR, lonR, altR = gps_to_ecef(45.90360309, 11.02804799, 227.5475)

        xE, yN, zU = geodetic_to_enu(pt[0], pt[1], pt[2], 45.90360309, 11.02804799, 227.5475)
        #xE, yN, zU = ecef_to_enu(xF, yF, zF, latR, lonR, altR)

        newData.append([xE, yN, zU, pt[3]])
                
        #print(xE, yN, zU)
    return newData

newData = run_test()
                
len_data = len(newData)
x = [n[0] for n in newData]
y = [n[1] for n in newData]
z = [n[2] for n in newData]
dataset = np.vstack([x, y, z]).transpose()
dataset.shape
#focus on light posts
def frange(start, stop, step):
    i = start
    while i <stop:
        yield i
        i+= step
#ground points grid filter
n = 100# grid step
dataset_Z_filtered = dataset[[0]]
zfiltered = (dataset[:, 2].max() - dataset[:, 2].min())/10 #hight filtered from ground
print('zfiltered: ', zfiltered)
xstep = (dataset[:, 0].max() - dataset[:, 0].min())/n
ystep = (dataset[:, 1].max() - dataset[:, 1].min())/n
for x in frange (dataset[:, 0].min(), dataset[:, 0].max(), xstep):
    for y in frange (dataset[:, 1].min(), dataset[:, 1].max(), ystep):
        datasetfiltered = dataset[(dataset[:,0] > x)
                                  &(dataset[:, 0] < x+xstep)
                                  &(dataset[:, 1] > y)
                                  &(dataset[:, 1] <y+ystep)]
        if datasetfiltered.shape[0] > 0:
            datasetfiltered = datasetfiltered[datasetfiltered[:, 2]
                                              >(datasetfiltered[:, 2].min()+ zfiltered)]
            if datasetfiltered.shape[0] > 0:
                dataset_Z_filtered = np.concatenate((dataset_Z_filtered, datasetfiltered))
            
print('datset_Z_filtered shape', dataset_Z_filtered.shape)
dataset = preprocessing.normalize(dataset)
clustering = DBSCAN(eps=2, min_samples=5, leaf_size=30).fit(dataset)
#visualize
core_samples_mask = np.zeros_like(clustering.labels_, dtype=bool)
core_samples_mask[clustering.core_sample_indices_] = True
labels = clustering.labels_
# Number of clusters in labels, ignoring noise if present.

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)
print('Estimated number of clusters: %d' % n_clusters_)
print('Estimated number of noise points: %d' % n_noise_)
# Black removed and is used for noise instead.
#fig = plt.figure(figsize=[100, 50])
f = open('yeet2.txt', 'w')
for t in newData:
    line = ' '.join(str(x) for x in t)
    f.write(line + '\n')
f.close()
