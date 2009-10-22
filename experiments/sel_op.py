from imgevolve import main, default, cleanup
import os

if __name__ == "__main__":
  gens = 5000
  for file in ['ml.bmp', 'lena.jpg', 'starry.jpg']:
    for op in ['roulette', 'tournament', 'rank']:
      basename = os.path.splitext(file)[0]
      dirname = 'render_test/%s_%s_%d'%(basename,op,gens)
      cleanup(dirname)
      options=default._replace( gens=gens
                              , output_freq=100
                              , output_dir=dirname
                              , sel_op=op
                              )
      main(options, file, dirname+'.svg')

