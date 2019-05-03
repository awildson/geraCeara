#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
import json
import os.path
import numpy as np
import matplotlib.pyplot as plt
import pprint
import googlemaps
import gmaps
import networkx as nx

from matplotlib import colors as mcolors
from geopy.distance import geodesic
from pandas.io.json import json_normalize
kkk=0


# In[2]:


colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

# Sort colors by hue, saturation, value and name.
by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                for name, color in colors.items())
sorted_names = [name for hsv, name in by_hsv]

kkk+=1;print("ordem",kkk)


# In[3]:


# Cesar para ver como faz a query consulte https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL
#
#
def getRodovias():
    poly = "-3.070145 -41.397623 -3.378076 -41.529317 -4.200684 -41.243993 -4.890447 -41.353599 -5.284097 -41.045815 -6.630547 -40.878812 -6.915577 -40.558076 -7.360932 -40.566191 -7.453001 -39.765866 -7.952970 -39.061235 -7.934419 -39.033309 -7.331740 -38.439331 -6.841795 -38.603392 -6.139325 -38.365410 -5.758917 -37.974206 -5.007089 -37.536193 -4.780404 -37.074409 -3.680291 -38.287696 -2.704505 -39.959576 -2.725466 -41.413189 -3.043958 -41.382122"
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = '[out:json];'
    overpass_query = overpass_query + 'area[admin_level=2];'
    overpass_query = overpass_query + '('
    overpass_query = overpass_query + 'way["ref"~"^BR-"](poly:"'+str(poly)+'");'
    overpass_query = overpass_query + 'node(w);'
    overpass_query = overpass_query + 'way["ref"~"^CE-"](poly:"'+str(poly)+'");'
    overpass_query = overpass_query + 'node(w);'
    overpass_query = overpass_query + ');'
    overpass_query = overpass_query + 'out center;'
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    return data
kkk+=1;print("ordem",kkk)


# In[4]:


f = "data/data.json"
if(os.path.exists(f)):
    with open(f) as json_file:
        data = json.load(json_file)
else:
    data = getRodovias()
    with open(f, 'w') as fileo:
        json.dump(data, fileo)
        
kkk+=1;print("ordem",kkk)


# In[9]:


def createG(data):
    G = nx.Graph()
    for element in data['elements']:
        if element['type'] == 'node':
            idn = element['id']
            lon = element['lon']
            lat = element['lat']
            G.add_node(idn,lat=lat,lon=lon,pos=(lon,lat),
                       cidade=0, nomeCidade="")
    
    for element in data['elements']:
        ide = element['id']
        try:
            nodes = element['nodes']
        except:
            nodes = []
        lenNodes = len(nodes)
        if(lenNodes>0):
            try:
                ref = element['ref']
            except:
                ref=""
            try:
                name = element['name']
            except:
                name = ""
            for i in range(1,lenNodes):
                G.add_edge(nodes[i],nodes[i-1],name=name,ref=ref,ide=ide)
    
    return G

G = createG(data)

kkk+=1;print("ordem",kkk)


# In[10]:


def plot1():
    pos = nx.get_node_attributes(G,'pos')
    draw = nx.draw_networkx_nodes(G,pos=pos,node_size=0.01)
    draw = nx.draw_networkx_edges(G,pos=pos,width=1)
    plt.savefig("export/ceara-ce-br.pdf")

kkk+=1;print("ordem",kkk)


# In[11]:


cc = sorted(nx.connected_components(G), key = len, reverse=True)
pos = nx.get_node_attributes(G,'pos')
def plot2():
    lcc = list(cc[0])
    sorted_names = sorted_names + sorted_names
    pos = nx.get_node_attributes(G,'pos')
    for i in range(len(cc)):
        #if(i==len(sorted_names)): break
        if(len(cc[i])<=100):
            color = sorted_names[i]
            draw = nx.draw_networkx_nodes(G,pos=pos,node_size=0.05,nodelist=list(cc[i]),node_color=color)
    plt.savefig("export/ceara-ce-br-subG-le100.pdf")

kkk+=1;print("ordem",kkk)


# In[ ]:


nx.write_gml(G,'export/G.gml')

kkk+=1;print("ordem",kkk)


# In[ ]:


def checkNodeNeig():
    dfcid = pd.read_csv("data/Municipios-Brasileiros/csv/municipios.csv",delimiter=",")
    dfcid["distancia"] = 1e10
    dfcid["node"] = 1

    # Ceará (23)
    dfcid = dfcid[dfcid.codigo_uf == 23]

    for i in dfcid.index:
        minV = dfcid.distancia.loc[i]
        lat0 = dfcid.latitude.loc[i]
        lon0 = dfcid.longitude.loc[i]
        cidade = dfcid.nome.loc[i]

        for n in list(G.nodes()):
            lon1,lat1 = pos[n]
            v = geodesic((lat0,lon0),(lat1,lon1)).meters
            if(v <= minV): 
                minV = v
                minN = n

        dfcid.distancia.at[i] = minV
        dfcid.node.at[i] = minN
        #print(cidade,minV,minN)

#
# Cria o arquivo de cidades mais proximo ao um vértice
#
try:
    dfcid = pd.read_pickle("data/cidades.plk")
except:
    print("Preciso criar o arquivo")

kkk+=1;print("ordem",kkk)


# In[ ]:


#
# Atualiza as Cidades
#

def plot3(dfcid,pos):
    draw = nx.draw_networkx_nodes(G,pos=pos,node_size=0.01)
    draw = nx.draw_networkx_nodes(G,pos=pos,nodelist=list(dfcid.node),node_size=5,node_color="blue")

    plt.savefig("export/ceara-ce-br-with-city.pdf")
#plot3(dfcid,pos)

cidades = nx.get_node_attributes(G,'cidade')
nome_cidades = nx.get_node_attributes(G,'nomeCidade')

for i in dfcid.index:
    cidade = dfcid.nome.loc[i]
    node = dfcid.node.loc[i]
    cidades[node] == 1
    nome_cidades[node]=cidade

nx.set_node_attributes(G,cidades,'cidade')
nx.set_node_attributes(G,nome_cidades,'nome_cidade') 

nodesCidades = list(dfcid.node)

kkk+=1;print("ordem",kkk)


# In[ ]:


#
# Verifica sítios vizinhos as Cidades
#
def checkNeig(cc):
    
    lenCC = len(cc)
    minsV = np.zeros((lenCC,lenCC))
    minsV = minsV + 1e10
    k=0
    for i in range(lenCC):
        nodesI = cc[i]
        for ni in nodesI:
            lat0, lon0 = pos[ni]
            for j in range(i+1,lenCC):
                nodesJ = cc[j]
                for nj in nodesJ:
                    lat1, lon1 = pos[nj]
                    minv = minsV[i,j]
                    v = geodesic((lat0,lon0),(lat1,lon1)).meters
                    #print(k,i,ni,j,nj,minv,v)
                    if(v<minv): minsV[i,j] = v
                    #if(k>100): return
                    k+=1
    return minsV

minsV = checkNeig(cc)

np.save("data/minsV",minsV)
                        
kkk+=1;print("ordem",kkk)


# In[ ]:


minsV = np.load("data/minsV.npy")
print(minsV)


# In[ ]:




