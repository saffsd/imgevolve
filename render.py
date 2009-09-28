#!/usr/bin/env python

import pdb
import os
import shutil
from pyevolve.GSimpleGA import GSimpleGA
from pyevolve import Selectors

import genetic_operators
from common import Candidate, TargetImage


def cleanup(path):
  if os.path.exists(path):
    shutil.rmtree(path)
  os.mkdir(path)

class ShowIntermediate:
  def __init__(self, target):
    self.target = target
    self.count = 0

  def __call__(self, ga):
    if self.count % 10 == 0:
      best = ga.bestIndividual()
      best.savefig(os.path.join(path,'best%04d.png' % self.count))
      #if self.count % 50 == 0:
      #  best.savediff(self.target, os.path.join(path, 'diff%04d.png' % self.count))
    self.count += 1
    return False
    
def main(path, image):
  target = TargetImage(image)
  count = 0

  callback = ShowIntermediate(target)

  #eval_func = target.rms_difference
  #eval_func = target.abs_difference
  eval_func = target.percept_difference
  #eval_func = target.square_difference

  # Initialize genome
  w, h = target.target.size
  genome = Candidate(w, h, target)
  genome.evaluator.set(eval_func)
  genome.initializator.set(genetic_operators.CandidateInitializator)
  #genome.mutator.add(genetic_operators.AddPolygon)
  #genome.mutator.add(genetic_operators.SamplePolygon)
  #genome.mutator.add(genetic_operators.RemovePolygon)
  #genome.mutator.add(genetic_operators.Reshuffle)
  genome.mutator.add(genetic_operators.Transpose)
  genome.mutator.add(genetic_operators.AdjustPolygon)
  #genome.mutator.add(genetic_operators.AdjustBackground)
  genome.mutator.add(genetic_operators.ChangePolygonOrder)
  genome.mutator.add(genetic_operators.ChangePolygonColor)
  genome.crossover.set(genetic_operators.SwapOne)
  #genome.crossover.add(genetic_operators.SinglePointCrossover)
  #genome.crossover.add(genetic_operators.AverageBackground)


  ga = GSimpleGA(genome)
  #ga.selector.set(Selectors.GTournamentSelector)
  #ga.selector.set(Selectors.GRouletteWheel)
  ga.selector.set(Selectors.GRankSelector)
  ga.setPopulationSize(50)
  ga.setGenerations(100000000)
  ga.setMutationRate(0.005)
  ga.setCrossoverRate(0.8)
  ga.stepCallback.set(callback)
  ga.setMinimax(0) 
  ga.initialize()
  pop = ga.getPopulation()
  ga.evolve(freq_stats = 10)

import sys
if __name__ == "__main__":
  path = sys.argv[1]
  image = sys.argv[2]
  cleanup(path)
  main(path, image)
