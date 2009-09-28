from PIL import Image, ImageChops
import numpy
import cairo
import random
from copy import deepcopy
from pyevolve.GenomeBase import GenomeBase
from pyevolve import Util

class TargetImage:
  """
  Encapsulates information about the evolution target
  """
  def __init__(self, path):
    self.path = path
    self.target = Image.open(self.path).convert('RGBA')
    self.target_im_array = numpy.asarray(self.target)


  def rms_difference(self, candidate):
    """
    Compute the root-mean-square difference between the target
    image and the candidate
    """
    candidate_arr = candidate.asarray()
    diff = candidate_arr - self.target_im_array
    return numpy.sqrt(numpy.mean(diff*diff))

  def abs_difference(self, candidate):
    candidate_arr = candidate.asarray()
    diff = candidate_arr - self.target_im_array
    return numpy.sum(numpy.abs(diff)) 

  def percept_difference(self, candidate):
    """
    Based on http://www.compuphase.com/cmetric.htm
    """
    #t_arr = numpy.vstack(self.target_im_array)
    c_arr = candidate.asarray()
    t_arr = self.target_im_array
    diff = (c_arr - t_arr).astype('uint32')
    r = diff[:,:,0]
    g = diff[:,:,1]
    b = diff[:,:,2]
    rmean = (c_arr[:,:,0] + t_arr[:,:,0]).astype('uint32') / 2
    out = numpy.sqrt((((512+rmean)*r*r)>>8) + 4*g*g + (((767-rmean)*b*b)>>8));
    #return numpy.sum(out)
    #Util.set_normal_term()
    #import pdb;pdb.set_trace()
    return numpy.sqrt(numpy.mean(out*out))

def color_distance(rgba1, rgba2):
  r,g,b,a = rgba1 - rgba2
  rmean = (rgba1[0] + rgba2[0]) / 2
  return numpy.sqrt((((512+rmean)*r*r)>>8) + 4*g*g + (((767-rmean)*b*b)>>8));

class Triangle:
  def __init__(self, vertices, color):
    if len(vertices) != 3: raise ValueError
    self.vertices = vertices
    self.color = color
  
  def __str__(self):
    return "<Triangle vertices: %s color: %s>" % (self.vertices, self.color)

  @property
  def midpoint(self):
    midpoint = tuple(sum(dim) / len(dim) for dim in zip(*self.vertices))
    return midpoint

class MyContext(cairo.Context):
  def triangle(self, triangle):
    self.set_source_rgba(*triangle.color)
    self.move_to(*triangle.vertices[0])
    self.line_to(*triangle.vertices[1])
    self.line_to(*triangle.vertices[2])
    self.fill()

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

  def savefig(self, filename):
    surface = self.cairo_surface()
    surface.write_to_png(filename)

  def savediff(self, target, filename):
    surface = self.cairo_surface()
    surf_im = Image.frombuffer("RGBA",( surface.get_width(),surface.get_height() ),surface.get_data(),"raw","RGBA",0,1)
    trgt_im = target.target
    diff = ImageChops.add(trgt_im, surf_im)
    diff.save(filename)

  def cairo_surface(self):
    w, h = self.width, self.height
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = MyContext(surface)
    ctx.set_source_rgb(*self.bg)
    ctx.paint()
    for t in self.triangles:
      ctx.triangle(t)
    return surface

  def asarray(self):
    surface = self.cairo_surface()
    buf = surface.get_data()
    candidate_arr = numpy.frombuffer(buf, numpy.uint8)
    candidate_arr.shape = (self.width, self.height, 4)
    return candidate_arr
