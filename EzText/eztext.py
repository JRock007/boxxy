# input lib
from pygame.locals import *
import pygame


class ConfigError(KeyError):
    pass


class Config:
    """ A utility for configuration """
    def __init__(self, options, *look_for):
        assertions = []
        for key in look_for:
            if key[0] in options.keys():
                exec('self.'+key[0]+' = options[\''+key[0]+'\']')
            else:
                exec('self.'+key[0]+' = '+key[1])
            assertions.append(key[0])
        for key in options.keys():
            if key not in assertions:
                raise ConfigError(key+' not expected as option')


class Input:
    """ A text input for pygame apps """
    def __init__(self, **options):
        """ Options: x, y, font, color, maxlength, prompt """
        self.options = Config(options, ['x', '0'], ['y', '0'], ['font', 'pygame.font.Font(None, 25)'],
                              ['color', '(0,0,0)'],
                              ['maxlength', '-1'], ['prompt', '\'\''], ['focus', 'False'])
        self.x = self.options.x
        self.y = self.options.y
        self.font = self.options.font
        self.color = self.options.color
        self.maxlength = self.options.maxlength
        self.prompt = self.options.prompt
        self.value = ''
        self.shifted = False
        self.pause = 0
        self.focus = self.options.focus

    def set_pos(self, x, y):
        """ Set the position to x, y """
        self.x = x
        self.y = y

    def set_font(self, font):
        """ Set the font for the input """
        self.font = font

    def draw(self, surface):
        """ Draw the text input to a surface """
        text = self.font.render(self.prompt+self.value, 1, self.color)
        surface.blit(text, (self.x, self.y))

    def update(self, events):
        """ Update the input based on passed events """
        if self.focus is not True:
            return

        pressed = pygame.key.get_pressed()  # Add ability to hold down delete key and delete text
        if self.pause == 3 and pressed[K_BACKSPACE]:
            self.pause = 0
            self.value = self.value[:-1]
        elif pressed[K_BACKSPACE]:
            self.pause += 1
        else:
            self.pause = 0

        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    self.value = self.value[:-1]
                elif event.key == K_RETURN:
                    return self.value
                else:
                    carac = event.dict['unicode']
                    self.value += carac

        if len(self.value) > self.maxlength and self.maxlength >= 0:
            self.value = self.value[:-1]
