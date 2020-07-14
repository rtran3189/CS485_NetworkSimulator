import sys
import socket
import select
import threading
import neighborRouter
import packet
from heapq import heappush, heappop
# Flag used to stop the server when the user inputs quit.
flag = True

# Flag used to hold the last packet this router sent.
recentlySentPacket = ''

# Lock used to between threads when updating packets.
lock = threading.Lock()

# A priority queue used for Dijkstra's algorithm.
priorityQueue = []

"""

targetIP - String, the ip address of the packet being searched for.
targetPort - String, the port number of the packet being searched for.
receivedPackets - List of packet objects. The list of packets to search through.

checkPacketList is used to check if a packet has been already received from the sender. checkPacketList compares each
packets sourceIP and sourcePort with the passed targetIP and targetPort. If a matching packet is found then true is 
returned and the loop is stopped, otherwise false is returned to indicate that the packet is not in the list.
"""


def checkPacketList(targetIP, targetPort, receivedPackets):
    #  used to indicate if the packet exists in the receivedPackets list or not.
    packetFound = False

    for packet in receivedPackets:

        # Find the correct router this message was received from.
        if packet.sourceIP == targetIP and int(packet.sourcePort) == int(targetPort):
            packetFound = True
            break

    return packetFound


"""

routers - List of neighborRouter objects, the neighbors of this router.
receivedData - String, the link state packet this router received.
routerLog - File pointer that is used to write log updates.
receivedPackets - List of packet objects, this is the list packets this router has received. 

noDijkstraMethod is used for broadcasting without using Dijkstra's. It starts by using checkPacketList to determine if
the passed packet information is already in the receivedPackets list. That is have we already received a packet from 
this sender. If checkPacketList returns false, then we have not received a packet from this sender. We then create 
a packet object from the packet string and add it to the receivedPackets list, then we forward this packet to 
all of this routers neighbors, and write an entry to the log file.

If checkPacketList returned true then this router has received a packet from this source before. We create a counter
to keep track of the index of the packet we are updating. Next we loop through each of the packets in the
receivedPackets list comparing each packets ip address and port number to those in the received packet. When the packet 
is found we check the received packets floodControlNumber with the found packets value. If the received packets 
value is higher we update the routers received packet list with the update information, forward the packet to each
of the routers neighbors, write a log entry, and break from the loop returning the updated receivedPackets list. If the
floodControlNumber received was smaller than the one in the list we drop the packet and write a log entry.  
"""


def noDijkstraMethod(routers, receivedData, routerLog, receivedPackets):

    # Separate the string for easier usage.
    sourceIP = receivedData[0]
    sourcePort = receivedData[1]
    sourceFloodControlNum = receivedData[2]

    # Concat the values passed into the original link state string.
    packetString = sourceIP + " " + sourcePort + " " + sourceFloodControlNum

    # if a packet is not in the recently received packet list add it to the list.
    if not checkPacketList(sourceIP, sourcePort, receivedPackets):

        # Create the new packet from the sent data and append it to the received list.
        receivedPackets.append(packet.Packet(sourceIP, sourcePort, sourceFloodControlNum))

        # Forward the messages to the neighboring routers.
        for router in routers:
            router.sendMessage(packetString)

            # Update the log file
            routerLog.write(sourceIP + " " + sourcePort + " " + router.ip + " " + str(router.port) + " Broadcast message Forward\n")
    else:

        # counter used to update an entry in our received packet list.
        index = 0

        # Find the recent received packet.
        for recentPacket in receivedPackets:

            # Find the correct router this message was received from.
            if recentPacket.sourceIP == sourceIP and int(recentPacket.sourcePort) == int(sourcePort):

                # If the flood control number is less than the new one update our packet and send messages
                if int(recentPacket.floodControlNum) < int(sourceFloodControlNum):

                    # Update the packet entry
                    receivedPackets[index] = packet.Packet(sourceIP, sourcePort, sourceFloodControlNum)

                    # forward the packets to the neighboring routers
                    for routerB in routers:
                        routerB.sendMessage(packetString)

                        routerLog.write(
                            sourceIP + " " + sourcePort + " " + routerB.ip + " " + str(routerB.port) + " Broadcast message Forwarded\n")

                    # update the router log.
                    # routerLog.write(sourceIP + " " + sourcePort + " forwarded \n")
                    break

                # If the recent packets control number was higher we drop the packet.
                else:
                    routerLog.write(sourceIP + " " + sourcePort + " No destination IP" + " N/A" + " Broacast message Dropped\n")
                    break

            # Update the index value if the current packet didn't match the source info.
            else:
                index = index + 1

    # return the updated receivedPackets list
    return receivedPackets


