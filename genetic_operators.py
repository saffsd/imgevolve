import pyevolve.Util as Util
from rand import randpolygon, randrgb, randpoint
from random import randint, uniform, choice, shuffle, sample
import random
from copy import deepcopy

####
# Initializators
####
def CandidateInitializator(genome, **args):
  genome.bg = randrgb()
  genome.polygons = []
  #for i in xrange(0): #TODO: Better way of deciding start number
  for i in xrange(100): #TODO: Better way of deciding start number
    t = randpolygon(genome.width, genome.height)
    genome.polygons.append(t)
    
####
# Mutators
###
def AddPolygon(genome, **args):
  """ Add a random polygon """
  if Util.randomFlipCoin(args['pmut']):
    t = randpolygon(genome.width, genome.height)
    genome.polygons.append(t)
    return 1
  else:
    return 0
  
def RemovePolygon(genome, **args):
  """ Remove a random polygon """
  if len(genome.polygons) == 0: return 0
  if Util.randomFlipCoin(args['pmut']):
    index = choice(xrange(len(genome.polygons)))
    del genome.polygons[index]
    return 1
  else:
    return 0

def AdjustPolygon(genome, **args):
  """ Modify a random polygon"""
  if len(genome.polygons) == 0: return 0
  mut_count = 0
  for i in range(len(genome.polygons)):
    if Util.randomFlipCoin(args['pmut']):
      t = deepcopy(genome.polygons[i])
      for v in xrange(len(t.vertices)):
        for dim in [0,1]:
          #t.vertices[v][dim] += randint(-2,2)
          t.vertices[v][dim] += random.gauss(0, 10) 
      genome.polygons[i] = t
  return mut_count

def ChangePolygonOrder(genome, **args):
  """ Randomly add or remove a vertex to the polygon """ 
  if len(genome.polygons) == 0: return 0
  mut_count = 0
  for i in range(len(genome.polygons)):
    if Util.randomFlipCoin(args['pmut']):
      t = genome.polygons[i]
      pos = choice(xrange(len(t.vertices)))
      if randint(0,1):
        if len(t.vertices) < 6:
          t.vertices.insert(pos, randpoint(genome.width, genome.height))
          mut_count += 1
      else:
        if len(t.vertices) > 3:
          del t.vertices[pos]
          mut_count += 1
      genome.polygons[i] = t
  return mut_count
  

def ChangePolygonColor(genome, **args):
  """ Modify polygon color at random """
  if len(genome.polygons) == 0: return 0
  mut_count = 0
  for i in range(len(genome.polygons)):
    if Util.randomFlipCoin(args['pmut']):
      t = deepcopy(genome.polygons[i])
      t.color = mutatecolor(t.color)
      genome.polygons[i] = t
  return mut_count

def Reshuffle(genome, **args):
  """Reshuffle the order of the polygons"""
  if Util.randomFlipCoin(args['pmut']):
    shuffle(genome.polygons)
    return 1
  else:
    return 0

def Transpose(genome, **args):
  """Transpose two polygons"""
  if Util.randomFlipCoin(args['pmut']):
    i,j = sample(xrange(len(genome.polygons)),2)
    genome.polygons[i], genome.polygons[j] = genome.polygons[j], genome.polygons[i]
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

def AdjustBackground(genome, **args):
  """Adjust the background color"""
  if Util.randomFlipCoin(args['pmut']):
    bg = genome.bg
    genome.bg = mutatecolor(bg)
    return 1
  else:
    return 0
  pass

def ReplaceBackground(genome, **args):
  if Util.randomFlipCoin(args['pmut']):
    genome.bg = randrgb()
    return 1
  else:
    return 0 
  

####
# Crossover
####
def color_mean(color1, color2):
  return tuple( (c1 + c2) / 2 for c1,c2 in zip(color1, color2))

def AverageBackground(genome, **args):
  """Average the background"""
  gMom = args['mom']
  gDad = args['dad']

  sister = gMom.clone()
  brother = gDad.clone()
  sister.resetStats()
  brother.resetStats()
  
  cm = color_mean(gMom.bg, gDad.bg)
  sister.bg = cm
  brother.bg = cm

  return (sister, brother)
  

def SwapOne(genome, **args):
  """ Exchange some genetic material """
  gMom = args['mom']
  gDad = args['dad']

  sister = gMom.clone()
  brother = gDad.clone()
  sister.resetStats()
  brother.resetStats()
  
  if len(sister.polygons) == 0 or len(brother.polygons) == 0:
    return (sister,brother)
  
  sis_i = choice(xrange(len(sister.polygons)))
  bro_i = choice(xrange(len(brother.polygons)))

  temp = sister.polygons[sis_i]
  sister.polygons[sis_i] = brother.polygons[bro_i]
  brother.polygons[bro_i] = temp
  return (sister, brother)

def SinglePointCrossover(genome, **args):
  """ Exchange some genetic material """
  gMom = args['mom']
  gDad = args['dad']

  sister = gMom.clone()
  brother = gDad.clone()
  sister.resetStats()
  brother.resetStats()
  
  sis_i = choice(xrange(len(sister.polygons)))
  bro_i = choice(xrange(len(brother.polygons)))

  sis_new = sister.polygons[:sis_i] + brother.polygons[bro_i:]
  bro_new = brother.polygons[:bro_i] + sister.polygons[sis_i:]
  sister.polygons = sis_new
  brother.polygons = bro_new
  return (sister, brother)

