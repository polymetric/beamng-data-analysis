import json

#filename = 'log_1_200bx_braketest_noabs_nopulse.json'
filename = 'log_2_200bx_braketest_abs_nopulse.json'

file = open(filename, 'r')
data = json.loads(file.read())
params = open('params', 'r').read().splitlines()
params.remove(params[-1])

results = []
n = 0
for i in data['electrics']['rpm']['values']:
    results.append({})
    if type(data['electrics']['rpm']['values'][n]) != dict:
        n += 1
        continue
    results[n]['time'] = data['electrics']['rpm']['values'][n]['time']
    for param in params:
            results[n][param] = data['electrics'][param]['values'][n]['value']
    n += 1

last_time = None
last_odometer_airspeed_mps = 0

params.insert(params.index('wheelspeed'), 'airspeed_mph')
params.insert(params.index('rpm'), 'wheelspeed_mph')
params.insert(params.index('airspeed'), 'odometer_airspeed_meters')

# calculate other parameters not originally included in the data
for i in results:
    try:
        # convert meters per second to miles per hour (conversion factor 2.237)
        i['airspeed_mph'] = 2.237*i['airspeed']
        i['wheelspeed_mph'] = 2.237*i['wheelspeed']
        # calculate how far we've traveled in the air.
        # (regular odometer param (also in meters) is based on how far the wheels have turned, like a real car)
        if last_time != None:
            time_diff = (i['time'] - last_time) / 1000
            i['odometer_airspeed_meters'] = last_odometer_airspeed_mps + i['airspeed'] * time_diff
            last_odometer_airspeed_mps = i['odometer_airspeed_meters']
        last_time = i['time']
    except KeyError as e:
        #print(e)
        #print(results.index(i))
        pass

# jankily construct a csv file
# first the names of the columns
s = 'time,'
for p in params:
    s += p + ','
s += '\n'
# then the actual values
for i in results:
    s2 = ''
    try:
        s2 += str(i['time'])
        s2 += ','
        for p in params:
            s2 += str(i[p])
            s2 += ','
        s2 += '\n'
    except KeyError as e:
        #print(e)
        continue
    s += s2

outfile = open(filename + '.csv', 'w')
outfile.write(s)

# grab braking distances
last_airspeed = None
for i in results:
    try:
        if last_airspeed != None and last_airspeed > 60 and i['airspeed_mph'] < 60:
            s = ''
            s += f"{ i['odometer_airspeed_meters'] }, { i['time'] }, "
        if last_airspeed != None and last_airspeed > 1 and i['airspeed_mph'] < 1:
            s += f"{ i['odometer_airspeed_meters'] }, { i['time'] } "
            print(s)
        last_airspeed = i['airspeed_mph']
    except KeyError as e:
        #print(e)
        #print(results.index(i))
        continue


