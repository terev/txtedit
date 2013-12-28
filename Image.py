from pygame import image

class img:
    def __init__(self, image):
        self.image = image
        self.width = self.image.get_rect()[2]
        self.height = self.image.get_rect()[3]