# This method will use recursion to find the shortest path to all routers.
# Takes in a list of routers as its neighbors and itself.
def useDijkstraMethod(routers, selfRouter):
    # Iterate through the list of routers
    for i in range (len(routers)):
        # This print statement is for debugging purposes.
        #print("%d: %s\t%s\t%f" % (i, routers[i].ip, routers[i].value, routers[i].totalDistance))
        # Grab current router out of the neighbor router list and its distance.
        currentRouter = routers[i]
        print(i, currentRouter)
        currentRouterValue = float(routers[i].value)
        # First step of Dijkstra's. If the total value(cost) of the router is greater than the
        # individual costs, update it and push it to the queue.
        if currentRouter.totalDistance > currentRouterValue + selfRouter.totalDistance:
            currentRouter.previousRouter = selfRouter
            currentRouter.totalDistance = currentRouterValue + selfRouter.totalDistance
            heappush(priorityQueue, (currentRouter.totalDistance, currentRouter))
    # Set the router's visited status to true.
    routers[i].visited = True

    # Pop off the next router in the queue and perform same operations recursively.
    (currentRouterValue, nextRouter) = heappop(priorityQueue)
    if not nextRouter.visited:
        useDijkstraMethod(routers, nextRouter)

# Gets the shortest path to a destination router. Prints out the list
# of IPs as the path.
def getShortestPath(dstRouter):
    currentRouter = dstRouter
    ipList = [dstRouter.ip]
    while currentRouter.ip != node.previousRouter.ip:
        currentRouter = currentRouter.previousRouter
        ipList.append(currentRouter.ip)
    ipList.reverse()
    return ipList


"""

ip - String, the ip address this router should use for a udp connection
port - String, the port number this router should use for a udp connection
routerName - String, the name of this router.
routers - List of neighborRouter objects, a list of neighboring routers.

server is used to handle incoming communication and to forward broadcasted messages to it neighbors. The server starts
by creating a file name for the router log, this is the name of the router followed by Log.txt. The server then opens 
the created file to write its log entries to. Next the server creates and binds the server socket used for the udp 
connection to the passed ip and port number. Another socket is created that allows the use of select.select to be
used across windows and linux machines. Next a receivedPackets list is created, this list will hold packets that 
the server has received. Next the main loop starts, in the loop two lists are created each iteration the socket
list that contains the server socket and the write list that contains the socket used for the select.select function.
After this another loop is used to check the server socket for incoming messages.If a message is received on the 
server socket we start to process it. The passed data is read and separated by the message and the address that passed
the message, next the data is decoded and parsed using split to split the string up by spaces. Next we verify that
the ip address and port in the passed packet doesn't match this routers information. If it does we write to the log file
that the message was dropped. If not we get the number of arguments in the packet string, if there are only three 
arguments then the no Dijkstra broadcast method was used and we forward the message and  update the receivedPackets list 
using the no Dijkstra's method.
"""


def server(ip, port, routerName, routers):
    localIP = ip
    localPort = int(port)
    bufferSize = 1024

    # Set the router log file name
    fileName = routerName + "Log.txt"

    # Open the router log file and overwrite the current contents.
    routerLog = open(fileName, "w")

    # Create server socket and bind it
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))

    # Create client socket - This is not only used to prevent select from hanging on the server socket.
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # List to hold the recently received packets
    receivedPackets = []

    while flag:
        # list of inputs from user and from the server socket.
        socket_list = [UDPServerSocket]

        # List of write sockets
        write_list = [UDPClientSocket]

        # Create the select lists.
        read_sockets, write_sockets, error_sockets = select.select(socket_list, write_list, [])

        # Loop through the input sockets
        for sock in read_sockets:

            # If the server socket received a message
            if sock == UDPServerSocket:

                # Receive the message up to the set buffer size.
                byteAddressPair = sock.recvfrom(bufferSize)

                data = byteAddressPair[0]
                address = byteAddressPair[1]

                # decode the data
                data = data.decode()

                # Split the packet string
                data = data.split()

                # verify the packet isn't the same one this router sent.
                if data[0] != localIP and data[1] != localPort:

                    # if the length of the message is 3 then this was sent via the no Dijkstra method.
                    if len(data) == 3:
                        # Call the noDijkstraMethod to continue broadcast
                        receivedPackets = noDijkstraMethod(routers, data, routerLog, receivedPackets)
                else:
                    # TODO this is currently writing out the packet control number not the value associated link value
                    routerLog.write(data[0] + " " + data[1] + " NA NA Broadcast Message Dropped\n")

    # Close the router log when finished
    routerLog.close()


