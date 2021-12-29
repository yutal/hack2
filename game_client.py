import socket
import time
import struct
import multiprocessing
import getch

CBOLD = '\33[1m'
CGREY = '\33[90m'
CSELECTED = '\33[7m'
CEND = '\33[0m'


class GameClient:

    def __init__(self, TEST):
        """
        Constractor for GameClient
        Parameters:
            TEST (boolean): Run on Test server or Div server
        """

        # Team Name !
        self.teamName = 'Maccabi Haifa yutal'

        # Initiate server UDP socket
        self.gameClientUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Allow more then 1 Client run on the same Addr / Port (More for testing then playing)
        self.gameClientUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        if TEST:
            self.gameClientUDP.bind(('172.99.255.255', 13117))
        else:
            self.gameClientUDP.bind(('172.1.255.255', 13117))

        print("Client started, listening for offer requests...")

        # Initiate server TCP socket
        self.gameClientTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Starting to look for a Game Server
        self.LookingForGame()

    def LookingForGame(self):
        """
        Looking for Game to play in
        """
        # Always working, our client is a Hard working one
        while True:
            self.gameClientUDP.settimeout(2)
            try:
                # Get the broadcast message
                data, addr = self.gameClientUDP.recvfrom(8)
                # Unpacking the broadcast message
                message = struct.unpack('IbH', data)
                # Getting the server Port
                serverPort = message[2]

                # Checking message Magic Cookie
                # 0xfeedbeef
                if message[0] != 0xabcddcba:
                    continue

                # Got the offer, now to connect
                print("Received offer from {}, attempting to connect...".format(addr[0]))
                # Data is good, connecting to the server
                self.ConnectingToGame(addr[0], int(serverPort))
            except:
                pass

    def ConnectingToGame(self, addr, gamePort):
        """
        Connecting to Game Server
        Parameters:
            addr (str): Game Server addr
            gamePort (int): Game Server Port
        """
        try:
            self.gameClientTCP.settimeout(10)
            # Connecting to the TCP Game Server
            self.gameClientTCP.connect((addr, gamePort))
            # Sending to the Server our Team Name
            self.gameClientTCP.sendall((self.teamName + '\n').encode())
            # Waiting for openning message
            data = None
            try:
                data = self.gameClientTCP.recv(1024)
            except:
                pass
            if data is None:
                print(f'{CBOLD}{CGREY}{CSELECTED}No Welcome Message has been received. Lets find new Server.{CEND}')
                raise Exception('Connected Server sucks.')
            else:
                print(data.decode())
            # Start the game !
            self.PlayGame()
            print('Server disconnected, listening for offer requests...')
        except:
            pass
        self.gameClientTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def PlayGame(self):
        """
        Playing the Game.
        Press as many keyboard keys as you can in 10 secs !
        """
        # Initiate PressKeys Thread
        tPressKeys = multiprocessing.Process(target=self.PressKeys)
        # Start the Thread
        tPressKeys.start()
        # Give the Thread 10 secs to live
        tPressKeys.join(10)
        if tPressKeys.is_alive():
            tPressKeys.terminate()
        # Waiting 3 sec for GameOver message
        self.gameClientTCP.settimeout(3)
        data = None
        # Getting the GameOver Message or if time pass moving on
        try:
            data = self.gameClientTCP.recv(1024)
        except:
            pass
        if data is None:
            print(f"{CBOLD}{CGREY}{CSELECTED}No GameOver Message, but it's over..{CEND}")
        else:
            print(data.decode())

    def PressKeys(self):
        # 10 secs to press, GO GO GO !
        stop_time = time.time() + 10
        while time.time() < stop_time:
            try:
                # Getting the pressed key
                char = getch.getch()
                # Sending it to the Server
                self.gameClientTCP.sendall(char.encode())
            except:
                pass


GameClient(False)