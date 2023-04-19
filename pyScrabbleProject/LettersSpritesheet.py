import pygame


class SpriteSheet:
    def __init__(self, file_name):
        try:
            self.sheet = pygame.image.load(file_name).convert()
        except pygame.error as msg:
            print(f'Cannot load spritesheet image: {file_name}')
            raise SystemExit(msg)

    def get_image(self, rect, color_key=None):
        """Retrieve image from given rectangle"""
        rectangle = pygame.Rect(rect)
        img = pygame.Surface(rectangle.size).convert()
        img.blit(self.sheet, (0, 0), rectangle)
        if color_key is not None:
            if color_key == -1:
                color_key = img.get_at((0, 0))
            img.set_colorkey(color_key, pygame.RLEACCEL)
        return img

    def get_images(self, rectangles, color_key=None):
        """Load multiple images using a list of coordinates"""
        return [self.get_image(rect, color_key) for rect in rectangles]

    def load_image_strip(self, rectangle, img_count, color_key=None):
        """Load a strip of images and return them as a list"""
        coords = [(rectangle[0] + rectangle[2] * i, rectangle[1], rectangle[2], rectangle[3])
                  for i in range(img_count)]
        return self.get_images(coords, color_key)

