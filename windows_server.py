import PodSixNet.Channel
import PodSixNet.Server
import pygame
from pygame.locals import *
from time import sleep
from EzText import eztext
import sys

if sys.platform == "win32":
    import pygame._view

# defining some colors
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)


def textInput(screen, maxLength, prompt):
    # fill the screen w/ black
    screen.fill(black)
    ypos = 0
    deltay = 25
    txtbx = []
    # For getting the return values
    a = ['']
    # here is the magic: making the text input
    # create an input with a max length of 45,
    # and a red color and a prompt saying 'type here $i: '
    txtbx.append(eztext.Input(maxlength=maxLength,
                              color=blue, y=ypos,
                              prompt=prompt))
    ypos += deltay

    # create the pygame clock
    clock = pygame.time.Clock()
    # main loop!

    while True:
        # make sure the program is running at 30 fps
        clock.tick(30)

        # events for txtbx
        events = pygame.event.get()
        # process other events
        for event in events:
            # close it x button si pressed
            if event.type == QUIT:
                return "None"

        # clear the screen
        screen.fill(white)  # I like black better :)
        # update txtbx and get return val
        a[0] = txtbx[0].update(events)
        txtbx[0].focus = True
        txtbx[0].color = black

        # blit txtbx[i] on the screen
        txtbx[0].draw(screen)

        # Changing the focus to the next element
        # every time enter is pressed
        if a[0] != None:
            return a[0]

        # refresh the display
        pygame.display.flip()


class ClientChannel(PodSixNet.Channel.Channel):
    def Network(self, data):
        print(data)

    def Network_place(self, data):
        # deconsolidate all of the data from the dictionary

        # horizontal or vertical?
        hv = data["is_horizontal"]
        # x of placed line
        x = data["x"]

        # y of placed line
        y = data["y"]

        # player number (1 or 0)
        num = data["num"]

        # id of game given by server at start of game
        self.gameid = data["gameid"]

        # tells server to place line
        self._server.placeLine(hv, x, y, data, self.gameid, num)

    def Close(self):
        self._server.close(self.gameid)


class BoxesServer(PodSixNet.Server.Server):

    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        PodSixNet.Server.Server.__init__(self, *args, **kwargs)
        self.games = []
        self.queue = None
        self.currentIndex = 0
        print("Waiting for clients...")

    def Connected(self, channel, addr):
        print("new connection:", channel)
        if self.queue is None:
            print("Player 1 joined the game !")
            self.currentIndex += 1
            channel.gameid = self.currentIndex
            self.queue = Game(channel, self.currentIndex)
        else:
            print("Player 2 joined the game !")
            channel.gameid = self.currentIndex
            self.queue.player1 = channel
            self.queue.player0.Send({"action": "startgame", "player": 0, "gameid": self.queue.gameid})
            self.queue.player1.Send({"action": "startgame", "player": 1, "gameid": self.queue.gameid})
            self.games.append(self.queue)
            self.queue = None

    def placeLine(self, is_h, x, y, data, gameid, num):
        game = [a for a in self.games if a.gameid == gameid]
        if len(game) == 1:
            game[0].placeLine(is_h, x, y, data, num)

    def close(self, gameid):
        try:
            game = [a for a in self.games if a.gameid == gameid][0]
            game.player0.Send({"action": "close"})
            game.player1.Send({"action": "close"})
        except:
            pass

    def tick(self):
        #  Check for any wins
        #  Loop through all of the squares
        index = 0
        change = 3
        for game in self.games:
            change = 3
            for time in range(2):
                for y in range(6):
                    for x in range(6):
                        if game.boardh[y][x] and game.boardv[y][x] and game.boardh[y+1][x] and game.boardv[y][x+1] and not game.owner[x][y]:
                            if self.games[index].turn == 0:
                                self.games[index].owner[x][y] = 2
                                game.player1.Send({"action": "win", "x": x, "y": y})
                                game.player0.Send({"action": "lose", "x": x, "y": y})
                                change = 1
                            else:
                                self.games[index].owner[x][y] = 1
                                game.player0.Send({"action": "win", "x": x, "y": y})
                                game.player1.Send({"action": "lose", "x": x, "y": y})
                                change = 0
            self.games[index].turn = change if change != 3 else self.games[index].turn
            game.player1.Send({"action": "yourturn", "torf": True if self.games[index].turn == 1 else False})
            game.player0.Send({"action": "yourturn", "torf": True if self.games[index].turn == 0 else False})
            index += 1
        self.Pump()


class Game:
    def __init__(self, player0, currentIndex):
        #  whose turn (1 or 0)
        self.turn = 0
        # owner map
        self.owner = [[False for x in range(6)] for y in range(6)]
        #  Seven lines in each direction to make a six by six grid.
        self.boardh = [[False for x in range(6)] for y in range(7)]
        self.boardv = [[False for x in range(7)] for y in range(6)]
        # initialize the players including the one who started the game
        self.player0 = player0
        self.player1 = None
        # gameid of game
        self.gameid = currentIndex

    def placeLine(self, is_h, x, y, data, num):
        # make sure it's their turn
        if num == self.turn:
            self.turn = 0 if self.turn else 1
            self.player1.Send({"action": "yourturn", "torf": True if self.turn == 1 else False})
            self.player0.Send({"action": "yourturn", "torf": True if self.turn == 0 else False})
            # place line in game
            if is_h:
                self.boardh[y][x] = True
            else:
                self.boardv[y][x] = True
            # send data and turn data to each player
            self.player0.Send(data)
            self.player1.Send(data)
print("STARTING SERVER ON LOCALHOST")

pygame.init()
width, height = 500, 20
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Boxxy server")

#  try:
address = textInput(screen, 30, "Host:Port (localhost:8000): ")
if address == "None":
    sys.exit()

if not address:
    host, port = "localhost", 8000
else:
    host, port = address.split(":")
boxesServe = BoxesServer(localaddr=(host, int(port)))
while True:
    events = pygame.event.get()
    # process other events
    for event in events:
        # close it x button si pressed
        if event.type == QUIT:
            sys.exit()

    boxesServe.tick()
    sleep(0.01)
