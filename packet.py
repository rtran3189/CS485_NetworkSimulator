"""

The packet class is used to create packet objects and their string counter parts to be used in a router.
"""


class Packet:

    """

    sourceIP - String, the sourceIP address of this packet.
    sourcePort - String, the source port number of this packet.
    floodControlNum - String, the current flood control value of this packet.

    initializes a packet object.
    """

    def __init__(self, sourceIP, sourcePort, floodControlNum):
        self.sourceIP = sourceIP
        self.sourcePort = sourcePort
        self.floodControlNum = floodControlNum


    """
    
    noDijkstraString converts this packet to a noDijkstraString that will be broadcasted to other routers. The method
    starts by increasing this packets floodControlNum by one as the only place to create this packet is in client 
    method, this value is then converted to a string. Finally all the strings are concatenated together with spaces
    to delimit them, this string is then returned.  
    """

    # Converts this packets information into a string to be sent to other routers.
    def noDijkstraString(self):

        # increment the flood control number by one
        self.floodControlNum = self.floodControlNum + 1

        # convert the flood control number to a string
        floodControlString = str(self.floodControlNum)

        # Convert the packet information into a string to be sent.
        packetToString = self.sourceIP + " " + self.sourcePort + " " + floodControlString

        return packetToString
