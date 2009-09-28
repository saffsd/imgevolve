from random import uniform, randint
from common import Triangle

def randpoint(width, height):
  return [randint(0, width), randint(0,height)]

def randrgb():
  r = uniform(0.0,1.0)
  g = uniform(0.0,1.0)
  b = uniform(0.0,1.0)
  return (r,g,b)

def randrgba():
  r = uniform(0.0,1.0)
  g = uniform(0.0,1.0)
  b = uniform(0.0,1.0)
  a = uniform(0.0,1.0)
  return (r,g,b,a)

def randtriangle(width, height):
  vertices = [ randpoint(width, height) for i in range(3) ]
  color = randrgba()
  return Triangle(vertices, color)
