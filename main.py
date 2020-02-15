import requests
import json
import sys
import collections


routeStopMap = {}
routeTransferStopMap = {}
transferStopRouteMap = {}
routeToRouteMapFinal = {}



def populateMaps():

	global routeStopMap
	global routeToRouteMapFinal
	global routeTransferStopMap
	global transferStopRouteMap

	# In this case, I'm using the filtered Get request. Realistically, we could use either, but in terms of having to not pull in as much data, it is better to
	# have the calcuation handled on MBTA's side. If I was looking to do more work with the rest of the MBTA (Commuter Rail etc), I would probably want to use the unfiltered request
	# as I would not need to pull in that data at a later time. 
	# For the sake of clarity, I have included the extra line of code needed to process the non-filtered request

	allRoutesJson= requests.get("https://api-v3.mbta.com/routes?filter[type]=0,1")

	# Build a Dictionary with Route Info
	text = json.dumps(allRoutesJson.json()['data'])
	dictFromJson = json.loads(text)

	# From the list of total routes, get the ones with type 0 or 1 (has already been done if filtered).
	# Then create a map pointing each route to the stops it has.
	# With the key of the map will help us answer Question 1. The values of the map will be used in Question 2

	for route in dictFromJson:
		# the below code is what I can use to filter if not already done so.
		#if route['attributes']['type'] == 0 or route['attributes']['type'] == 1:
		routeStopMap[route['id']] = getSubwayStops(route['id'])
	
	#Printing List of Subway Routes
	print('List of Subway Routes')
	print(*routeStopMap)
	print()


	# Once we have the list of all of the routes and the stops on each, let's create a map for Routes to List of Stops with Transfers
	# First let's just take the list of stops and map them with the lines they have access to.  
	# This will give us a dictionary from which we can determine both the stops with multiple routes and create a basis for finding the path between stops
	listOfStopsAndTransfer = getTransferStops()


	#We can get two maps from this map created above

	# RouteTransferStopMap has the form: {Stop: [Routes at Stop]}
	# TransferStopRouteMap  has the form: {Routes: [Transfer Stops on Route]}
	transferStopRouteMap, routeTransferStopMap=transformTransferStopOfRoute(listOfStopsAndTransfer)

	# Solving for Question 2
	minRoute, minValue = minStop()
	maxRoute, maxValue = maxStop()

	
	minRouteTransferList = transferStopRouteMap[minRoute]
	maxRouteTransferList = transferStopRouteMap[maxRoute]

	print('The route with the fewest stops is: ' + minRoute + ' with a total of ' + str(minValue) +' stops.')
	print('The route with the most stops is: ' + maxRoute + ' with a total of ' + str(maxValue) +' stops.')
	print()
	print('List of Stops that Connect Two or more Subway Routes along with the routes they connect ')
	for route in routeTransferStopMap:
		print('Stop: ' +route + " connects routes from " + str(routeTransferStopMap[route]))
	
	print()
	# For Question 3, I started out by trying to set up a graph to use shortest path algorithms.
	# The nodes of the graph are the Routes and the Transfer Stops. We don't need to use every single stop, as we only really need to know which line these stops are.
	# I am also using transfer stops as nodes, so we don't have an issue where the algorithm would visit multiple lines at the same stop.
	# The combination of these two dictionaries just so happens to map out the graph.

	routeToRouteMapFinal = {**transferStopRouteMap,**routeTransferStopMap}

	# We take in user input through the command line arguments.
	# This could be done better in waiting for a user query, but this will suffice for now

	startDestination = sys.argv[1]
	endDestination = sys.argv[2]

	# In the case the user enters an incorrect stop on the subway, we want to make sure they know and can try again.
	# I still send the answers for Qs 1 and 2, as they are not dependent on the input
	if not isStopInSubway(startDestination):
		print("Start Destination is not in Subway. Try again.")
		return
	elif not isStopInSubway(endDestination):
		print("End Destination is not in Subway. Try again.")
		return

	# This is a special helper function to help with how I have set up the graph. Because once again, we do not need to know where the exact stops are if they are not transfer stops
	# I have a nodeifier which will either return a transfer stop (if the entered value is a transfer stop) or the line that the stop lies on.
	startNew = nodeifyLocation(startDestination)
	endNew = nodeifyLocation(endDestination)

	# Answer to Question 3. I have this wrapped in a cleaner to return the correct result. Make sure to look at that method for the reasoning. Essentailly, I am returning the shortest path, but
	# we only want to know the routes, not the stops. So I need to clear out the stops.
	print("The Path from " + startDestination + " to " + endDestination)
	print(cleanUpSubwayPath(findSubwayPath(routeToRouteMapFinal, startNew, endNew)))



#Returns the name of the stops given the route
def getSubwayStops(route) -> list:
	stopList = []
	response = requests.get("https://api-v3.mbta.com/stops?filter[route]="+route)


	text = json.dumps(response.json()['data'])
	dictFromJson = json.loads(text)

	for stop in dictFromJson:
		stopList.append(stop['attributes']['name'])

	return stopList

