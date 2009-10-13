from random import uniform, randint, choice

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
  #a=1.0
  #a=0.5
  return (r,g,b,a)

