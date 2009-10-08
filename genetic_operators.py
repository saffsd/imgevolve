import pyevolve.Util as Util
from rand import randrgb, randpoint
from random import randint, uniform, choice, shuffle, sample
import random
from copy import deepcopy
from common import shape_generators

def randshape(genome):
  return random.choice(shape_generators)(genome)
####
# Initializators
####
def RandomShapes(genome):
  """
  Initialize the individual with a set of completely random shapes
  """
  initialPoly = genome.getParam('poly_count')
  genome.shapes = []
  for i in range(initialPoly):
    t = randshape(genome)
    genome.shapes.append(t)

    
####
# Mutators
###
def AddShape(genome, **args):
  """ Add a random shape"""
  if Util.randomFlipCoin(args['pmut']):
    t = randshape(genome)
    genome.shapes.append(t)
    return 1
  else:
    return 0

def RemoveShape(genome, **args):
  """ Remove a random shape"""
  if len(genome.shapes) == 0: return 0
  if Util.randomFlipCoin(args['pmut']):
    index = choice(xrange(len(genome.shapes)))
    del genome.shapes[index]
    return 1
  else:
    return 0

def MutateShape(genome, **args):
  """ Move the vertexes of a random polygon"""
  if len(genome.shapes) == 0: return 0
  mut_count = 0
  for i in range(len(genome.shapes)):
    if Util.randomFlipCoin(args['pmut']):
      genome.shapes[i] = genome.shapes[i].mutate(genome)
      mut_count += 1
  return mut_count


def ChangeShapeColor(genome, **args):
  """ Modify shape color at random """
  if len(genome.shapes) == 0: return 0
  mut_count = 0
  for i in range(len(genome.shapes)):
    if Util.randomFlipCoin(args['pmut']):
      t = genome.shapes[i].copy()
      t.color = mutatecolor(t.color)
      genome.shapes[i] = t
  return mut_count

def Reshuffle(genome, **args):
  """Reshuffle the order of the shapes"""
  if Util.randomFlipCoin(args['pmut']):
    shuffle(genome.shapes)
    return 1
  else:
    return 0

def Transpose(genome, **args):
  """Transpose two shapes"""
  if Util.randomFlipCoin(args['pmut']) and len(genome.shapes) >= 2:
    i,j = sample(xrange(len(genome.shapes)),2)
    genome.shapes[i], genome.shapes[j] = genome.shapes[j], genome.shapes[i]
    return 1
  else:
    return 0

def mutatecolor(color):
  r = []
  for c in color:
    new_c = c + random.gauss(0,0.1)
    if new_c > 1.0: new_c = 1.0
    if new_c < 0.0: new_c = 0.0
    r.append(new_c)
  return tuple(r)

####
# Crossover
####
def color_mean(color1, color2):
  return tuple( (c1 + c2) / 2 for c1,c2 in zip(color1, color2))

#http://gnosis.cx/publish/programming/charming_python_b13.html
def weave(*iterables):
    "Intersperse several iterables, until all are exhausted"
    iterables = map(iter, iterables)
    while iterables:
        for i, it in enumerate(iterables):
            try:
                yield it.next()
            except StopIteration:
                del iterables[i]


def SwapOne(genome, **args):
  """ Exchange some genetic material """
  gMom = args['mom']
  gDad = args['dad']

  sister = gMom.clone()
  brother = gDad.clone()
  sister.resetStats()
  brother.resetStats()
  
  if len(sister.shapes) == 0 or len(brother.shapes) == 0:
    return (sister,brother)
  
  sis_i = choice(xrange(len(sister.shapes)))
  bro_i = choice(xrange(len(brother.shapes)))

  temp = sister.shapes[sis_i]
  sister.shapes[sis_i] = brother.shapes[bro_i]
  brother.shapes[bro_i] = temp
  return (sister, brother)

def Recombine(genome, **args):
  """Randomly redistribute the genetic material of the parents into
  the children"""
  gMom = args['mom']
  gDad = args['dad']

  if len(gMom.shapes) == 0 or len(gDad.shapes) == 0: return (gMom,gDad)

  children = (gMom.clone(), gDad.clone())
  for c in children:
    c.resetStats()
    c.shapes = []

  long, short = gMom.shapes, gDad.shapes
  if len(long) < len(short):
    long, short = short, long

  i = 0
  while i < len(short):
    c = randint(0,1)
    children[(0,1)[c]].shapes.append(short[i])
    children[(1,0)[c]].shapes.append(long[i])
    i += 1
  while i < len(long):
    children[0].shapes.append(long[i])
    i += 1

  return children

