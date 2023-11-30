#!/usr/bin/python

from collections import namedtuple
import time
import sys
import csv
import numpy as np

class Edge:
    def __init__(self, origin=None, destination=None, weight=None):
        self.origin = origin
        self.destination = destination
        self.weight = weight

    def printEdge(self):
        print(self.origin, ' ', self.destination, ' ', self.weight);

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)
    
    def same_edge(self, edge):
        return self.origin == edge.origin and self.destination == edge.destination

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight = 0

    def __repr__(self):
        return f"{self.code}\t{self.name}"
    
    def fillOutWeight(self):
        for route in self.routes:
            for dest in edgeHash[route.code]:
                if dest.origin == self.code:
                    self.outweight += dest.weight
                    break
    
    def printA(self):
        print(self.code, self.outweight)

def prints():
    for a in airportList: # list of Airport
        print(a.code, ' ', airportHash[a.code])
    for a in airportList:
        print(a.code, ' ', len(airportHash[a.code].routes) )

def printEdgeHash(filename = "EdgeHash.txt"):
    # Redirect standard output to a file
    with open(filename, "w") as file:
        sys.stdout = file
        print("PageRank Results")
        for key in edgeHash.keys():
            #print(key)
            for edge in edgeHash[key]:
                print(edge.origin, ' ', edge.destination, ' ', edge.weight)
        
        # Reset standard output
        sys.stdout = sys.__stdout__   
    
    print("EdgeHash printed in {0}".format(filename))

def printAirpotHash(filename = "AirpotHash.txt"):
    # Redirect standard output to a file
    with open(filename, "w") as file:
        sys.stdout = file
        print("AirpotHash")
        for a in airportHash.values():
            a.printA()
        
        # Reset standard output
        sys.stdout = sys.__stdout__
    
    print("AirpotHash printed in {0}".format(filename))

edgeList = [] # list of Edge
edgeHash = dict() # hash of edge to ease the match
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r")
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")

def readRoutes(fd):
    print("Reading Routes file from {0}".format(fd))
    routesTxt = open(fd, "r");
    cont_add = 0
    cont_rep = 0
    cont_rm = 0
    for line in routesTxt.readlines():
        e = Edge()
        try:
            temp = line.split(',')
            # Extract relevant information
            e.origin = temp[2]
            e.destination = temp[4]
            e.weight = 1
        except Exception as inst:
            pass
        else:
            # Eliminate routes with no origin or destination in the airport hash
            if e.origin not in airportHash.keys() or e.destination not in airportHash.keys():
                cont_rm += 1
                continue
            cont_add += 1
            edgeList.append(e)
            # Add edge to edgeHash if it is not there
            if e.destination not in edgeHash:
                edgeHash[e.destination] = []
                edgeHash[e.destination].append(e)
            else:
                # If the edge is already there, increase the weight
                for edge in edgeHash[e.destination]:
                    if edge.same_edge(e):
                        edge.weight += 1
                        cont_rep += 1
                        break
                else:
                    edgeHash[e.destination].append(e)
    routesTxt.close()

    print(f"There were {cont_add} routes with IATA code")
    print(f"There were {cont_rep} routes repeated")
    print(f"There were {cont_rm} routes removed because of the origin or destination were not in the airport list")
    printEdgeHash()

def fill_airport_routes():

    # Fill outweight
    # The edgeHash is a hash of destination -> list of edges
    # to be able to find the airports than have a route to the destination
    for edgeKey in edgeHash.keys():
        for edge in edgeHash[edgeKey]:
            airportHash[edge.origin].routes.append(airportHash[edge.destination])
            airportHash[edge.origin].outweight += edge.weight
    
    printAirpotHash()

# PageRank variables
epsilon=1e-8
max_iterations=1000

def computePageRanks(P, L):
    n = len(airportHash)
    n_zeroOutDegree = len([a for a in airportHash.keys() if airportHash[a].outweight == 0])
    aux = 1.0/n
    numberOuts = L/float(n)*n_zeroOutDegree

    it = 0
    for it in range(max_iterations):
        
        Q = {key: 0 for key in airportHash.keys()}
        for i in airportHash.values():

            # Distribute PageRank from each node with outdegree > 0
            if i.code in edgeHash.keys() and airportHash[i.code].outweight > 0:
                
                # Makeing the sumatory L*sum{P[j]*w(j,i)/out(j): there is an edge (j,i) in G }
                for ji in edgeHash[i.code]:
                    if ji.origin not in P.keys() or ji.destination not in P.keys():
                        continue
                    A = P[ji.origin] * ji.weight
                    B = airportHash[ji.origin].outweight
                    Q[i.code] += L * (A / B)
                
            # Damping Factor efect: + (1-L)/n
            Q[i.code] += (1 - L) / len(airportHash) + aux*numberOuts

        # Check for convergence
        if sum(abs(Q[a] - P[a]) for a in Q.keys()) < epsilon:
           break

        aux = (1 - L) / len(airportHash) + aux*numberOuts
        remaining_pagerank_total = 1 - sum(Q.values())
        P = Q

    return it, P, remaining_pagerank_total

def outputPageRanks(P, filename):
    # Redirect standard output to a file
    with open(filename, "w") as file:
        sys.stdout = file
        print("PageRank Results")
        
        for p in sorted(P.items(), key=lambda x: x[1], reverse=True):
            
            if airportHash[p[0]].outweight == 0:
                print( "Outdegree 0", p[1], ' ', p[0], ' ', airportHash[p[0]].name)
            else:
                print(p[1], ' ', p[0], ' ', airportHash[p[0]].name)

         # Reset standard output
        sys.stdout = sys.__stdout__

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    fill_airport_routes()

    with open("Dades_pagerank.csv", "w", newline='') as csvfile:
        fieldnames = ["L", "It", "Time", "rPK"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()

        for L in np.arange(0.99, 1.0, 0.05):
            count_it = 0
            count_time = 0
            count_rPK = 0
            damping_factor = L

            for rep in range(0, 10):
                # Initialize P as the all-1/n vector
                P = {key: (1 / len(airportHash)) for key in airportHash.keys()} 
                time1 = time.time()
                iterations, newP, rPK = computePageRanks(P,L)
                time2 = time.time()

                count_it += iterations
                count_time += time2 - time1
                count_rPK += rPK

            # Escribir una fila en el archivo CSV
            writer.writerow({"L": "{:.2f}".format(damping_factor), "It": count_it / 5, "Time": count_time / 5, "rPK": count_rPK / 5})


if __name__ == "__main__":
    sys.exit(main())
