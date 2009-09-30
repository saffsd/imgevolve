from random import uniform, randint
from common import Polygon 

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

def randpolygon(genome):
  v_min = genome.getParam('vert_min')
  v_max = genome.getParam('vert_max')
  width = genome.width
  height = genome.height
  vertices = [ randpoint(width, height) for i in range(randint(v_min,v_max)) ]
  color = randrgba()
  return Polygon(vertices, color)
