#!/usr/bin/env python

import pdb
import os
import shutil
import time
from optparse import OptionParser, OptionGroup
from collections import defaultdict

from pyevolve.GSimpleGA import GSimpleGA
from pyevolve import Selectors

import genetic_operators
from common import Candidate, TargetImage

def mean(seq):
  return sum(seq) / float(len(seq))

class ImgEvolveGA(GSimpleGA):
  def printStats(self):
    GSimpleGA.printStats(self)
    self.printSimulationRate()
    self.printShapeSummary()

  def printSimulationRate(self):
    if not hasattr(self, 'rateinfo'):
      self.rateinfo = (0, self.time_init)
    
    now = time.time()
    elapsed = now - self.rateinfo[1] 
    rate = (self.currentGeneration - self.rateinfo[0]) / elapsed
    print "\tEvolution rate: %.2f generations/sec" % rate
    self.rateinfo = (self.currentGeneration, now)
    
  def printShapeSummary(self):
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

import gtk

class LiveWindow:
    func_name= "Moo"
    func_doc = 'Moo'
    def __init__(self):
      window = gtk.Window()
      area = gtk.DrawingArea()
      area.show()
      window.add(area)
      window.present()
      self.area = area

    def __call__(self, ga):
      best = ga.bestIndividual()
      # Create the cairo context
      self.area.window.clear()
      cr = self.area.window.cairo_create()
      for s in best.shapes:
        s.render(cr)

 
    

def main(options, image, outfile):
  # Initialize the target
  target = TargetImage(image)

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
  #genome.mutator.add(genetic_operators.ChangePolygonOrder)
  genome.mutator.add(genetic_operators.ChangeShapeColor)
  #genome.crossover.set(genetic_operators.SwapOne)
  #genome.crossover.set(genetic_operators.FrontRear)
  genome.crossover.set(genetic_operators.Recombine)
  #genome.crossover.add(genetic_operators.SinglePointCrossover)

  # Initialize GA engine
  ga = ImgEvolveGA(genome)
  ga.setMinimax(0) # Set minimzation problem
  ga.setElitism(False)
  #ga.selector.set(Selectors.GTournamentSelector)
  #ga.selector.set(Selectors.GRouletteWheel)
  ga.selector.set(Selectors.GRankSelector)
  ga.setPopulationSize(options.pop_size)
  ga.setGenerations(options.gens)
  ga.setMutationRate(options.mut_rate)
  ga.setCrossoverRate(options.cross_rate)

  # Set up the display callback if required
  if options.output_dir is not None:
    callback = ShowIntermediate(options.output_dir, options.output_freq)
    ga.stepCallback.add(callback)

  if options.live_view:
    ga.stepCallback.add(LiveWindow())
  
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
  parser.add_option('--eval', type='string', dest='eval_func', default='rms', help='Evaluation function: [(rms),abs,percept,square]')

  group = OptionGroup(parser, 'Output Options')
  group.add_option('-o', type='string', dest='output_file', help='File to write final evolved image to')
  group.add_option('-d', type='string', dest='output_dir', help='Directory to write intermediate images')
  group.add_option('-n', type='int', dest='output_freq', default=10, help='Frequency between intermediate images (generations)')
  group.add_option('-l', action='store_true', dest='live_view', help='Show live view of running evolution')
  parser.add_option_group(group)

  group = OptionGroup(parser, 'Shape Parameters')
  group.add_option('--v_min', type='int', dest='vert_min', default=3, help='Minimum number of vertices')
  group.add_option('--v_max', type='int', dest='vert_max', default=10, help='Maximum number of vertices')
  group.add_option('--initial', type='int', dest='init_poly', default=50, help='Initial Shape Count')
  parser.add_option_group(group)

  group = OptionGroup(parser, "GA Parameters")
  group.add_option('--mut_rate', type='float', dest='mut_rate', default=0.01, help='Mutation Rate')
  group.add_option('--cross_rate', type='float', dest='cross_rate', default=0.8, help='Crossover Rate')
  group.add_option('--gens', type='int', dest='gens', default=10000, help='Generations to run for')
  group.add_option('--pop', type='int', default=25, dest='pop_size', help='Population size')
  parser.add_option_group(group)

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
