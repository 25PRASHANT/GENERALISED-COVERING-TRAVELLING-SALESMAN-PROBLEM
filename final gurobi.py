# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 23:50:20 2019

@author: PRASHANT
"""

from gurobipy import*
import os
import xlrd

from scipy import spatial
import numpy
from sklearn.metrics.pairwise import euclidean_distances
import math

facility_cordinate={}
cust_cordinate={}
n_facility=23
n_cust=52
nc=6            ####CHANGE LINE NO 76 ALSO
book = xlrd.open_workbook(os.path.join("1.xlsx"))
sh = book.sheet_by_name("Sheet1")
i = 1
for i in range(1,n_facility+2):  
    sp3=sh.cell_value(i,0)
    sp = sh.cell_value(i,1)
    sp2 = sh.cell_value(i,2)
    sp1=(sp,sp2)
    facility_cordinate[sp3]=(sp1)
j=1
for i in range(n_facility+2,n_cust+2+n_facility):
    sp3=sh.cell_value(i,0)
    sp = sh.cell_value(i,1)
    sp2 = sh.cell_value(i,2)
    sp1=(sp,sp2)
    cust_cordinate[sp3]=sp1  
    j=j+1

def calculate_dist(x1, x2):
    eudistance = spatial.distance.euclidean(x1, x2)
    return(eudistance) 
facility_dist={}      
for i in facility_cordinate:
#    a=facility_cordinate[i]
    for j in facility_cordinate:
        facility_dist[i,j]=calculate_dist(facility_cordinate[i],facility_cordinate[j])
        
cust_dist={}
for i in facility_cordinate:
    for j in cust_cordinate:
        cust_dist[i,j]=calculate_dist(facility_cordinate[i],cust_cordinate[j])
a_ij={}
facility=[]
for i in range(n_facility+1):
    facility.append(i)
customers=[] 
demand={}
for i in range(n_facility+1,n_cust+n_facility+1):
    customers.append(i)  
    demand[i]=1
abc={}
    

for i in range(2,n_facility+2):
    j = 3
    xyz=[]
    while True:
        try:
            print(i,j)
            sp = sh.cell_value(i,j)
            xyz.append(sp)
            
            j = j + 1
            
        except IndexError:
            break
    abc[i-1]=xyz



for i in customers:
    for j in facility:
        if j!=0:
            a=abc[j]
            if i in a:
                a_ij[i,j]=1
            else:
                a_ij[i,j]=0

D=26
   
m=Model('GTSP')

X=m.addVars(facility,facility,vtype=GRB.BINARY,name="Xij")
U=m.addVars(facility,vtype=GRB.CONTINUOUS,name='U')

Z=m.addVars(customers,facility  ,vtype=GRB.BINARY,name="Zij")

m.modelSense=GRB.MINIMIZE
m.setObjective(sum((facility_dist[i,j]*X[i,j])for i in facility for j in facility))

m.addConstr((sum(demand[i]*Z[i,j] for i in customers for j in facility if j!=0 if a_ij[i,j]==1 )>=D))
       
for i in customers:
    m.addConstr(sum(Z[i,j] for j in facility if j!=0 if a_ij[i,j]==1) <=1)
    
m.addConstr(sum(X[0,j] for j in facility if j!=0 )==1)

m.addConstr(sum(X[j,0] for j in facility if j!=0)==1)

for i in facility:
    m.addConstr(sum(X[i,j] for j in facility ) - sum(X[j,i] for j in facility )==0)         

for i in customers:
    for j in facility:
        if j!=0:
            if a_ij[i,j]==1:
                m.addConstr(Z[i,j]<=sum(X[k,j] for k in facility)+ sum(X[j,k] for k in facility))
    
for i in facility:
    for j in facility:
        if i!=0 and j != 0:
            m.addConstr((U[i]-U[j]+(n_facility+2)*X[i,j])<=n_facility+1)

m.write('GTSP1.lp')
m.optimize()

for v in m.getVars():
    if v.x>0.01:
        print('%s%g'%(v.varName,v.x))
print('Objective:',round(m.objVal,2))
        