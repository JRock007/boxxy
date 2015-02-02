from pygame.locals import *
import pygame
import math
import os
import sys
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep
import eztext

if sys.platform == "win32":
    import pygame._view

# Set root path
try:
    approot = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    approot = os.path.dirname(os.path.abspath(sys.argv[0]))

if(".exe" in approot):
    approot = approot.replace("boxxy.exe", "")


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


class BoxesGame(ConnectionListener):
    def initSound(self):
        pygame.mixer.music.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "music.wav"))
        self.winSound = pygame.mixer.Sound(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "win.wav"))
        self.loseSound = pygame.mixer.Sound(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "lose.wav"))
        self.placeSound = pygame.mixer.Sound(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "place.wav"))
        if self.enableSound:
            pygame.mixer.music.play()

    def Network_close(self, data):
        sys.exit()

    def Network_yourturn(self, data):
        #  torf = short for true or false
        self.turn = data["torf"]

    def Network_startgame(self, data):
        self.running = True
        self.num = data["player"]
        self.gameid = data["gameid"]

    def Network_place(self, data):
        if self.enableSound:
            self.placeSound.play()

        #  get attributes
        x = data["x"]
        y = data["y"]
        hv = data["is_horizontal"]
        #  horizontal or vertical
        if hv:
            self.boardh[y][x] = True
        else:
            self.boardv[y][x] = True

    def __init__(self):
        self.justplaced = 10
        self.boardh = [[False for x in range(6)] for y in range(7)]
        self.boardv = [[False for x in range(7)] for y in range(6)]
        #  1
        pygame.init()
        pygame.font.init()
        width, height = 489, 389
        #  2
        # initialize the screen
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Boxxy")
        # 3
        # initialize pygame clock
        self.clock = pygame.time.Clock()
        # initialize the graphics
        self.initGraphics()
        self.turn = True
        self.owner = [[0 for x in range(6)] for y in range(6)]
        self.me = 0
        self.otherplayer = 0
        self.didiwin = False
        self.running = False

        enableSound = textInput(self.screen, 5, "Enable sound and music: ")
        if enableSound == "1" or enableSound.lower() == "true":
            self.enableSound = True
        else:
            self.enableSound = False

        self.initSound()

        address = textInput(self.screen, 30, "Address of Server: ")
        try:
            if not address:
                host, port = "localhost", 8000
            else:
                host, port = address.split(":")
            self.Connect((host, int(port)))
        except:
            print("Error Connecting to Server")
            print("Usage:", "host:port")
            print("e.g.", "localhost:31425")
            sys.exit()

        width, height = 389, 489
        self.screen = pygame.display.set_mode((width, height))

        print("Boxes client started, waiting for server and/or the other player")
        self.running = False
        self.owner = [[0 for x in range(6)] for y in range(6)]
        while not self.running:
            # events for txtbx
            events = pygame.event.get()
            # process other events
            for event in events:
                # close it x button si pressed
                if event.type == QUIT:
                    sys.exit()
            self.Pump()
            connection.Pump()
            sleep(0.05)
        print("Starting game")
        # determine attributes from player #
        if self.num == 0:
            self.turn = True
            self.marker = self.greenplayer
            self.othermarker = self.blueplayer
        else:
            self.turn = False
            self.marker = self.blueplayer
            self.othermarker = self.greenplayer

    def drawBoard(self):
        #  This draws all of the lines other than the edges.
        for x in range(6):
            for y in range(6):
                if not self.boardh[y][x]:
                    self.screen.blit(self.normallineh, [(x)*64+5, (y)*64])
                else:
                    self.screen.blit(self.bar_doneh, [(x)*64+5, (y)*64])
                if not self.boardv[y][x]:
                    self.screen.blit(self.normallinev, [(x)*64, (y)*64+5])
                else:
                    self.screen.blit(self.bar_donev, [(x)*64, (y)*64+5])
        for edge in range(6):
            if not self.boardh[6][edge]:
                self.screen.blit(self.normallineh, [edge*64+5, 6*64])
            else:
                self.screen.blit(self.bar_doneh, [edge*64+5, 6*64])
            if not self.boardv[edge][6]:
                self.screen.blit(self.normallinev, [6*64, edge*64+5])
            else:
                self.screen.blit(self.bar_donev, [6*64, edge*64+5])
        # draw separators
        for x in range(7):
            for y in range(7):
                self.screen.blit(self.separators, [x*64, y*64])

    def drawHUD(self):
        # draw the background for the bottom:
        self.screen.blit(self.score_panel, [0, 389])
        # create font
        myfont = pygame.font.Font(None, 32)

        # create text surface
        label = myfont.render("Your Turn:", 1, (255, 255, 255))

        # draw surface
        self.screen.blit(label, (10, 400))
        self.screen.blit(self.greenindicator if self.turn else self.redindicator, (130, 395))
        # same thing here
        myfont64 = pygame.font.Font(None, 64)
        myfont20 = pygame.font.Font(None, 20)

        scoreme = myfont64.render(str(self.me), 1, (255, 255, 255))
        scoreother = myfont64.render(str(self.otherplayer), 1, (255, 255, 255))
        scoretextme = myfont20.render("You", 1, (255, 255, 255))
        scoretextother = myfont20.render("Other Player", 1, (255, 255, 255))

        self.screen.blit(scoretextme, (10, 425))
        self.screen.blit(scoreme, (10, 435))
        self.screen.blit(scoretextother, (280, 425))
        self.screen.blit(scoreother, (340, 435))

    def update(self):
        if self.me+self.otherplayer == 36:
            self.didiwin = True if self.me > self.otherplayer else False
            return 1
        # sleep to make the game 60 fps
        self.justplaced -= 1
        self.clock.tick(60)
        connection.Pump()
        self.Pump()
        # clear the screen
        self.screen.fill(0)
        self.drawBoard()
        self.drawHUD()
        self.drawOwnermap()

        for event in pygame.event.get():
            # quit if the quit button was pressed
            if event.type == pygame.QUIT:
                sys.exit()

        # update the screen
        # 1
        mouse = pygame.mouse.get_pos()

        # 2
        xpos = int(math.ceil((mouse[0]-32)/64.0))
        ypos = int(math.ceil((mouse[1]-32)/64.0))

        # 3
        is_horizontal = abs(mouse[1] - ypos*64) < abs(mouse[0] - xpos*64)

        # 4
        ypos = ypos - 1 if mouse[1] - ypos*64 < 0 and not is_horizontal else ypos
        xpos = xpos - 1 if mouse[0] - xpos*64 < 0 and is_horizontal else xpos

        # 5
        board = self.boardh if is_horizontal else self.boardv
        isoutofbounds = False

        # 6
        try:
            if not board[ypos][xpos]: self.screen.blit(self.hoverlineh if is_horizontal else self.hoverlinev, [xpos*64+5 if is_horizontal else xpos*64, ypos*64 if is_horizontal else ypos*64+5])
        except:
            isoutofbounds = True
            pass
        if not isoutofbounds:
            alreadyplaced = board[ypos][xpos]
        else:
            alreadyplaced = False
        if pygame.mouse.get_pressed()[0] and not alreadyplaced and not isoutofbounds and self.turn and self.justplaced <= 0:
            self.justplaced = 10
            if is_horizontal:
                self.boardh[ypos][xpos] = True
                self.Send({"action": "place", "x": xpos, "y": ypos, "is_horizontal": is_horizontal, "num": self.num, "gameid": self.gameid})
            else:
                self.boardv[ypos][xpos] = True
                self.Send({"action": "place", "x": xpos, "y": ypos, "is_horizontal": is_horizontal, "num": self.num, "gameid": self.gameid})
        pygame.display.flip()

    def Network_win(self, data):
        self.owner[data["x"]][data["y"]] = "win"
        self.boardh[data["y"]][data["x"]] = True
        self.boardv[data["y"]][data["x"]] = True
        self.boardh[data["y"]+1][data["x"]] = True
        self.boardv[data["y"]][data["x"]+1] = True
        # add one point to my score
        if self.enableSound:
            self.winSound.play()
        self.me += 1

    def Network_lose(self, data):
        self.owner[data["x"]][data["y"]] = "lose"
        self.boardh[data["y"]][data["x"]] = True
        self.boardv[data["y"]][data["x"]] = True
        self.boardh[data["y"]+1][data["x"]] = True
        self.boardv[data["y"]][data["x"]+1] = True
        # add one to other players score
        if self.enableSound:
            self.loseSound.play()
        self.otherplayer += 1

    def initGraphics(self):
        self.normallinev = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "normalline.png"))
        self.normallineh = pygame.transform.rotate(pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "normalline.png")), -90)
        self.bar_donev = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "bar_done.png"))
        self.bar_doneh = pygame.transform.rotate(pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "bar_done.png")), -90)
        self.hoverlinev = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "hoverline.png"))
        self.hoverlineh = pygame.transform.rotate(pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "hoverline.png")), -90)
        self.separators = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "separators.png"))
        self.redindicator = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "redindicator.png"))
        self.greenindicator = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "greenindicator.png"))
        self.greenplayer = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "greenplayer.png"))
        self.blueplayer = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "blueplayer.png"))
        self.winningscreen = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "youwin.png"))
        self.gameover = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "gameover.png"))
        self.score_panel = pygame.image.load(os.path.join(os.environ.get("RESOURCEPATH", approot), "resources", "score_panel.png"))

    def drawOwnermap(self):
        for x in range(6):
            for y in range(6):
                if self.owner[x][y] != 0:
                    if self.owner[x][y] == "win":
                        self.screen.blit(self.marker, (x*64+5, y*64+5))
                    if self.owner[x][y] == "lose":
                        self.screen.blit(self.othermarker, (x*64+5, y*64+5))

    def finished(self):
        self.screen.blit(self.gameover if not self.didiwin else self.winningscreen, (0, 0))
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            pygame.display.flip()

bg = BoxesGame()  # __init__ is called right here
while 1:
    if bg.update() == 1:
        break
bg.finished()
