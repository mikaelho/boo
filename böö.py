#coding: utf-8

import ui, math, random
from random import randint as rint
from vector import Vector
import numpy as np
from PIL import Image as PILImage
import io
import matplotlib.pyplot as plt

def snapshot(view):
  with ui.ImageContext(view.width, view.height) as ctx:
    view.draw_snapshot()
    return ctx.get_image()
    
def ui2pil(ui_img):
  return PILImage.open(io.BytesIO(ui_img.to_png()))
  
def inttuple(input_pair):
  return (int(input_pair[0]), int(input_pair[1]))
  
def get_radar(radius):
  points = radius * radius
  slice = 360/points
  
  origin = Vector()
  
  rays = []
  angles = []
  
  seen = set()
  for step in range(points):
    angle = round(step * slice, 4)
    endpoint = Vector(0, radius)
    endpoint.degrees = angle
    point_on_circle = tuple(round(endpoint))
    if point_on_circle not in seen:
      seen.add(point_on_circle)
      angles.append(angle)
      ray_steps = [
        tuple(s)
        for s in origin.steps_to(endpoint)
      ]
      rays.append(ray_steps)
      
  a = np.array(angles)
  r = np.array(rays).astype(int)
  
  return a, r

class Playground(ui.View):
  
  no_of_blocks = 30
  min_d = 10
  max_d = 50
  
  def __init__(self, radius=150, **kwargs):
    super().__init__(**kwargs)
    w,h = ui.get_screen_size()
    c_v = Vector(w/2, h/2)
    for _ in range(self.no_of_blocks):
      
      b_v = Vector(rint(0,w), rint(0,h))
      from_center = b_v - c_v
      if from_center.magnitude < self.max_d:
        from_center.magnitude += self.max_d
        b_v = c_v + from_center
      
      block = ui.View(
        width=rint(self.min_d, self.max_d),
        height=rint(self.min_d, self.max_d),
        center=tuple(b_v),
        background_color='black',
        border_color='grey',
        border_width=3
      )
      block.transform = ui.Transform.rotation(random.random() * math.pi)
      self.add_subview(block)
      

class FieldOfView(ui.View):
  
  def __init__(self, radius=150, **kwargs):
    super().__init__(**kwargs)
    self.playground = None
    self.heading = 0
    self.angles, self.rays = get_radar(radius)
    self.polygon = None
      
  def update(self):
    self.heading += 1
    self.set_heading()
      
  def set_heading(self):
    heading = self.heading
    h, w = self.playground.shape
    location = (int(w/2), int(h/2)) #inttuple(self.center)
    sector_angle = 210
    left_edge = (heading - sector_angle/2) % 360
    right_edge = (heading + sector_angle/2) % 360
    
    a = self.angles
    r = self.rays
    
    if left_edge < right_edge:
      sector = r[(a > left_edge) & (a < right_edge)]
    else: 
      # Concatenated for left-to-right sweep
      sector = np.concatenate((r[a > left_edge], r[a < right_edge]), axis=0)
    
    '''
    alpha_vector = [
      round(1-pow(step/radius,2), 4)
      for step in range(radius)
    ]
    '''
    '''
    playfield = np.random.choice([0, 2], size=(100,100), p=[19./20, 1./20])
    playfield[50,50] = 0
    '''
    
    #location = (50,50)
    playfield = self.playground
    sector_shifted = sector+location
    
    sector_hits = playfield[
      sector_shifted[:,:,1], # SWITCH
      sector_shifted[:,:,0]]
    sector_visible = np.add.accumulate(sector_hits, axis=1)
    sector_visible[sector_visible == 0] = 1
    sector_visible[sector_visible > 1] = 0
    
    obstacles = np.abs(np.sum(sector_visible, axis=1)-1)
    #print(np.any(obstacles))
    self.polygon = sector_shifted[
      np.arange(sector_visible.shape[0]),
      obstacles]
    self.set_needs_display()

  def draw(self):
    if self.polygon is None:
      '''
      rays = self.rays + inttuple(self.center)
      ui.set_color('blue')
      for ray in rays:
        for cx,cy in ray:
          p = ui.Path.oval(cx-1,cy-1,3,3)
          p.fill()
      '''
      return
    p = ui.Path()
    p.move_to(*self.center)
    for vertex in self.polygon:
      p.line_to(*vertex)
    p.line_to(*self.center)
    #ui.set_color((0,0,0,0.2))
    ui.set_color('white')
    #ui.set_shadow('white', 0, 0, 10)
    p.fill()
      
bg = ui.View(background_color='black')
bg.present('full_screen', hide_title_bar=True)

display_img = ui.Image('images/caves.JPG')
w,h = display_img.size
v = ui.ImageView(image=display_img, width=w, height=h, content_mode=ui.CONTENT_SCALE_ASPECT_FILL)
#v = Playground(background_color='#d2e7c9')
v.center = bg.bounds.center()

mask_img = ui.Image('images/caves_mask.PNG')
#img = snapshot(v)
img_array = np.array(ui2pil(mask_img))[::mask_img.scale,::mask_img.scale]/255
img_array = img_array[...,3]
#print(img_array)
img_array = np.where(img_array == 0, 1, 0)

'''
plt.clf()
plt.title('Alpha filtered')
plt.imshow(img_array)
plt.show()
'''

fov = FieldOfView(frame=v.bounds, flex='WH')
v.add_subview(fov)
v.objc_instance.setMaskView_(fov.objc_instance)
fov.playground = img_array
fov.update_interval = 1/60

bg.add_subview(v)



