# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 14:13:32 2016

@author: Florian Jehn
"""
from __future__ import division
import numpy as np
import os
import subprocess
from matplotlib import pyplot as plt
from matplotlib import animation
import copy

class Fluxogram:
    """
    a class to draw and maintain all fluxes and storages from a model or 
    some similiar kind of thing to be drawn as a sequence of storages 
    and fluxes. Storages and fluxes are not drawn proportional
    it should look something like this:
        
    order    offset=-1        center         offset=1
    ----------------------------------------------------
     1.      .       .       . stor1 .       .       . 
      .      .       .arrow  . arrow . arrow .       .
     2.      .stor2  .       . stor3 .       . stor4 .
      .      .       .       .       .       . arrow .
     3.      .       .       .       .       . stor5 .         
    """
    def __init__(self, max_flux, max_storage, grid_size = 20, storages = None, 
                 fluxes = None):
        """
        initilalizes a fluxogram. must be called with:
            - max_flux: aximum flux of all fluxes; needed for scaling
            - max_storage: maximum storages of all storages; needed for scaling
            - grid_size:grid_size for drawing the fluxogram, determines how big
                        everything is. Fluxes and storages  scaled accordingly
            - storages: all the storages the fluxogram has (usually empy to
                        begin with)
            - fluxes: all the fluxes the fluxogram has (usually empty to begin
                        with)            
        """
        if storages == None:
            self.storages = []
        if fluxes == None:
            self.fluxes = []
        self.max_flux = max_flux
        self.max_storage = max_storage
        self.grid_size = grid_size
    
    def add_storage(self, name, amount, order, offset):
        """
        add a storage to the storages of the fluxogram
        """
        # len(self.storages is used to give the storages consecutive numbers)
        self.storages.append(Storage(name, self.grid_size,len(self.storages) , 
                                     amount,  order, offset))
    
    def add_flux(self, name, from_storage, to_storage, amount):
        """
        add a flux to the fluxes of the fluxogram
        """
        self.fluxes.append(Flux(name, self.grid_size, from_storage, to_storage, 
                                amount))
    
    def update_all_storages(self, amounts):
        """
        updates the amount of all storages
        """
        for storage, amount in zip(self.storages, amounts):
            storage.update_storage(amount)
    
    def update_all_fluxes(self, amounts):
        """
        updates the amount of all fluxes
        """
        for flux, amount in zip(self.fluxes, amounts):
            flux.update_flux(amount)
        
    def update_everything(self, amounts_storages, amounts_fluxes):
        """
        updates all fluxes and storages
        """
        self.update_all_fluxes(amounts_fluxes)
        self.update_all_storages(amounts_storages)        
    
    def draw(self, day = -1):
        """
        draws all fluxes and storages
        """
        plt.axes()
        # find the smallest/largest offset_ so the fluxogram can be drawn big 
        # enough
        largest_offset = 0
        smallest_offset = 0
        largest_order = 0
        for storage in self.storages:
            if storage.offset > largest_offset:
                largest_offset = storage.offset
            if storage.offset < smallest_offset:
                smallest_offset = storage.offset
            if storage.order > largest_order:
                largest_order = storage.order
                
        # set y and x limits
        y_max = 0
        y_min = (largest_order + 1) * 2 * self.grid_size * -1
        x_max = (largest_offset + 2) * 2 * self.grid_size
        x_min = (smallest_offset - 1) * 2 * self.grid_size       
        plt.axis([x_min, x_max, y_min, y_max])
       
        # draw all fluxes
        for flux in self.fluxes:
            # scale the amount
            scaled_amount_flux = self.scaler(flux.amount, self.max_flux)
            # width multiplied  because if not, the arrows are so tiny
            arrow = plt.Arrow(flux.x_start, flux.y_start, flux.dx, flux.dy, 
                             width = scaled_amount_flux * 1.7, alpha = 0.8)
#                        # label all fluxes
#            plt.text(storage.x + self.grid_size * 0.1, 
#                     storage.y - self.grid_size * 1.2, flux.name, 
#                     fontsize = self.grid_size * 0.3)
            plt.gca().add_patch(arrow)
            
        # draw all storages
        for storage in self.storages:
            # scale the amount
            scaled_amount_stor = self.scaler(storage.amount, self.max_storage)
            if scaled_amount_stor == 0:
                scaled_amount_stor = 0.0001
            # change_x and y, so the storages are centered to the middle
            # of their position and not to upper left
            x = (storage.x + (1 - storage.amount / self.max_storage) * 0.5 
                 * self.grid_size)
            y = (storage.y - (1 - storage.amount / self.max_storage) * 0.5 
                 * self.grid_size)
            rectangle = plt.Rectangle((x, y), scaled_amount_stor,
                                      -scaled_amount_stor, alpha = 0.4)
            # label all storages
            plt.text(storage.x + self.grid_size * 0.1, 
                     storage.y - self.grid_size * 1.2, storage.name, 
                     fontsize = self.grid_size * 0.7)
            # draw a date 
            if day > -1:
                plt.text(x_min + 0.5 * self.grid_size,
                         y_min + 0.5 * self.grid_size, 
                         "Year: " + str(int(day/365)) + " Day: " + str(
                                                                    day % 365))
                
            plt.gca().add_patch(rectangle)
            
        
    def show(self):
        """
        shows the current fluxogram on screen
        """
        plt.show()
            
    
    def animate(self, timeseries_fluxes, timeseries_storages, anim_name):
        """
        animates the shit out of a timeseries
        flux and storage timeseries need to be equally long
        must be called with:
            - timeseries_fluxes: a timeseries with amounts for all fluxes for
                                every day of the timeseries
            - timeseries_storages: a timeseries with amounts for all storages 
                                for every day of the timeseries            
            - anim_name: the name the animation should have
        """
        # test if both time series are equally long
        if len(timeseries_fluxes) != len(timeseries_storages):
            print("Timeseries are not equally long, abort")
            return
        # make a deepcopy of the timeseries so the originals aren't changed
        
        timeseries_fluxes = copy.deepcopy(timeseries_fluxes)
        timeseries_storages = copy.deepcopy(timeseries_storages)           
        
        # draw all seperate fluxogram for all days and save them in working
        # directory
        print("Start making the single frames")
        for day in range(len(timeseries_fluxes)): 
            # if the values of the day in a timeseries are stored as a dict
            # it is changed to an list, so the fluxogram can use it
            # the order is after the alphabetical keys
            if type(timeseries_fluxes[day]) == dict and (
                                        type(timeseries_storages[day])==dict):
                temp_fluxes = []
                for key in sorted(timeseries_fluxes[day].keys()):
                    temp_fluxes.append(timeseries_fluxes[day][key])

                temp_storages = []
                for key in sorted(timeseries_storages[day].keys()):
                    temp_storages.append(timeseries_storages[day][key])
             #   print(temp_fluxes)
                timeseries_fluxes[day] = temp_fluxes
                timeseries_storages[day] = temp_storages
            
            self.update_everything(timeseries_storages[day], 
                                   timeseries_fluxes[day])
            self.draw(day)
            file_name = "_temp%05d.png" % day
            plt.savefig(file_name, dpi = 150)
            plt.clf()
            day += 1
            # tells the user that the program isn't crashed
            if day % 100 == 0:
                print("Working...please wait")
        # change directory to the current working directoy    
        cwd = os.getcwd()
        os.chdir(cwd)
        # try to delete videos with the same name as the one that is to be
        # made, as ffmpeg doesn't overwrite old ones. shell = True is needed
        # as only with this standart command line arguments can be used 
        try:
            subprocess.call("del " + anim_name + ".mpg", shell = True)
        except FileNotFoundError:
            print("No video with same name --> proceeding")
        print("Start making animation")    
        name = anim_name + ".mpg"
        # calls the command line and in there ffmpeg to stich all pictures 
        # together to one video
        subprocess.check_call(["ffmpeg","-r", "20", "-i", "_temp%05d.png",
                               name])
        print("Finished --> cleaning up")
        # delete all the temporary pictures
        subprocess.call("del _temp*.png", shell = True)      
        print("All done")
        
   
    def scaler(self, value_in, base_max):
        """
        scales the fluxes and storages, so they don't overstep their grafical
        bounds must be called with:
            - valueIn: the value that needs rescaling
            - baseMax: the upper limit of the original dataset
                    ~ 100 for fluxes, ~250 for stores (in my model)
        """
        # baseMin: the lower limit of the original dataset (usually zero)
        base_min = 0
        # limitMin: the lower limit of the rescaled dataset (usually zero)
        limit_min = 0
        # limitMax: the upper limit of the rescaled dataset (in our case  grid)
        limit_max = self.grid_size
        # prevents wrong use of scaler
        if value_in > base_max:
            raise ValueError("Input value larger than base max")        

        return (((limit_max - limit_min) * (value_in - base_min)
                / (base_max - base_min)) + limit_min)

class Flux:
    """
    a flux of a fluxogram
    """
    def __init__(self, name, grid_size, from_storage, to_storage, amount = 0):
        """
        initializes a flux with:
            - name: name of the flux
            - grid_size: grid size of the diagram
            - from_storage: storage the flux is originating from
            - to_storage: storage the flux is going into
            - amount: how much stuff fluxes
        """
        self.name = name
        self.from_storage = from_storage
        self.to_storage = to_storage
        self.amount = amount
        self.grid_size = grid_size
        self.x_start,self.y_start,self.x_end,self.y_end, self.dx, self.dy = (
                                                self.calc_start_end_dx_dy())
        
    def update_flux(self, amount):
        """
        update the amount of the flux
        """
        self.amount = amount
        
    def calc_start_end_dx_dy(self):
        """
        calculates the starting and ending point of an arrow depending on the 
        order and offset of the starting and ending storages. This helps 
        determine the direction of the arrow
        returns the start and end xy coordinates of the arrow as tuples
        """
        # small corrections of x_start/y_start are to make a little gap
        # between the arrow and the storage
        correction_factor = 0.25
        
        # arrow pointing to left up
        if (self.from_storage.offset > self.to_storage.offset and
            self.from_storage.order > self.to_storage.order):
            x_start = self.from_storage.x - self.grid_size * correction_factor
            y_start = self.from_storage.y + self.grid_size * correction_factor
            x_end = self.to_storage.x + self.grid_size
            y_end = self.to_storage.y - self.grid_size
            dx = abs(x_start - x_end) * (-1)
            dy = abs(y_start - y_end)       
        # arrow pointing up    
        elif (self.from_storage.offset == self.to_storage.offset and
              self.from_storage.order > self.to_storage.order):
            x_start = self.from_storage.x + 0.5 * self.grid_size 
            y_start = self.from_storage.y + self.grid_size * correction_factor
            x_end = self.to_storage.x + 0.5 * self.grid_size
            y_end = self.to_storage.y - self.grid_size
            dx = abs(x_start - x_end) 
            dy = abs(y_start - y_end)    
        # arrow pointing right up    
        elif (self.from_storage.offset < self.to_storage.offset and
              self.from_storage.order > self.to_storage.order):
            x_start = (self.from_storage.x + self.grid_size + self.grid_size * 
                       correction_factor)
            y_start = self.from_storage.y + self.grid_size * correction_factor
            x_end = self.to_storage.x
            y_end = self.to_storage.y - self.grid_size
            dx = abs(x_start - x_end) 
            dy = abs(y_start - y_end)  
            # arrow pointing right    
        elif (self.from_storage.offset < self.to_storage.offset and
              self.from_storage.order == self.to_storage.order):
            x_start = (self.from_storage.x + self.grid_size + self.grid_size * 
                       correction_factor)
            y_start = self.from_storage.y - 0.5 * self.grid_size
            x_end = self.to_storage.x 
            y_end = self.to_storage.y - 0.5 * self.grid_size      
            dx = abs(x_start - x_end) 
            dy = abs(y_start - y_end)    
            # arrow pointing right down    
        elif (self.from_storage.offset < self.to_storage.offset and
              self.from_storage.order < self.to_storage.order):
            x_start = (self.from_storage.x + self.grid_size + self.grid_size * 
                       correction_factor)
            y_start = (self.from_storage.y - self.grid_size - self.grid_size *
                       correction_factor)
            x_end = self.to_storage.x 
            y_end = self.to_storage.y       
            dx = abs(x_start - x_end) 
            dy = abs(y_start - y_end) * (-1)
            # arrow pointing down    
        elif (self.from_storage.offset == self.to_storage.offset and
              self.from_storage.order < self.to_storage.order):
            x_start = self.from_storage.x + 0.5 * self.grid_size
            y_start = (self.from_storage.y - self.grid_size - self.grid_size * 
                       correction_factor)
            x_end = self.to_storage.x + 0.5 * self.grid_size
            y_end = self.to_storage.y    
            dx = abs(x_start - x_end) 
            dy = abs(y_start - y_end) * (-1)  
            # arrow pointing left down    
        elif (self.from_storage.offset > self.to_storage.offset and
              self.from_storage.order < self.to_storage.order):
            x_start = self.from_storage.x - self.grid_size * correction_factor
            y_start = (self.from_storage.y - self.grid_size - self.grid_size *
                       correction_factor)
            x_end = self.to_storage.x + self.grid_size
            y_end = self.to_storage.y    
            dx = abs(x_start - x_end) * (-1)
            dy = abs(y_start - y_end) * (-1)
            # arrow pointing left    
        elif (self.from_storage.offset > self.to_storage.offset and
              self.from_storage.order == self.to_storage.order):
            x_start = self.from_storage.x - self.grid_size * correction_factor
            y_start = self.from_storage.y - 0.5 *self.grid_size
            x_end = self.to_storage.x + self.grid_size
            y_end = self.to_storage.y - 0.5 * self.grid_size  
            dx = abs(x_start - x_end) * (-1)
            dy = abs(y_start - y_end)    
        
        # multiply by 0.9 so there is a gap between storages and arrows
        dx = dx * 0.75
        dy = dy * 0.75
        
        return x_start, y_start, x_end, y_end, dx, dy
    
class Storage:
    """
    a storage of a fluxogram
    """
    def __init__(self, name, grid_size, number, amount = 0, order = 0, 
                 offset = 0):
        """initializes a storage with:
                - name: name of the storage
                - number: consecutive number
                - grid_size of the diagram
                - amount: how much stuff is in it
                - order: how much down it is in the hierachie (starts with 0)
                - offset = how much the storage is offset to the left/right
                    in relationship to the center
        """
        self.name = name
        self.amount = amount
        self.number = number
        self.order = order
        self.offset = offset
        self.grid_size = grid_size
        self.x, self.y = self.calculate_xy()
        
    def update_storage(self, amount):
        """
        update the amount of the storage
        """
        self.amount = amount
        
    def calculate_xy(self):
        """
        calculates the xy coordinates of the starting point from where
        the recangle is drawn. The additional multiplication by two is
        to produce the gaps in the diagram
        """
        x = self.offset * self.grid_size * 2
        # multiply by -1 to draw the diagram from top to bottom
        y = self.order * self.grid_size * 2  * -1 
        return x,y        
    
if __name__ == "__main__":
    """
    Example of usage
    """    
    # make a fluxgram instance
    fl = Fluxogram(100, 150, grid_size = 10)
    
    # add storages
    fl.add_storage("up", 23, 0, 0)
    fl.add_storage("right", 130, 1, 1)
    fl.add_storage("middle", 149, 1, 0)
    fl.add_storage("right_up", 90, 0, 2)
    fl.add_storage("right_down", 50, 2, 1)
    fl.add_storage("down", 23, 2, 0)
    fl.add_storage("left_down", 76, 2, -1)
    fl.add_storage("left", 43, 1, -2)
    fl.add_storage("left_up", 34, 0, -1)
    fl.add_storage("down_down", 78, 3, 0)
    
    # add fluxes
    fl.add_flux("middle_to_up", fl.storages[2], fl.storages[0], 30) 
    fl.add_flux("middle_to_right_up", fl.storages[2], fl.storages[3], 50) 
    fl.add_flux("middle_to_right", fl.storages[2], fl.storages[1], 100) 
    fl.add_flux("middle_to_right_down", fl.storages[2], fl.storages[4], 35) 
    fl.add_flux("middle_to_down", fl.storages[2], fl.storages[5], 50) 
    fl.add_flux("middle_to_left_down", fl.storages[2], fl.storages[6], 10) 
    fl.add_flux("middle_to_left", fl.storages[2], fl.storages[7], 50) 
    fl.add_flux("middle_to_left_up", fl.storages[2], fl.storages[8], 25)
    fl.add_flux("down_to_down_down", fl.storages[5], fl.storages[9], 25)
    fl.add_flux("down_to_left_down", fl.storages[5], fl.storages[4], 25)  
    
    # draw
    fl.draw()
    
    # show the fluxgram
    fl.show()
    
    # generate data for updating the plots and 
    data_fluxes = np.random.uniform(0, fl.max_flux, len(fl.fluxes))
    data_storages = np.random.uniform(0, fl.max_storage, len(fl.storages))
            
    # update fluxes/storages
    fl.update_everything(data_storages, data_fluxes)
    
    # draw again
    fl.draw()
    fl.show()
        
    # generate random somehow oscillating data for animation 
    timeseries = {"fluxes" : {}, "storages" : {}}
    timespan_timeseries = 50
    timeseries["fluxes"][0] = data_fluxes
    timeseries["storages"][0] = data_storages
    for day in range(1, timespan_timeseries):
        timeseries["fluxes"][day] = []
        for flux in range(len(timeseries["fluxes"][0])):
            upper_limit = timeseries["fluxes"][day - 1][flux] + 6
            lower_limit = timeseries["fluxes"][day - 1][flux] - 5
            new_flux = np.random.randint(lower_limit, upper_limit)
            timeseries["fluxes"][day].append(new_flux)
            if timeseries["fluxes"][day][flux] > fl.max_flux:
                timeseries["fluxes"][day][flux] = fl.max_flux
            if timeseries["fluxes"][day][flux] < 0:
                timeseries["fluxes"][day][flux] = 0

        timeseries["storages"][day] = []
        for storage in range(len(timeseries["storages"][0])):
            upper_limit = timeseries["storages"][day - 1][storage] + 6
            lower_limit = timeseries["storages"][day - 1][storage] - 5
            new_storage = np.random.randint(lower_limit, upper_limit)
            timeseries["storages"][day].append(new_storage)
            if timeseries["storages"][day][storage] > fl.max_storage:
                timeseries["storages"][day][storage] = fl.max_storage
            if timeseries["storages"][day][storage] < 0:
                timeseries["storages"][day][storage] = 0

    # animate the timeseries
    fl.animate(timeseries["fluxes"], timeseries["storages"], 
               "example_animation")  

                
        
         
        
        
    