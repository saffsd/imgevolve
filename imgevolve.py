#!/usr/bin/env python
"""
imgevolve by Marco Lui
http://github.com/saffsd/imgevolve
An implementation of a genetic algorithm to evolve an approximation to an image
using a set of translucent shapes.
"""
import pdb
import os
import shutil
import time
from optparse import OptionParser, OptionGroup
from collections import defaultdict
from collections import namedtuple

from pyevolve.GSimpleGA import GSimpleGA
from pyevolve import Selectors

import genetic_operators
from common import Candidate, TargetImage

Options = namedtuple('Options','eval_func init_poly vert_min vert_max\
                                pop_size gens mut_rate cross_rate output_dir\
                                output_freq live_view sel_op elitism')

default = Options( eval_func = 'rms'
                 , init_poly= 50
                 , vert_min = 3
                 , vert_max = 10
                 , pop_size = 25
                 , gens = 10000
                 , mut_rate = 0.01
                 , cross_rate = 0.8
                 , sel_op = 'rank'
                 , output_dir = None
                 , output_freq = 10
                 , live_view = False
                 , elitism = False
                 )

def mean(seq):
  """
  Calulate the mean value in a sequence
  """
  return sum(seq) / float(len(seq))

class ImgEvolveGA(GSimpleGA):
  """
  Subclass of GSimpleGA which adds some instrumentation to monitor parameters specific
  to imgevolve.
  """
  def printStats(self):
    """
    Override printStats so we get an extended summary
    """
    GSimpleGA.printStats(self)
    self.printSimulationRate()
    self.printShapeSummary()

  def printSimulationRate(self):
    """
    Display the current evolution rate
    """
    if not hasattr(self, 'rateinfo'):
      self.rateinfo = (0, self.time_init)
    
    now = time.time()
    elapsed = now - self.rateinfo[1] 
    rate = (self.currentGeneration - self.rateinfo[0]) / elapsed
    print "\tEvolution rate: %.2f generations/sec" % rate
    self.rateinfo = (self.currentGeneration, now)
    
  def printShapeSummary(self):
    """
    Display a summary of shapes across all individuals
    """
    pop = self.getPopulation()
    shape_counts = []
    shape_type_count = defaultdict(list)
    for ind in pop:
      shape_counts.append(len(ind.shapes))
      types = defaultdict(int)
      for shape in ind.shapes:
        types[shape.desc] += 1
      for t in types:
        shape_type_count[t].append(types[t])

    print "\tShape count: %d/%d/%.1f" % (max(shape_counts), min(shape_counts), mean(shape_counts))
    for t in sorted(shape_type_count):
      c = shape_type_count[t]
      print "\t\t%s: %d/%d/%.1f" % (t, max(c), min(c), mean(c))
    print
    return False


def cleanup(path):
  if os.path.exists(path):
    shutil.rmtree(path)
  os.mkdir(path)

class ShowIntermediate:
  func_name= "ShowIntermediate"
  func_doc = 'Show Intermediate Results'
  def __init__(self, output_dir, output_freq):
    self.output_dir = output_dir 
    self.output_freq = output_freq
    self.count = 0

  def __call__(self, ga):
    if self.count % self.output_freq == 0:
      best = ga.bestIndividual()
      best.save(os.path.join(self.output_dir,'best%04d.png' % self.count))
    self.count += 1
    return False

class ShowIntermediateAll:
  func_name= "ShowIntermediateAll"
  func_doc = 'Show all individuals in an intermediate generation'
  def __init__(self, output_dir, output_freq):
    self.output_dir = output_dir 
    self.output_freq = output_freq
    self.count = 0

  def __call__(self, ga):
    if self.count % self.output_freq == 0:
      output_dir = os.path.join(self.output_dir, 'gen%d'%self.count)
      cleanup(output_dir)
      for i,ind in enumerate(ga.getPopulation()):
        ind.save(os.path.join(output_dir,'ind%d.png' % i))
    self.count += 1
    return False

import gtk

class LiveWindow:
    func_name= "Moo"
    func_doc = 'Moo'
    def __init__(self, width, height):
    #def __init__(self):
      self.window = gtk.Window()
      self.window.set_default_size(width, height)
      self.area = gtk.DrawingArea()
      #self.area.set_size_request(best.width, best.height)
      self.area.show()
      self.window.add(self.area)
      self.window.present()

    def __call__(self, ga):
      best = ga.bestIndividual()
      # Create the cairo context
      self.area.window.clear()
      cr = self.area.window.cairo_create()
      best.cairo_draw(cr)
 
    

