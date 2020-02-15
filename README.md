# mbtaAPI

Hi! This is the ReadMe.

For starters, you will need Python3. The only library you should need to install is the Python Requests library, which can be done through: pip3 install requests

To run the code, just run python3 main.py {stop1_id} {stop2_id}

Some sample tests would be: python3 main.py "Ashmont" "Arlington", python3 main.py "North Station" "Wonderland"

I have included documentation in the code itself.

Some Possible Improvements:
1) Adding a UI interface to interact with this code easier. Could also make the parameters for the path calculator user input instead of having to be entered through the command line

2) Improvements could be made to the graph building process. Making each stop its own node would be helpful for future improvements and extending the functionality. I have used BFS as a shortest path, but I could have also added weights to the edges instead of keeping them at the same value. I would be able to find the actually shortest path instead of just the shortest number of switches

3) Cut down on nested for loops. I use quite a few nested for loops to give some of my helper functions O(n^2) runtimes. This should be looked to be cut down. This could be accomplished through storing the maps in database tables for instant retrieval (or near instant retrieval). This would cut down on runtime pretty significantly, especially since the data we are pulling is unlikely to change significantly

4) Creating a class for each stop/route. I thought about this as I was setting up the node graph, but having each stop or route could allow us to better return values instead of relying on functions to do this task across all of the stops or all of the route. This would allow us to focus on the stops we need to look at, as opposed to having to put all the data into dictionaries several times. This could connect to 3.

Thank you so much for your time!

If you have any questions, don't hesitate to reach out to me at wilson.xu.94@gmail.com



