import ui, objc_util, ctypes
from ctypes import *

UIGraphicsGetCurrentContext = objc_util.c.UIGraphicsGetCurrentContext
UIGraphicsGetCurrentContext.restype = ctypes.c_void_p
UIGraphicsGetCurrentContext.argtypes = []

CGColorSpaceCreateDeviceRGB = objc_util.c.CGColorSpaceCreateDeviceRGB
CGColorSpaceCreateDeviceRGB.restype = c_void_p
CGColorSpaceCreateDeviceRGB.argtypes = []

CGColorSpaceRelease = objc_util.c.CGColorSpaceRelease
CGColorSpaceRelease.restype = None
CGColorSpaceRelease.argtypes = [c_void_p]

CGFloat_p = ctypes.POINTER(objc_util.CGFloat)
CGGradientCreateWithColors = objc_util.c.CGGradientCreateWithColors
CGGradientCreateWithColors.restype = c_void_p
CGGradientCreateWithColors.argtypes = [c_void_p, c_void_p, CGFloat_p]

CGGradientRelease = objc_util.c.CGGradientRelease
CGGradientRelease.restype = None
CGGradientRelease.argtypes = [c_void_p]

CGContextDrawLinearGradient = objc_util.c.CGContextDrawLinearGradient
CGContextDrawLinearGradient.restype = None
CGContextDrawLinearGradient.argtypes = [ c_void_p, c_void_p,
  objc_util.CGPoint, objc_util.CGPoint,
  objc_util.NSUInteger]

CGContextDrawRadialGradient = objc_util.c.CGContextDrawRadialGradient
CGContextDrawRadialGradient.restype = None
CGContextDrawRadialGradient.argtypes = [ c_void_p, c_void_p,
  objc_util.CGPoint, objc_util.CGFloat,
  objc_util.CGPoint, objc_util.CGFloat,
  objc_util.NSUInteger]


class Gradient(ui.View):
  
  def __init__(self,
  colors, locations=(0.0, 1.0), centers=None, radial=False, radiuses=None,
  **kwargs):
    super().__init__(**kwargs)
    assert len(colors) == len(locations)
    self.colors = [
      objc_util.UIColor.colorWithRed_green_blue_alpha_(*ui.parse_color(color)).CGColor()
      for color in colors
    ]
    self.locations = (objc_util.CGFloat * len(locations))(*locations)
    self.centers = centers
    self.radial = radial
    self.radiuses = radiuses
    
  def draw(self):
    c = UIGraphicsGetCurrentContext()
    colorSpace = CGColorSpaceCreateDeviceRGB()
    '''
    start = objc_util.UIColor.colorWithRed_green_blue_alpha_(1.0,1.0,1.0,1.0)
    end = objc_util.UIColor.colorWithRed_green_blue_alpha_(1.0,1.0,1.0,0.0)
    colors = [start.CGColor(), end.CGColor()]
    locations = (objc_util.CGFloat * 2)(0.8,1.0)
    '''
    gradient = CGGradientCreateWithColors(colorSpace, objc_util.ns(self.colors),  ctypes.cast(self.locations, CGFloat_p))
    CGColorSpaceRelease(colorSpace)


    if self.centers is not None:
      center1 = objc_util.CGPoint(*self.centers[0])
      center2 = objc_util.CGPoint(*self.centers[1])
    elif self.radial:
      center1 = center2 = objc_util.CGPoint(*self.bounds.center())
    else:
      center1 = objc_util.CGPoint(0,0)
      center2 = objc_util.CGPoint(self.width, 0)
      
    if not self.radial:
      CGContextDrawLinearGradient(c, gradient, center1, center2, 0)
    else:
      if self.radiuses is None:
        r = self.radiuses = []
        r.append(0)
        r.append(self.width/2)
      assert len(self.radiuses) == 2
      CGContextDrawRadialGradient(
        c, gradient,
        center1, self.radiuses[0],
        center2, self.radiuses[1],
        0
      )
    CGGradientRelease(gradient)

if __name__ == '__main__':
  
  v = Gradient(
    ['grey', 'black'], locations=[0.0, 0.6])

  v.present('full_screen', hide_title_bar=True)
  
  v2 = Gradient(
    ['white', 'transparent'], radial=True,
    width=200, height=200)
  v2.center = v.bounds.center()
  v.add_subview(v2)