"""

routers = A list of all the routers that are this routers neighbors, a list of neighborRouter objects.

client is used to handel the user input on each router. The client method updates two global variables: flag and 
recentlySentPacket. Flag is used to stop the server main loop and exit the program gracefully. recentlySentPacket is a
packet object, this is used to create the link state packets that are broadcasted to its neighbors. The client loop 
starts by displaying a message to indicate it is waiting for input. If the user enters "quit" the flag variable is 
set to false to exit the server loop and the program is shut down. If the user enters "broadcast,noDijkstra" then
an updated packet is created and sent to each of the neighbor routers in routers. If the user enters anything else
an error message is displayed.
"""


def client(routers, selfRouter):
    # A global flag that tells the server to shutdown when the user enters quit.
    global flag

    # allow the client to update the packet.
    global recentlySentPacket

    # Main client loop, gets user input and then forwards the message.
    while True:
        # Wait for user input with an indication message.
        userInput = input("What message would you like to send?\n")

        # if the user has input quit shut down the router.
        if userInput == "quit":
            flag = False
            break

        # If the user selected to broadcast without using Dijkstra
        elif userInput == "broadcast,noDijkstra":

            # acquire lock to update the recentlySentPacket
            with lock:
                # Generate the updated packet to send.
                packetString = recentlySentPacket.noDijkstraString()

            # Send the packetString to all neighboring routers.
            for router in routers:
                router.sendMessage(packetString)

        elif userInput == "broadcast,withDijkstra":
            # Create a variable that has the list of routers in the file for Dijkstra's.
            listOfRoutersFile = "Routers.txt"
            listOfRouters = []

            # Parse the passed file line by line
            with open(listOfRoutersFile) as fp:
                # set line to the first read line
                line = fp.readline()

                # loop through each line of the router file.
                while line:
                    # Strip the line of any hidden characters and split the string by spaces.
                    line = line.strip().split()
                    listOfRouters.append(line)
                    # create the initial packet object for each routerNeighbor object.
                    #initialPacket = packet.Packet(line[0], line[1], 0)

                    # Create a new router neighbor for the given line and append it to the list of neighbors.
                    #routerNeighbors.append(neighborRouter.Neighbor(line[0], line[1], line[2], initialPacket))

                    # Creates a router object that refers to itself.
                    #selfRouter = neighborRouter.Neighbor(sourceIP, sourcePort, "0", initialPacket)

                    # update line.
                    line = fp.readline()

            #print('TEST: ', listOfRouters)
            useDijkstraMethod(listOfRouters, selfRouter)
            for r in routers:
                print ('Route: ', getShortestPath(r))


        # If the user entered anything other then the allowed input print out message.
        elif userInput != '':
            print("Unrecognized command\n")


"""

This is the main function, it starts by getting the four arguments supplied via the command line. The first argument
should be the source IP, i.e. the ip address you want to assign this router. The second is the source port that you 
want this router to be open to. The third argument is the name you want to assign this router. This will be used to 
create a log file with the same name. Next it creates a packet object that is saved on the router that will be used 
for writing out new packets with in the client. Next it parses the passed file line by line and coverts the lines
into routerNeighbor objects, these are used to broadcast messages to. It starts by striping the line of any extraneous 
characters such as new lines and carriage returns and then splits the string up by the spaces. Once the data has been 
parsed the routerNeighbor objects are stored in a list for the router to use. Once the file has been parsed a client
thread is created with the client method and the routerNeighbors list an argument and started, then the server is
started on the main thread. When the client is finished join is called to ensure thread hygiene. 
"""
if __name__ == "__main__":

    sourceIP = sys.argv[1]
    sourcePort = sys.argv[2]
    routerName = sys.argv[3]
    routerFile = sys.argv[4]

    # Create the initial packet for this router
    recentlySentPacket = packet.Packet(sourceIP, sourcePort, 0)

    # List of routerNeighbor objects that the router will use to broadcast to.
    routerNeighbors = []

    # Parse the passed file line by line
    with open(routerFile) as fp:

        # set line to the first read line
        line = fp.readline()

        # loop through each line of the router file.
        while line:
            # Strip the line of any hidden characters and split the string by spaces.
            line = line.strip().split()

            # create the initial packet object for each routerNeighbor object.
            initialPacket = packet.Packet(line[0], line[1], 0)

            # Create a new router neighbor for the given line and append it to the list of neighbors.
            routerNeighbors.append(neighborRouter.Neighbor(line[0], line[1], line[2], initialPacket))

            # Creates a router object that refers to itself.
            selfRouter = neighborRouter.Neighbor(sourceIP, sourcePort, "0", initialPacket)

            # update line.
            line = fp.readline()

    # Create client thread that will process user input
    client = threading.Thread(target=client, args=(routerNeighbors, selfRouter))

    # Start client thread
    client.start()

    # Start router
    server(sourceIP, sourcePort, routerName, routerNeighbors)

    # wait for client thread to finish
    client.join()
