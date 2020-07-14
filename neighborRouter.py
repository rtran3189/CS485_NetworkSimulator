import socket


"""

The neighbor class is used to create a neighboring router object and to to send messages to it.
"""


class Neighbor:

    
    """

    ip - String, ip address of this neighboring router.
    port - String, port number of this neighboring router.
    value - the cost between the router this neighbor was created in and itself.
    initialPacket - a packet object, not used at the moment by the neighboring router but by the base router.

    the init function initializes this neighboring router. It sets its ip address, port, value and initial packet
    to the value passed. Next it creates a socket that will be used to write to this router.
    """
    def __init__(self, ip, port, value, initialPacket):
        self.ip = ip
        self.port = int(port)
        self.value = value
        self.writeSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.serverAddressPort = (self.ip, self.port)
        self.lastReceivedPacket = initialPacket
        self.totalDistance = float('Inf')
        self.previousRouter = None
        self.visited = False

    """
    
    message - String, the link state string that will be written to this router. 
    
    sendMessage is used to send the link state string created in the router to send to this neighboring router.
    """

    def sendMessage(self, message):

        # encode the message to bytes.
        bytesToSend = str.encode(message)

        # send the message to the router.
        self.writeSocket.sendto(bytesToSend, self.serverAddressPort)
