print("Hello Malcolm! Your SolarEdge API Program is running!")

import requests

api_key = '&api_key='
base_url = 'http://monitoringapi.solaredge.com/sites/'

# Get the fleet size
url = base_url+'list?size=1'+api_key
data = requests.get(url).json()
count = data['sites']['count']
n_calls = int(count/100)
print("The number of SunBug sites is "+str(count))

# Build site information lists
id_list = []
name_list = []
peakPower_list = []
module_list = []
installation_date_list = []
for i in range(0, n_calls+1):
    start_index = i*100
    start_index = '&startIndex='+str(start_index)
    url = base_url+'list?'+start_index+api_key
    print("Making call "+str(i)+"...")
    data = requests.get(url).json()
    list_of_sites = data['sites']['site']
    n_sites = len(list_of_sites)
    for x in range(0, n_sites):
        id_list.append(list_of_sites[x]['id'])
        name_list.append(list_of_sites[x]['name'])
        installation_date_list.append(list_of_sites[x]['installationDate'])
        peakPower_list.append(list_of_sites[x]['peakPower'])
        module_list.append(list_of_sites[x]['primaryModule']['manufacturerName'])

#build the URL for the bulk energy call
url = base_url
for i in range(0, count):
    url += str(id_list[i])
    url += ','
url = url.rstrip(',')
url += '/energy?'
url += 'timeUnit=DAY'
url += '&startDate=2016-01-01'
url += '&endDate=2016-12-31'
url += api_key

#make the bulk energy call
print("Making the bulk energy call...")
data2 = requests.get(url).json()
data2 = data2['sitesEnergy']['siteEnergyList']

# make the energy lists using a list of lists called lol
lol = []
for i in range(0, count):
    liszt = []
    for x in range(0, len(data2[0]['energyValues']['values'])):
        if data2[i]['energyValues']['values'] == []:
            liszt = [None, None, None]
        else:
            liszt.append(data2[i]['energyValues']['values'][x]['value'])
    for y in range(0, len(liszt)):
        if liszt[y] != None:
            liszt[y] /= 1000
    lol.append(liszt)

# create a master dictionary for parsing sites.
# call it md
md = {}
for i in range(0, count):
    md[id_list[i]] = {}
    md[id_list[i]]['name'] = name_list[i]
    md[id_list[i]]['site_id'] = id_list[i]
    md[id_list[i]]['installation_date'] = installation_date_list[i]
    md[id_list[i]]['module'] = module_list[i]
    md[id_list[i]]['peak_power'] = peakPower_list[i]
    md[id_list[i]]['values_list'] = lol[i]

# create a duplicate master dictionary for safe deleting
md2 = md.copy()
for k, v in md.items():
    if None in v['values_list']:
        del md2[k]

# add energy sums an production ratios!
md3 = md2.copy()
for k, v in md2.items():
    e_tot = sum(v['values_list'])
    md3[k]['e_total'] = e_tot
    md3[k]['prod_ratio'] = e_tot/v['peak_power']

# make csv matrix
matrix = []
for k, v in md3.items():
    row = []
    row.append(v['name'])
    row.append(v['site_id'])
    row.append(v['installation_date'])
    row.append(v['module'])
    row.append(v['peak_power'])
    row.append(v['e_total'])
    row.append(v['prod_ratio'])
    matrix.append(row)

import csv
with open('test.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(matrix)
print("CSV complete!")
