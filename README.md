# Lab 4: Link-state Routing Simulator

### Created by Richard Tran and Eric Turnbull

This is a multi-threaded Python program that simulates a link-state routing algorithm that uses either Controlled Flooding or Dijkstra's algorithm. 

# How to run

In order to run our program, you will need to navigate to the location of your python.exe here you will then need to give the directory where this code is stored along with four arguments: The IP address where this router will reside, the port number the router should you, the name of the router, and a text file that contains the information for this router's neighbors. For example: [file path]/python.exe [file path to code] 127.0.0.1 20001 routerA routerA.txt. You will need to create 7 terminal windows to create the necessary network.

## Important Information
In our building of the simulator, we were unable to make use of the IP address and port numbers as specified in the spec. Instead, we substituted these addresses for localhost addresses such as 127.0.0.1 20001. Contained with our code are 7 text files that contain corresponding IP addresses for those found in the spec in the event that you are also unable to use the specified information. 

If you are using your own text files you will need to follow the following format to ensure compatibility:
IP address Port Number Cost

Deviation from this format will result in incorrect results, we leave it to the user to ensure that our format is adhered to. 

## Broadcasting to a Routers Neighbors
Once a router has been properly initialized you should be greeted with the message "What message would you like to send?". Here you have three options

Option 1: "quit" - This will allow the router to exit without crashing.

Option 2: "broadcast,noDijkstra" - Broadcast a link packet to the entire network without using Dijkstra's algorithm.

Option 3: "broadcast,withDijkstra" - Broadcasts using Dijkstra's algorithm and finding the shortest possible path using information from Routers.txt

## Reading a routers log file
Each router writes its own log file that is saved as routerName.txt. Inside each file, there are rows of text of the format: Source IP Source Port Destination IP Destination Port Content Forward/Drop

If a message came back to the same router that sent it the destination IP and destination port fields with show NA NA. If a server received a packet with a lower packet counter then the destination Ip will show No destination and the IP field will be NA to indicate that the packet was dropped. We were unsure what Destination IP meant in the context of controlled flooding so the Destination IP is the IP address that the packet was forwarded to.