def main(options, image, outfile):
  target = TargetImage(image)

  # Decide which evaluation function to use
  if options.eval_func == 'rms':
    eval_func = target.rms_difference
  elif options.eval_func == 'abs':
    eval_func = target.abs_difference
  elif options.eval_func == 'percept':
    eval_func = target.percept_difference
  elif options.eval_func == 'square':
    eval_func = target.square_difference
  else:
    raise ValueError, "Unknown evaluation function!"

  # Initialize genome
  genome = Candidate(target)
  genome.setParams( background=False
                  , poly_count=options.init_poly
                  , vert_min = options.vert_min
                  , vert_max = options.vert_max
                  )
  genome.evaluator.set(eval_func)
  genome.initializator.set(genetic_operators.RandomShapes)
  #genome.initializator.set(genetic_operators.SampleShapes)
  #genome.mutator.add(genetic_operators.SampleShape)
  genome.mutator.add(genetic_operators.AddShape)
  genome.mutator.add(genetic_operators.RemoveShape)
  #genome.mutator.add(genetic_operators.Reshuffle)
  genome.mutator.add(genetic_operators.Transpose)
  genome.mutator.add(genetic_operators.MutateShape)
  genome.mutator.add(genetic_operators.Crawl)
  genome.mutator.add(genetic_operators.ChangeShapeColor)
  genome.mutator.add(genetic_operators.AdjustBackground)
  genome.mutator.add(genetic_operators.ReplaceBackground)
  #genome.crossover.set(genetic_operators.SwapOne)
  #genome.crossover.set(genetic_operators.FrontRear)
  genome.crossover.set(genetic_operators.Recombine)
  #genome.crossover.add(genetic_operators.SinglePointCrossover)
  genome.crossover.add(genetic_operators.AverageBackground)

  # Initialize GA engine
  ga = ImgEvolveGA(genome)
  ga.setMinimax(0) # Set minimzation problem 

  # Configure elitism 
  ga.setElitism(options.elitism)
  
  # Decide which selection operator to use
  if options.sel_op == 'tournament':
    ga.selector.set(Selectors.GTournamentSelector)
  elif options.sel_op == 'roulette':
    ga.selector.set(Selectors.GRouletteWheel)
  elif options.sel_op == 'rank':
    ga.selector.set(Selectors.GRankSelector)
  else:
    raise ValueError, "Unknown selection operator!"

  ga.setPopulationSize(options.pop_size)
  ga.setGenerations(options.gens)
  ga.setMutationRate(options.mut_rate)
  ga.setCrossoverRate(options.cross_rate)

  # Set up the display callback if required
  if options.output_dir is not None:
    callback = ShowIntermediate(options.output_dir, options.output_freq)
    ga.stepCallback.add(callback)
    callback = ShowIntermediateAll(options.output_dir, options.output_freq * 100)
    ga.stepCallback.add(callback)

  if options.live_view:
    ga.stepCallback.add(LiveWindow(*target.target.size))
  
  print genome
  print ga

  # Evolve!
  ga.evolve(freq_stats = options.output_freq)

  # Output final image
  best = ga.bestIndividual()
  best.save(outfile)

  print "Best individual:"
  print best

import sys
if __name__ == "__main__":
  parser = OptionParser(usage = '%prog [options] input')

  parser.add_option('-p', action='store_true', dest='profile', help='Enable Profiling')
  parser.add_option('--eval', type='string', dest='eval_func', help='Evaluation function: [(rms),abs,percept,square]')

  group = OptionGroup(parser, 'Output Options')
  group.add_option('-o', type='string', dest='output_file', help='File to write final evolved image to')
  group.add_option('-d', type='string', dest='output_dir', help='Directory to write intermediate images')
  group.add_option('-n', type='int', dest='output_freq', help='Frequency between intermediate images (generations)')
  group.add_option('-l', action='store_true', dest='live_view', help='Show live view of running evolution')
  parser.add_option_group(group)

  group = OptionGroup(parser, 'Shape Parameters')
  group.add_option('--v_min', type='int', dest='vert_min', help='Minimum number of vertices')
  group.add_option('--v_max', type='int', dest='vert_max', help='Maximum number of vertices')
  group.add_option('--initial', type='int', dest='init_poly', help='Initial Shape Count')
  parser.add_option_group(group)

  group = OptionGroup(parser, "GA Parameters")
  group.add_option('--mut_rate', type='float', dest='mut_rate', help='Mutation Rate')
  group.add_option('--cross_rate', type='float', dest='cross_rate', help='Crossover Rate')
  group.add_option('--sel', type='string', dest='sel_op', help='Selection Operator [(rank), tournament, roulette]')
  group.add_option('--gens', type='int', dest='gens', help='Generations to run for')
  group.add_option('--pop', type='int', dest='pop_size', help='Population size')
  group.add_option('--elite', action='store_true', dest='elitism', help='Enable elitism')
  parser.add_option_group(group)

  parser.set_defaults(**default._asdict())
  options, args = parser.parse_args()

  if len(args) != 1:
    parser.error('Incorrect number of arguments')

  image = args[0]

  # If outputting intermediates, set up an empty directory to do so
  if options.output_dir is not None:
    cleanup(options.output_dir)
    shutil.copy(image, options.output_dir)

  if options.output_file is None:
    base, ext = os.path.splitext(image)
    outfile = base + '_evolved.svg'
  else:
    outfile = options.output_file

  from pyevolve import Util
  Util.set_normal_term()
  if options.profile:
    import cProfile
    cProfile.run('main(options, image, outfile)', image+'.profile')
  else:
    main(options, image, outfile)
