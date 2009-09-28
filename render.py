#!/usr/bin/env python

import pdb
import os
import shutil
from pyevolve.GSimpleGA import GSimpleGA
from pyevolve import Selectors

import genetic_operators
from common import Candidate, TargetImage

count = 0
def callback(ga):
  global count
  global target
  if count % 10 == 0:
    best = ga.bestIndividual()
    best.savefig('out/best%04d.png' % count)
    #pop = ga.getPopulation()
    #for i, ind in enumerate(pop):
    #  ind.write('out/pop_%d_%d.png' % (count,i))
    if count % 50 == 0:
      best.savediff(target, 'out/diff%04d.png' % count)

  count += 1
  return False

def cleanup(path):
  if os.path.exists(path):
    shutil.rmtree(path)
  os.mkdir(path)

target = TargetImage('lena.jpg')
#target = TargetImage('target.png')

def main():
  global target

  #eval_func = target.rms_difference
  #eval_func = target.abs_difference
  eval_func = target.percept_difference

  # Initialize genome
  w, h = target.target.size
  genome = Candidate(w, h)
  genome.evaluator.set(eval_func)
  genome.initializator.set(genetic_operators.CandidateInitializator)
  genome.mutator.add(genetic_operators.AddTriangle)
  genome.mutator.add(genetic_operators.RemoveTriangle)
  #genome.mutator.add(genetic_operators.Reshuffle)
  genome.mutator.add(genetic_operators.AdjustTriangle)
  genome.mutator.add(genetic_operators.AdjustBackground)
  genome.crossover.set(genetic_operators.SwapOne)
  #genome.crossover.add(genetic_operators.SinglePointCrossover)
  genome.crossover.add(genetic_operators.AverageBackground)


  ga = GSimpleGA(genome)
  #ga.selector.set(Selectors.GTournamentSelector)
  #ga.selector.set(Selectors.GRouletteWheel)
  ga.selector.set(Selectors.GRankSelector)
  ga.setPopulationSize(50)
  ga.setGenerations(100)
  ga.setMutationRate(0.05)
  ga.setCrossoverRate(0.8)
  ga.stepCallback.set(callback)
  ga.setMinimax(0) 
  ga.initialize()
  pop = ga.getPopulation()
  ga.evolve(freq_stats = 10)

import cProfile
if __name__ == "__main__":
  cleanup('out')
  #cProfile.run(main(), 'profile')
  main()