# For each route, we go through each stop and see if we have added the routes which go through it
# If this is the first time the stop is seen, let's just add it to the Map with the route.
# If this is not the first time the stop is seen, append the route to the list of routes
def getTransferStops() -> dict:
	global routeStopMap
	transferStops = {}
	for route in routeStopMap:
		for stop in routeStopMap[route]:
			if stop in transferStops:
				transferStops[stop].append(route)
			else:
				transferStops[stop] = [route]

	return transferStops

# Potentially we could use another global variable, but don't really feel like it's necessary.
# This is the transformation part.
# Taking the list of Stops and the Route they transfer to, we trim these down so that we only look at stops that have 2 or more routes.
# The output is mentioned above. Basically we are populating the edges here.
def transformTransferStopOfRoute(stopsTransferMap) -> (dict, dict):
	holderStopsTransfer = {}
	holderTransferLine = {}
	for stop in stopsTransferMap:
		#print(stop)
		if len(stopsTransferMap[stop])<2:
			continue
		else:
			for route in stopsTransferMap[stop]:
				if stop not in holderTransferLine:
					holderTransferLine[stop] = [route]
				else:
					holderTransferLine[stop].append(route)

				if route not in holderStopsTransfer:
					holderStopsTransfer[route] = [stop]
				else:
					holderStopsTransfer[route].append(stop)
	
			
	return (holderStopsTransfer, holderTransferLine)

#Straightforward min stop and max stop evaluators
def minStop():
	global routeStopMap
	minRoute = None
	minValue = float("inf")

	for route in routeStopMap:
		if minValue > len(routeStopMap[route]):
			minRoute = route
			minValue = len(routeStopMap[route])

	return (minRoute, minValue)


def maxStop():
	global routeStopMap
	maxRoute = None
	maxValue = -float("inf")

	for route in routeStopMap:
		if maxValue < len(routeStopMap[route]):
			maxRoute = route
			maxValue = len(routeStopMap[route])


	return (maxRoute, maxValue)
# These Functions are not used but I had started on them to solve Q3 a different way. 
# Effectively, I would have created a final Map that had routes mapped to the routes they could access
# This unfortunately did not work, as I did not entirely account for cycles that could exist. 
# def getRouteToRoute(transferRouteMap, routeStopMap) -> dict:
# 	routeOfRouteMap = {}

# 	for route in transferRouteMap:
# 		#print(route)
	
# 		listOfRoutes = []
# 		for stop in transferRouteMap[route]:
			
				
# 			listOfRoutes = routeStopMap[stop]
			
# 			if route not in routeOfRouteMap.keys():

# 				routeOfRouteMap[route] = listOfRoutes
				
# 			else:

# 				routeOfRouteMap[route].extend(listOfRoutes)

# 				routeOfRouteMap[route]=list(set(routeOfRouteMap[route]))


# 	routeOfRouteMap=cleanUpRouteToRouteMap(routeOfRouteMap)

# 	return routeOfRouteMap

#Just a clean up function to remove the route itself from the mapping of routes you can access. (Trivial Case: You can access Red from Red)
# def cleanUpRouteToRouteMap(routeToRouteMap) -> dict:

# 	for key in routeToRouteMap:
# 		if(key in routeToRouteMap[key]):
# 			routeToRouteMap[key].remove(key)


# 	return routeToRouteMap


# Utilized a BFS to find the shortest path.
# Once again, could use global variables here, but choosing not to.
# We keep adding the edges created before to the double ended queue. 
# Queue the start -> search the edges -> if we have not explored that node yet, add it to the queue.
# Each time we arrive at a new node, we basically map it to the shortest path. This works because we add the path when we visit the node first (which we can guarantee with the queue)
# Return the end point once we finish mapping the entire graph
def findSubwayPath(map, start, end):
	#print(start)
	#print(end)
	path = {start: [start]}

	queue = collections.deque()
	queue.append(start)

	while len(queue):
		prevValue = queue.popleft()

		for node in map[prevValue]:
			if node not in path:
				path[node] = path[prevValue] + [node]

				queue.append(node)

	return path[end]

# As mentioned before, we have a shortest path at this point, which includes the Routes and the Transfer Points.
# We only need the Routes, so this is just removing the Transfer Points, which we can check by looking at the Dictionary we created before with just this information
def cleanUpSubwayPath(path):
	global routeTransferStopMap

	for stop in path:
		if stop in routeTransferStopMap:
			path.remove(stop)

	return path

# Explained before. We want to return a vertex, so we make sure to return the transfer point if it is one. Or the otherwise the route the stop is on
def nodeifyLocation(location):
	global routeStopMap
	global routeToRouteMapFinal

	if location in routeToRouteMapFinal:
		return location
	else:
		for route in routeStopMap:

			if location in routeStopMap[route]:

				return route
	return None		

# just checks to make sure the stop exists				
def isStopInSubway(stop):
	global routeStopMap

	for route in routeStopMap:
		if(stop in routeStopMap[route]):
			return True

	return False


populateMaps()

