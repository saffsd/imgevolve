import pyevolve.Util as Util
from rand import randtriangle, randrgb
from random import randint, uniform, choice, shuffle
import random
from copy import deepcopy

####
# Initializators
####
def CandidateInitializator(genome, **args):
  genome.bg = randrgb()
  genome.triangles = []
  for i in xrange(randint(1,100)): #TODO: Better way of deciding start number
  #for i in xrange(100): #TODO: Better way of deciding start number
    t = randtriangle(genome.width, genome.height)
    genome.triangles.append(t)
    
####
# Mutators
###
def AddTriangle(genome, **args):
  """ Add a random triangle """
  if Util.randomFlipCoin(args['pmut']):
    t = randtriangle(genome.width, genome.height)
    genome.triangles.append(t)
    return 1
  else:
    return 0
  
def RemoveTriangle(genome, **args):
  """ Remove a random triangle """
  if len(genome.triangles) == 0: return 0
  if Util.randomFlipCoin(args['pmut']):
    index = choice(xrange(len(genome.triangles)))
    del genome.triangles[index]
    return 1
  else:
    return 0

def AdjustTriangle(genome, **args):
  """ Modify a random triangle"""
  if len(genome.triangles) == 0: return 0
  mut_count = 0
  for i in range(len(genome.triangles)):
    if Util.randomFlipCoin(args['pmut']):
      t = deepcopy(genome.triangles[i])
      for v in xrange(len(t.vertices)):
        for dim in [0,1]:
          #t.vertices[v][dim] += randint(-2,2)
          t.vertices[v][dim] += random.gauss(0, 10) 
      genome.triangles[i] = t
  return mut_count

def ChangeTriangleColor(genome, **args):
  """ Modify triangle color at random """
  if len(genome.triangles) == 0: return 0
  mut_count = 0
  for i in range(len(genome.triangles)):
    if Util.randomFlipCoin(args['pmut']):
      t = deepcopy(genome.triangles[i])
      t.color = mutatecolor(t.color)
      genome.triangles[i] = t
  return mut_count

def Reshuffle(genome, **args):
  """Reshuffle the order of the triangles"""
  if Util.randomFlipCoin(args['pmut']):
    shuffle(genome.triangles)
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
  
  if len(sister.triangles) == 0 or len(brother.triangles) == 0:
    return (sister,brother)
  
  sis_i = choice(xrange(len(sister.triangles)))
  bro_i = choice(xrange(len(brother.triangles)))

  temp = sister.triangles[sis_i]
  sister.triangles[sis_i] = brother.triangles[bro_i]
  brother.triangles[bro_i] = temp
  return (sister, brother)

def SinglePointCrossover(genome, **args):
  """ Exchange some genetic material """
  gMom = args['mom']
  gDad = args['dad']

  sister = gMom.clone()
  brother = gDad.clone()
  sister.resetStats()
  brother.resetStats()
  
  sis_i = choice(xrange(len(sister.triangles)))
  bro_i = choice(xrange(len(brother.triangles)))

  sis_new = sister.triangles[:sis_i] + brother.triangles[bro_i:]
  bro_new = brother.triangles[:bro_i] + sister.triangles[sis_i:]
  sister.triangles = sis_new
  brother.triangles = bro_new
  return (sister, brother)

