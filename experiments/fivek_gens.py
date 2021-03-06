"""
by Marco Lui
This experiment renders each target image specified using each of the 4 
fitness functions, for 5000 generations. It assumes that the target images
are in the same folder as the program.
"""
from imgevolve import main, default, cleanup
import os

if __name__ == "__main__":
  gens = 5000
  for file in ['ml.bmp', 'lena.jpg', 'starry.jpg']:
    for alg in ['rms', 'percept', 'square', 'abs']:
      basename = os.path.splitext(file)[0]
      dirname = 'render_test/%s_%s_%d'%(basename,alg,gens)
      cleanup(dirname)
      options=default._replace( gens=gens
                              , output_freq=100
                              , output_dir=dirname
                              , eval_func = alg
                              )
      main(options, file, dirname+'.svg')


