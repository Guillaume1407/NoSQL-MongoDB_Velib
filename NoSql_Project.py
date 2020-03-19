# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 08:25:44 2020

@author: Miloj
"""


"""
ANANDARASA Milojan
BICHAT Guillaume

"""
import requests 
import json
from pymongo import MongoClient
import datetime
import os
import matplotlib.pyplot as plt
import threading
import time





"""
Indique les disponibilités en temps réel des stations Vélib.
"""

API="https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&rows=1400&facet=station_state&facet=kioskstate&facet=creditcard&facet=overflowactivation"
data = requests.get(API)
data_json = json.loads(data.text)

with open('C:\Data\mydata.json','w') as file:
    json.dump(data_json['records'],file,indent=4)



def Newdata():
    client = MongoClient()
    db = client.velib
    col = db.data
    if(col.count_documents({})==0):
        for x in data_json['records']:
            col.insert_one(x)
    col.create_index([('fields.stationcode', 1)],unique=True)
    client.close() 
    

def Update():
    client = MongoClient()
    db = client.velib
    col = db.data
    for x in data_json['records']:   #New data 
        y=col.find({'fields.stationcode': x['fields']['stationcode']})    #Old data
        new_date=datetime.datetime.strptime(x['fields']['duedate'],'%Y-%m-%dT%H:%M:%S%z')    #New date
        old_date=datetime.datetime.strptime(y[0]['fields']['duedate'],'%Y-%m-%dT%H:%M:%S%z')
        if (new_date>old_date):
            col.replace_one({'fields.stationcode':y[0]['fields']['stationcode']},x)
    client.close()


class MonThread (threading.Thread):
    def __init__(self,jusqua):      
        threading.Thread.__init__(self) 
        self.jusqua = jusqua

    def run(self):
        for i in range(0, self.jusqua):
            Update()
            time.sleep(30)   # attend 30 secondes sans rien faire

m = MonThread(10)          # crée le thread
m.start()                  # démarre le thread,


def Nb_mbike():
    client = MongoClient()
    db = client.velib
    col = db.data
    nb_velib=col.aggregate([{'$group':{'_id':"$datasetid",'total':{'$sum':"$fields.mechanical"}}}])
    client.close()
    return nb_velib
    
        
def Nb_ebike():
    client = MongoClient()
    db = client.velib
    col = db.data
    nb_velib=col.aggregate([{'$group':{'_id':"$datasetid",'total':{'$sum':"$fields.ebike"}}}])
    client.close()
    return nb_velib

def Top_station(nb=3):
    client = MongoClient()
    db = client.velib
    col = db.data
    top=col.aggregate([{'$project':{'fields.name':1,'total':{'$add':["$fields.ebike","$fields.mechanical"]}}},{'$sort':{'total':-1}},{'$limit':int(nb)}])
    client.close()
    return top

def Find_station(name_station):
    client = MongoClient()
    db = client.velib
    col = db.data
    station=col.find({'fields.name':{'$regex': name_station}})
    client.close()
    return station



'''
          Menu
'''

def Menu():
    
    Newdata()
    choice=0
    while(choice!=str(4)) :
        print("\n\n                               ##################################\n")
        print("                                          Data Velib': \n")
        print("                               ##################################\n\n")
        print("          1-Number of bikes available.")
        print("          2-Find data about a station.")
        print("          3-Top stations")    
        print("          4-Exit")
          
        choice=input("\nYour choice: ")
        os.system("cls")
        if(choice==str(1)):
            bikes=[]
            name=['Electric Bike','Mechanic Bike']
            tot=0
            ebike=Nb_ebike()
            for x in ebike:
                print("  Number of bikes avaible at :\n")
                print("    -Electric Bike: "+str(x['total']))
                tot+=x['total']
                bikes.append(x['total'])
            mbike=Nb_mbike()
            for x in mbike:
                print("    -Mechanic Bike: "+str(x['total']))
                tot+=x['total']
                bikes.append(x['total'])
            print("    -Total: "+str(tot)+"\n")
            plt.pie(bikes, labels=name, autopct='%1.1f%%', startangle=90, shadow=True)
            plt.show()
            input("\nType enter for the next...")
            os.system("cls")
            
        if(choice==str(2)):
            station_name=input("Enter the station name please: ")
            stations=Find_station(station_name)
            for x in stations:
                print("\n  City: "+x['fields']['nom_arrondissement_communes'])
                print("     Station name: "+x['fields']['name'])
                print("           Capacity: "+str(x['fields']['capacity']))
                print("           Docks avaible: "+str(x['fields']['numdocksavailable']))
                print("           Bikes avaible: "+str(x['fields']['numbikesavailable']))
                print("           Last update: "+x['fields']['duedate']+"\n")
            input("\nType enter for the next...")
            os.system("cls")
            
             
        if(choice==str(3)):
            nb=input("How many stations do you want to see? ")
            bikes=[]
            name=[]
            top=Top_station(nb)
            print("\n  The top stations which the number of bikes avaible: \n")
            for x in top:
                print("     -"+str(x['fields']['name'])+": "+str(x['total']))
                bikes.append(x['total'])
                name.append(x['fields']['name'])
                
            plt.bar(name,bikes)
            plt.show()
            
            input("\nType enter for the next...")
            os.system("cls")
                    
   
Menu()
m._stop()
