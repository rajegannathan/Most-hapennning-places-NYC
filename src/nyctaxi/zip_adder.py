import multiprocessing as mp
import itertools
import time
import csv
import json
from shapely.geometry import shape, Point

count = 0
NUM_PROCESS = 12

GEO_JSON_FILE = '/scratch/ajr619/Most-hapennning-places-NYC/data/zipcode.geojson'
geof = open(GEO_JSON_FILE, 'r')
geo_js = json.load(geof)

# `chunk` will be a list of CSV rows all with the same name column
# replace this with your real computation
def worker(chunk):
    global geo_js
    row = chunk[0]
    #6,7,10,11

    print(len(row))
    print(row)
    pickup_lon = row[0].strip()
    pickup_lat = row[1].strip()
    pickup_zipcode = '' 

    if len(pickup_lon) > 0 and len(pickup_lat) > 0:
        pickup_point = Point(float(pickup_lon),float(pickup_lat))
        for feature in geo_js['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(pickup_point):
                pickup_zipcode = feature['properties']['postalCode']
                print "pickup: got zipcode"
                break
            #else:
                #print("pickup polygon not available", pickup_lat, pickup_lon)
    #else:
        #print("pickup lat long not available ", pickup_lat, pickup_lon)

    row.append(pickup_zipcode)
    return row 

# `row` is one row of the CSV file.
# replace this with the name column.
def keyfunc(row):
    global count
    count = (count+1)%NUM_PROCESS
    return count


def main():
    INPUT_FILE = '/scratch/ajr619/Most-hapennning-places-NYC/data/taxi_latlng/uniq_latlongs.tsv.new'
    OUTPUT_FILE = '/scratch/ajr619/Most-hapennning-places-NYC/data/taxi_latlng/latlong_with_zip.csv'

    inf = open(INPUT_FILE,'r')
    outf = open(OUTPUT_FILE,'w')

    datareader = csv.reader(inf)
    datawriter = csv.writer(outf)
    pool = mp.Pool()
    iteration = 0
    with open(INPUT_FILE) as f:
        reader = csv.reader(f)
        chunks = itertools.groupby(reader, keyfunc)
        while True:
            # make a list of NUM_PROCESS chunks
            groups = [list(chunk) for key, chunk in itertools.islice(chunks, NUM_PROCESS)]
            if groups:
                result = pool.map(worker, groups)
                print("writing :", iteration);
                for r in result:
                    datawriter.writerow(r)
            else:
                break
            iteration = iteration +1
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
