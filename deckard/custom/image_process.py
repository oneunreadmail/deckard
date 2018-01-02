from math import sin, cos, pi
from PIL import Image, ImageDraw
import numpy
from io import BytesIO


class WrongVertexCountError(ValueError):
    pass


class Vector:
    """Vector class for storing coordinates of vectors on 2-dimensional plane."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, number):
        return Vector(self.x * number, self.y * number)

    def __truediv__(self, number):
        return Vector(self.x / number, self.y / number)

    def __str__(self):
        return '({x}, {y})'.format(x=self.x, y=self.y)

    def __repr__(self):
        return 'Vector({x}, {y})'.format(x=self.x, y=self.y)

    def rotate(self, a):
        """Rotate vector counterclockwise by angle a."""
        self.x, self.y = cos(a) * self.x - sin(a) * self.y, sin(a) * self.x + cos(a) * self.y


class Polygon:
    """Polygon class for creating regular N-gons and storing coordinates of their vertices."""
    def __init__(self, vertex_count, center=(0, 0), side=1.0):
        if not isinstance(vertex_count, int):
            raise TypeError("Vertex count should be an integer")
        if vertex_count < 3:
            raise WrongVertexCountError("Vertex count should be greater than 2")
        self.center = Vector(center[0], center[1])
        # Radius of a regular polygon
        radius = side / (2 * sin(pi / vertex_count))
        # Inner angles in a regular polygon
        inner_angle = (vertex_count - 2) * pi / vertex_count
        # Angle between one vector side and the next vector side
        a = pi - inner_angle
        # Angle between vectors (vertex-1, center) and (vertex-2, center)
        b = inner_angle / 2
        # Calculate the position of the first vertex
        x0 = self.center.x - radius * cos(b)
        y0 = self.center.y - radius * sin(b)
        vertices = []
        vertices.append(Vector(x0, y0))

        for i in range(1, vertex_count):
            next_vertice = vertices[i-1] + Vector(cos(a * (i-1)), sin(a * (i-1))) * side
            vertices.append(next_vertice)

        self.inner_angle = inner_angle
        self.vertex_count = vertex_count
        self.vertices = vertices

    def rotate(self, angle):
        """Rotates the polygon counterclockwise. The center of rotation is polygon center."""
        for i in range(self.vertex_count):
            center_to_vertex = self.vertices[i] - self.center
            center_to_vertex.rotate(angle)
            self.vertices[i] = self.center + center_to_vertex

    def move(self, vector):
        """Add a vector to all vertices."""
        for i in range(self.vertex_count):
            self.vertices[i] += vector
            self.center += vector


def crop_image(image, polygon):
    """Crop image with polygon mask."""
    # convert to numpy (for convenience)
    im_array = numpy.asarray(image)

    # create mask
    mask_im = Image.new('L', (im_array.shape[1], im_array.shape[0]), 0)
    ImageDraw.Draw(mask_im).polygon(polygon, outline=1, fill=1)
    mask = numpy.array(mask_im)

    # assemble new image (uint8: 0-255)
    new_im_array = numpy.empty(im_array.shape, dtype='uint8')

    # colors (three first columns, RGB)
    new_im_array[:, :, :3] = im_array[:, :, :3]

    # transparency (4th column)
    new_im_array[:, :, 3] = mask * 255

    # back to Image from numpy
    new_im = Image.fromarray(new_im_array, "RGBA")
    new_im = new_im.crop(new_im.convert("RGBa").getbbox())
    return new_im


def polygonize(uploaded_image, vertex_count, bbox_side_px):
    """Polygonize an image."""

    # Open the uploaded image and add alpha channel to it
    im = Image.open(uploaded_image).convert("RGBA")
    orig_width, orig_height = im.size
    orig_im_center = (orig_width / 2, orig_height / 2)
    poly_side = min(orig_width, orig_height) * sin(pi / vertex_count) * 0.95  # Polygon will be a little smaller than the bounding box
    p = Polygon(vertex_count=vertex_count, center=orig_im_center, side=poly_side)
    p.rotate(pi / 2)
    cropped_image = crop_image(image=im, polygon=[(point.x, point.y) for point in p.vertices])

    # Resize to bounding box side with anti-aliasing, save
    cropped_image.thumbnail((bbox_side_px, bbox_side_px), Image.ANTIALIAS)
    cropped_image_io = BytesIO()
    cropped_image.save(cropped_image_io, format='PNG')
    return cropped_image_io
