"""
by Marco Lui
This experiment times the runtime of imgevolve on each target image
for 100 generations for each fitness function. It writes the timing
information to a csv file.
"""
from imgevolve import main, default
import timeit
import csv


if __name__ == "__main__":
  with open('timing.csv','w') as outfile:
    writer = csv.writer(outfile)
    for file in ['ml.bmp', 'lena.jpg', 'starry.jpg']:
      for alg in ['rms', 'square', 'abs', 'percept']:
        t = timeit.Timer( 'main(options, "%s", "timing.svg")' % file
                        , 'from imgevolve import main; from time_evolution import default; options = default._replace(eval_func="%s", gens=100)' % alg
                        )
        times = t.repeat(repeat=10, number=1)
        writer.writerow([file, alg] + times)


