from PIL import Image, ImageChops
import numpy
import cairo
import pdb
import math
import os
from copy import deepcopy
from pyevolve.GenomeBase import GenomeBase
from pyevolve import Util
from rand import randpoint, randrgba
from random import uniform, randint, choice, gauss

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

class Ellipse:
  desc = 'Ellipse'
  def __init__(self, x, y, width, height, angle, color):
    """
    x      - center x
    y      - center y
    width  - width of ellipse  (in x direction when angle=0)
    height - height of ellipse (in y direction when angle=0)
    angle  - angle in radians to rotate, clockwise
    """
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.angle = angle
    self.color = color

  def __str__(self):
    return "<Ellipse center:(%d,%d), color: %s>" % (self.x, self.y, str(self.color))


  def copy(self):
    return deepcopy(self)

  @staticmethod
  def random(genome):
    x,y = randpoint(genome.width,genome.height)
    width = uniform(0.0,1.0) * genome.width 
    height = uniform(0.0,1.0) * genome.height 
    angle = randint(0,360)
    color = randrgba()
    return Ellipse(x,y,width,height,angle,color)

  def mut_angle(self, genome):
    self.angle += int(gauss(0,10))
    
  def mut_center(self, genome):
    self.x += gauss(0,10)
    self.y += gauss(0,10)

  def mut_size(self, genome):
    self.width += gauss(0,10)
    self.height += gauss(0,10)

  def mutate(self, genome):
    """ 
    Return a mutated copy of this polygon
    This must be a copy because polygons may be shared by instances
    """
    r = self.copy()
    possible_mut =\
      [ r.mut_size
      , r.mut_angle
      , r.mut_center
      ]
    choice(possible_mut)(genome)
    return r

  # adapted from http://lists.cairographics.org/archives/cairo/2006-April/006801.html
  def render(self, ctx):
    ctx.save()
    ctx.translate(self.x, self.y)
    ctx.rotate(self.angle)
    ctx.scale(self.width / 2.0, self.height / 2.0)
    ctx.arc(0.0, 0.0, 1.0, 0.0, 2.0 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(*self.color)
    ctx.fill()

class Polygon:
  def __init__(self, vertices, color):
    self.vertices = vertices
    self.color = color
  
  def __str__(self):
    return "<Polygon %d vertices, color: %s>" % (len(self.vertices), self.color)

  @property
  def desc(self):
    return '%d-gon' % len(self.vertices)

  def copy(self):
    return deepcopy(self)

  def mut_vertices(self, genome):
    v = choice(self.vertices)
    for dim in [0,1]:
      v[dim] += gauss(0,10)

  def mut_order(self, genome):
    vert_min = genome.getParam('vert_min')
    vert_max = genome.getParam('vert_max')
    pos = choice(xrange(len(self.vertices)))
    if randint(0,1):
      if len(self.vertices) < vert_max:
            self.vertices.insert(pos, randpoint(genome.width, genome.height))
    else:
      if len(self.vertices) > vert_min:
        del self.vertices[pos]

  def mutate(self, genome):
    """ 
    Return a mutated copy of this polygon
    This must be a copy because polygons may be shared by instances
    """
    r = self.copy()
    possible_mut =\
      [ r.mut_vertices
      , r.mut_order
      ]
    choice(possible_mut)(genome)
    return r


  @staticmethod
  def random(genome):
    v_min = genome.getParam('vert_min')
    v_max = genome.getParam('vert_max')
    width = genome.width
    height = genome.height
    vertices = [ randpoint(width, height) for i in range(randint(v_min,v_max)) ]
    color = randrgba()
    return Polygon(vertices, color)

  def render(self, ctx):
    ctx.set_source_rgba(*self.color)
    ctx.move_to(*self.vertices[0])
    for v in self.vertices[1:]:
      ctx.line_to(*v)
    ctx.fill()


class Candidate(GenomeBase):
  def __init__(self, target):
    GenomeBase.__init__(self)
    self.width, self.height = target.target.size
    self.target = target
    self.shapes= []

  def __repr__(self):
    r = GenomeBase.__repr__(self)
    r += "Polygons:\n"
    for t in self.shapes:
      r += '\t' + str(t) + '\n'
    return r

  def copy(self, g):
    """Copy method required by pyevolve"""
    GenomeBase.copy(self, g)
    g.shapes = self.shapes[:]
    g.target = self.target

  def clone(self):
    newcopy = Candidate(self.target)
    self.copy(newcopy)
    return newcopy

  def save(self, filename):
    """
    Render this candidate. Autodetect PNG or SVG
    """
    ext = os.path.splitext(filename)[1].lower()
    w, h = self.width, self.height
    if ext == '.svg':
      surface = cairo.SVGSurface(open(filename,'w'), w, h)
      self.cairo_draw(surface)
    elif ext == '.png':
      surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
      self.cairo_draw(surface)
      surface.write_to_png(filename)
    else:
      raise ValueError, "Unknown output format for final output: %s"% ext

  def savediff(self, target, filename):
    surf = self.asarray()
    trgt = target.target_im_array
    diff = numpy.abs(surf - trgt)
    diff[:,:,3] = 255
    im = Image.frombuffer("RGBA",(self.width,self.height),diff,"raw","RGBA",0,1)
    im.save(filename)

  def cairo_draw(self, surface):
    ctx = cairo.Context(surface)
    for s in self.shapes:
      s.render(ctx)

  def asarray(self):
    w, h = self.width, self.height
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    self.cairo_draw(surface)
    buf = surface.get_data()
    candidate_arr = numpy.frombuffer(buf, numpy.uint8).astype('int32')
    candidate_arr.shape = (self.height, self.width, 4)
    return candidate_arr

shape_generators =\
  [ Ellipse.random
  , Polygon.random
  ]

