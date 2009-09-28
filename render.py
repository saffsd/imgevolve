#!/usr/bin/env python

import pdb
import cairo
import numpy
from copy import deepcopy
from pyevolve.GenomeBase import GenomeBase
from pyevolve.GSimpleGA import GSimpleGA
from PIL import Image
from random import randint, uniform, choice, shuffle
import random
import pyevolve.Util as Util
from pyevolve import Selectors


class rms_difference:
  """
  Compute rms difference between target image and a candidate
  """
  func_name = "RMS Difference"
  func_doc = ""
  def __init__(self, target_file):
    self.target = Image.open(target_file).convert('RGBA')
    self.target_im_array = numpy.asarray(self.target)

  def __call__(self, candidate):
    surface = candidate.get_surface()
    buf = surface.get_data()
    a = numpy.frombuffer(buf, numpy.uint8)
    a.shape = (candidate.width, candidate.height, 4)
    diff = a - self.target_im_array
    #Util.set_normal_term()
    #pdb.set_trace()
    return numpy.sqrt(numpy.mean(diff*diff))

class MyContext(cairo.Context):
  def triangle(self, triangle):
    self.set_source_rgba(*triangle.color)
    self.move_to(*triangle.vertices[0])
    self.line_to(*triangle.vertices[1])
    self.line_to(*triangle.vertices[2])
    self.fill()

def randpoint(width, height):
  return [randint(0, width), randint(0,height)]

class Triangle:
  def __init__(self, vertices, color):
    if len(vertices) != 3: raise ValueError
    self.vertices = vertices
    self.color = color
  
  def __getstate__(self):
    return self.__dict__

  def __setstate__(self, state):
    self.__dict__.update(state)

  def __str__(self):
    return "Vertices: %s Color: %s" % (self.vertices, self.color)

  @staticmethod
  def random(width, height, target):
    vertices = [ randpoint(width, height) for i in range(3) ]
    midpoint = tuple(sum(dim) / len(dim) for dim in zip(*vertices))
    r,g,b,a = target.getpixel(midpoint)
    r /= 255.0
    g /= 255.0
    b /= 255.0
    a = uniform(0.0,1.0)
    return Triangle(vertices, (r,g,b,a))
    
class Candidate(GenomeBase):
  def __init__(self, width, height, bg=(0,0,0)):
    GenomeBase.__init__(self)
    self.bg = bg 
    self.width = width
    self.height = height
    self.triangles = []

  def __repr__(self):
    r = GenomeBase.__repr__(self)
    r += "Triangles:\n"
    for t in self.triangles:
      r += '\t' + str(t) + '\n'
    return r

  def copy(self, g):
    """Copy method required by pyevolve"""
    GenomeBase.copy(self, g)
    g.bg = self.bg
    g.triangles = deepcopy(self.triangles)

  def clone(self):
    newcopy = Candidate(self.width, self.height, self.bg)
    self.copy(newcopy)
    return newcopy

  def write(self, filename):
    surface = self.get_surface()
    surface.write_to_png(filename)

  def get_surface(self):
    w, h = self.width, self.height
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = MyContext(surface)
    ctx.set_source_rgb(*self.bg)
    ctx.paint()
    for t in self.triangles:
      ctx.triangle(t)
    return surface
    
####
# Initializators
####
def CandidateInitializator(genome, **args):
  global eval_func
  genome.triangles = []
  for i in xrange(50): #TODO: Better way of deciding start number
    t = Triangle.random(genome.width, genome.height, eval_func.target)
    genome.triangles.append(t)
    
####
# Mutators
###
def AddTriangle(genome, **args):
  """ Add a random triangle """
  global eval_func
  if Util.randomFlipCoin(args['pmut']):
    t = Triangle.random(genome.width, genome.height, eval_func.target)
    genome.triangles.append(t)
    #print "Adding a triangle", t
    return 1
  else:
    return 0
  
def RemoveTriangle(genome, **args):
  """ Remove a random triangle """
  if len(genome.triangles) == 0: return 0
  if Util.randomFlipCoin(args['pmut']):
    index = choice(xrange(len(genome.triangles)))
    del genome.triangles[index]
    #print "Removing a triangle at", index, "p=",args['pmut']
    return 1
  else:
    return 0

def AdjustTriangle(genome, **args):
  """ Remove a random triangle """
  if len(genome.triangles) == 0: return 0
  if Util.randomFlipCoin(args['pmut']):
    index = choice(xrange(len(genome.triangles)))
    t = genome.triangles[index]
    t.vertices[randint(0,2)][randint(0,1)] += int(random.gauss(0,genome.width))
    return 1
  else:
    return 0

def reshuffle(genome, **args):
  """Reshuffle the order of the triangles"""
  if Util.randomFlipCoin(args['pmut']):
    shuffle(genome.triangles)
    return 1
  else:
    return 0

####
# Crossover
####
def SwapOne(genome, **args):
  """ Exchange some genetic material """
  gMom = args['mom']
  gDad = args['dad']

  sister = gMom.clone()
  brother = gDad.clone()
  sister.resetStats()
  brother.resetStats()
  
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

count = 0
def callback(ga):
  global count
  if count % 10 == 0:
    best = ga.bestIndividual()
    best.write('out/best%04d.png' % count)
    #pop = ga.getPopulation()
    #for i, ind in enumerate(pop):
    #  ind.write('out/pop_%d_%d.png' % (count,i))
  count += 1
  return False

#target = 'tb.png'
target = 'lena.jpg'
#target = 'target.png'
eval_func = rms_difference(target)
#print eval_func(x)

# Initialize genome
w, h = eval_func.target.size
genome = Candidate(w, h)
genome.evaluator.set(eval_func)
genome.initializator.set(CandidateInitializator)
genome.mutator.add(AddTriangle)
genome.mutator.add(RemoveTriangle)
genome.mutator.add(reshuffle)
genome.mutator.add(AdjustTriangle)
#genome.crossover.set(SwapOne)
genome.crossover.add(SinglePointCrossover)


ga = GSimpleGA(genome)
ga.selector.set(Selectors.GTournamentSelector)
ga.setPopulationSize(50)
ga.setGenerations(100000000)
ga.setMutationRate(0.05)
ga.setCrossoverRate(0.8)
ga.stepCallback.set(callback)
ga.setMinimax(0) 
ga.initialize()
pop = ga.getPopulation()
ga.evolve(freq_stats = 10)

