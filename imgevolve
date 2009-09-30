#!/usr/bin/env python

import pdb
import os
import shutil
from optparse import OptionParser, OptionGroup

from pyevolve.GSimpleGA import GSimpleGA
from pyevolve import Selectors

import genetic_operators
from common import Candidate, TargetImage


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
      best.savefig(os.path.join(self.output_dir,'best%04d.png' % self.count))
    self.count += 1
    return False
    
def main(options, image, outfile):
  # Initialize the target
  target = TargetImage(image)

  eval_func = target.rms_difference
  #eval_func = target.abs_difference
  #eval_func = target.percept_difference
  #eval_func = target.square_difference

  # Initialize genome
  w, h = target.target.size
  genome = Candidate(w, h, target)
  genome.setParams( background=False
                  , poly_count=options.init_poly
                  , vert_min = options.vert_min
                  , vert_max = options.vert_max
                  )
  genome.evaluator.set(eval_func)
  genome.initializator.set(genetic_operators.RandomPolygons)
  #genome.mutator.add(genetic_operators.SamplePolygon)
  genome.mutator.add(genetic_operators.AddPolygon)
  genome.mutator.add(genetic_operators.RemovePolygon)
  genome.mutator.add(genetic_operators.Reshuffle)
  genome.mutator.add(genetic_operators.Transpose)
  genome.mutator.add(genetic_operators.AdjustPolygon)
  #genome.mutator.add(genetic_operators.AdjustBackground)
  genome.mutator.add(genetic_operators.ChangePolygonOrder)
  genome.mutator.add(genetic_operators.ChangePolygonColor)
  genome.crossover.set(genetic_operators.SwapOne)
  #genome.crossover.add(genetic_operators.SinglePointCrossover)
  #genome.crossover.add(genetic_operators.AverageBackground)

  # Initialize GA engine
  ga = GSimpleGA(genome)
  ga.setMinimax(0) # Set minimzation problem
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
    ga.stepCallback.set(callback)

  print genome
  print ga

  # Evolve!
  ga.evolve(freq_stats = options.output_freq)

  # Output final image
  best = ga.bestIndividual()
  best.savefig(outfile)
  print "Best individual:"
  print best

import sys
if __name__ == "__main__":
  parser = OptionParser(usage = '%prog [options] input')

  group = OptionGroup(parser, 'Output Options')
  group.add_option('-o', type='string', dest='output_file', help='output file')
  group.add_option('-d', type='string', dest='output_dir', help='output directory')
  group.add_option('-n', type='int', dest='output_freq', default=10, help='output frequency (generations)')

  group = OptionGroup(parser, 'Polygon Parameters')
  group.add_option('--v_min', type='int', dest='vert_min', default=3, help='Minimum number of vertices')
  group.add_option('--v_max', type='int', dest='vert_max', default=6, help='Maximum number of vertices')
  group.add_option('--initial', type='int', dest='init_poly', default=50, help='Initial Polygon Count')

  group = OptionGroup(parser, "GA Parameters")
  group.add_option('--mut_rate', type='float', dest='mut_rate', default=0.01, help='Mutation Rate')
  group.add_option('--cross_rate', type='float', dest='cross_rate', default=0.8, help='Crossover Rate')
  group.add_option('--gens', type='int', dest='gens', default=1000, help='Generations to run for')
  group.add_option('--pop', type='int', default=25, dest='pop_size', help='Population size')

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
    outfile = base + '_evolved' + ext
  else:
    outfile = options.output_file

  main(options, image, outfile)
