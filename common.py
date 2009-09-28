from PIL import Image, ImageChops
import numpy
import cairo
import random
import pdb
from copy import deepcopy
from pyevolve.GenomeBase import GenomeBase
from pyevolve import Util

numpy.seterr(all='raise')

class TargetImage:
  """
  Encapsulates information about the evolution target
  """
  def __init__(self, path):
    self.path = path
    self.target = Image.open(self.path).convert('RGBA')
    data = numpy.asarray(self.target).astype('int32')
    b = data[:,:,0]
    g = data[:,:,1]
    r = data[:,:,2]
    a = data[:,:,3]
    self.target_im_array = numpy.dstack((r,g,b,a))
    #Util.set_normal_term()
    #pdb.set_trace()


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

  def square_difference(self, candidate):
    candidate_arr = candidate.asarray()
    diff = (candidate_arr - self.target_im_array)[:,:,:3]
    #Util.set_normal_term()
    #import pdb;pdb.set_trace()
    return numpy.sum(diff * diff)
    

  def percept_difference(self, candidate):
    """
    Based on http://www.compuphase.com/cmetric.htm
    """
    #t_arr = numpy.vstack(self.target_im_array)
    c_arr = candidate.asarray()
    t_arr = self.target_im_array
    diff = (c_arr - t_arr)
    r = diff[:,:,0]
    g = diff[:,:,1]
    b = diff[:,:,2]
    rmean = (c_arr[:,:,0] + t_arr[:,:,0]) / 2
    out = numpy.sqrt((((512+rmean)*r*r)>>8) + 4*g*g + (((767-rmean)*b*b)>>8));
    #return numpy.sum(out)
    #Util.set_normal_term()
    #import pdb;pdb.set_trace()
    return numpy.sqrt(numpy.mean(out*out))

class Polygon:
  def __init__(self, vertices, color):
    self.vertices = vertices
    self.color = color
  
  def __str__(self):
    return "<Polygon %d vertices, color: %s>" % (len(self.vertices), self.color)

  @property
  def midpoint(self):
    midpoint = tuple(sum(dim) / len(dim) for dim in zip(*self.vertices))
    return midpoint

class MyContext(cairo.Context):
  def polygon(self, p):
    self.set_source_rgba(*p.color)
    self.move_to(*p.vertices[0])
    for v in p.vertices[1:]:
      self.line_to(*v)
    self.fill()

class Candidate(GenomeBase):
  def __init__(self, width, height, target, bg=(0,0,0)):
    GenomeBase.__init__(self)
    self.bg = bg 
    self.width = width
    self.height = height
    self.target = target
    self.polygons = []

  def __repr__(self):
    r = GenomeBase.__repr__(self)
    r += "Polygons:\n"
    for t in self.polygons:
      r += '\t' + str(t) + '\n'
    return r

  def copy(self, g):
    """Copy method required by pyevolve"""
    GenomeBase.copy(self, g)
    g.bg = self.bg
    g.polygons = deepcopy(self.polygons)
    g.target = self.target

  def clone(self):
    newcopy = Candidate(self.width, self.height, self.bg)
    self.copy(newcopy)
    return newcopy

  def savefig(self, filename):
    surface = self.cairo_surface()
    surface.write_to_png(filename)

  def savediff(self, target, filename):
    surf = self.asarray()
    trgt = target.target_im_array
    diff = numpy.abs(surf - trgt)
    diff[:,:,3] = 255
    im = Image.frombuffer("RGBA",(self.width,self.height),diff,"raw","RGBA",0,1)
    im.save(filename)

  def cairo_surface(self):
    w, h = self.width, self.height
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = MyContext(surface)
    ctx.set_source_rgb(*self.bg)
    ctx.paint()
    for p in self.polygons:
      ctx.polygon(p)
    return surface

  def asarray(self):
    surface = self.cairo_surface()
    buf = surface.get_data()
    candidate_arr = numpy.frombuffer(buf, numpy.uint8).astype('int32')
    candidate_arr.shape = (self.width, self.height, 4)
    return candidate_arr
