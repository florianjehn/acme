# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 15:42:56 2016

@author: Florian Jehn
"""
import copy

def storages_of_cell(node, cell, nodes_so_far = None):
    """
    gets the storage of all nodes of a cell of a lumped
    model 
    must be called with:
        - starting node: usually cell.rain_source
        - cmf cell that contains the storages
        
    returns:
        - a dict, which contains all nodes with their storage
    """
    # make a seperate dict for several runs, otherwise all will point to the
    # same dict, with horrible consequences
    if nodes_so_far == None:
        nodes_so_far = {}
    # add the volume of the current node
    # some nodes don't have a volume function, so their volume is set to 0
    try:
        nodes_so_far[str(node)] = node.volume
    except AttributeError:
        nodes_so_far[str(node)] = 0
    
    # find out what the neighbouring nodes of the current node are
    neighbours = node.connected_nodes
   
    # check if the neighbours of the current mode are already in the dict
    # if not add them to nodes_so_far  be recusively calling storage_of_cell
    for neighbour in neighbours:
        if str(neighbour) not in nodes_so_far.keys():
            nodes_so_far.update(storages_of_cell(neighbour, cell, 
                                                 nodes_so_far))
            
    return nodes_so_far
    
def flux_of_all_nodes_of_cell(node, cell, timestep, nodes_so_far = None):
    """
    gets the flux from all nodes to all the other nodes by iterating recusively
    through all nodes
    must be called with:
       - node that is the starting point (usually cell.rain_source)
       - cmf cell that containt the model to be mapped
       - timestep for when the fluxes should be determined
       - nodes_so_far -> a dict that containts all nodes that have been found
            so far. Starts usually as empty dict
            
    returns:
        a dict of dicts, where dict contains all nodes and dicts contains 
        all fluxes from and to that node, all positive fluxes are goint to that
        node and all negative fluxes are coming from that node
    """
    # make a seperate dict for several runs, otherwise all will point to the
    # same dict, with horrible consequences
    if nodes_so_far == None:
        nodes_so_far = {}
    # find out what the neighbouring nodes of the current node are
    neighbours = node.connected_nodes
    # make a new entry for the current node
    nodes_so_far[str(node)] = {}
        
    # add all fluxes from the current node to his neighbouring nodes
        
    for neighbour in neighbours:
        
        nodes_so_far[str(node)][str(neighbour)] = node.flux_to(neighbour, 
                                                                 timestep)    
    # check if the neighbours of the current mode are already in the dict
    # if not add them to nodes_so_far with all their fluxes to their neighbours
    # be recusively calling flux_of_all_nodes
    for neighbour in neighbours:
        if str(neighbour) not in nodes_so_far:
            nodes_so_far.update(flux_of_all_nodes_of_cell(neighbour, cell, 
                                                          timestep, 
                                                          nodes_so_far)) 
    return nodes_so_far
    
def convert_fluxes_for_fluxogram(all_fluxes):
    """
    converts the usual output of the recursive search through the model to
    a form that is more easyly to use in a fluxogram.
    - all_fluxes = dict of dicts of all fluxes for one timestep
    returns
    a dictionary where the key has the form 
    node where the water comes from to node where the water goes to
    """
    fluxes_for_fluxogram = {}
    # go through all nodes where the water is coming or going from and then
    # go through all nodes that are connected to that node and check if they
    # have a negative value and only save the positive values. This makes
    # the output easier to interpret as CMF always gives you the flow from and
    # to another node. If you go through all nodes, this results is 
    # redundant data
    for from_storage in all_fluxes:
        for to_storage in all_fluxes[from_storage]:
            # - 0.0 has to be kicked out as well because its origin is a 
            # negative value that needs to be kicked out for further analysis
            if all_fluxes[from_storage][to_storage] >= 0 and (
                                str(all_fluxes[from_storage][to_storage]
                                ) != str(-0.0)):
                fluxes_for_fluxogram[from_storage + " to " + to_storage] = (
                                        all_fluxes[from_storage][to_storage])
    return fluxes_for_fluxogram     
    
    
def del_empty_nodes(model_results):
    """
    checks if the sum of a flux/storage in a timeseries is 0 and deletes it 
    form the dict to make it easier to use
    - model results: results of a repeated recursive search through the model. 
                    it is assumed that fluxes have been converted with the 
                    above function such that fluxes and storages are ordered 
                    alike. The structure is a list of dicts of numbers
                    Also it is assumed that the keys don't change over time
    returns: a dictionary that has been stripped of emtpy entries
    """
    empty_series = {}
    # find all the keys there are
    # because of the way the data is created the different days can have a 
    # different amount of keys at this stage of the program. To avoid key 
    # errors one first has to find the day with the most keys and use this
    # for further analyses
    most_keys_day = 0
    most_keys = 0
    for date in range(len(model_results)): 
        if len(model_results[date]) > most_keys:
            most_keys = len(model_results[date])
            most_keys_day = date
    all_keys = model_results[most_keys_day].keys()
    # make a dict with all keys
    for key in all_keys:
        empty_series[key] = 0    
    # iterate through all days and add the values for each key seperately
    for day in range(len(model_results)):
        for key in model_results[day]:
            empty_series[key] += model_results[day][key]
    # if the sum of all entries is 0, delete the node/flux   
    for day in range(len(model_results)):
        keys = model_results[day].keys()
        for key in keys:
            if empty_series[key] <= 0:
              #  print(day)
                del model_results[day][key]
            
#    for key in all_keys:
#        if empty_series[key] <= 0:
#            model_results_temp = copy.deepcopy(model_results)
#            for day in range(len(model_results_temp)):
#                del model_results[day][key]   
    
    return model_results
    
    
    
if __name__ == "__main__":
    """
    example of usage
    important: If you want to use this functions in your own model you have 
    to import this file to the file of your own model using 'import'
    """
    # make a simple cmf model with a surfacewater, soil and an outlet
    import numpy as np
    import cmf
    import datetime
    p = cmf.project()
    c = p.NewCell(0,0,0,1000)
    
    # create the storages/outlet
    c.surfacewater_as_storage()
    c.add_layer(5.0)
    outlet = p.NewOutlet("outlet", 10,0,0)
    
    # add the connections between the storages
    cmf.kinematic_wave(c.surfacewater, outlet, 1)
    cmf.kinematic_wave(c.surfacewater, c.layers[0], 1)
    cmf.kinematic_wave(c.layers[0], outlet, 3)    
    
    # create artificial rain data
    begin = datetime.datetime(1979,1,1)
    end = begin + 15 * datetime.timedelta(days = 1)
    step = datetime.timedelta(days=1)
    
    P = cmf.timeseries(begin, step)
    P.extend(prec for prec in np.random.randint(0, high = 30, size = 15))
    
    # add a rainstation
    rainstation = p.rainfall_stations.add("Rain", P, (0,0,0))
    p.use_nearest_rainfall()
    
    # create a solver
    solver = cmf.CVodeIntegrator(p, 1e-8)
    
    # create lists to store the results of the fluxes and storages
    timeseries_fluxes = []
    timeseries_storages = []

    # let the solver run for our timeperiod    
    for t in solver.run(begin, end, cmf.day):
        fluxes_raw = flux_of_all_nodes_of_cell(c.rain_source, c, t)
        # to get an easier to grasp of the output of the fluxes it can be 
        # converted using the following function
        fluxes_nicer = convert_fluxes_for_fluxogram(fluxes_raw)
        timeseries_fluxes.append(fluxes_nicer)
        timeseries_storages.append(storages_of_cell(c.rain_source, c))
        

    # due to the way CMF constructs models and how this program searches 
    # through it, nodes with no fluxes and storage can occur.
    # To get rid of them the following function can be useful
    # but be careful as sometimes those empty timeseries emerge because
    # you did something wrong and not the code          
    timeseries_fluxes_stripped = del_empty_nodes(timeseries_fluxes)
    timeseries_storages_stripped = del_empty_nodes(timeseries_storages)
    
    # and now lets look on the results
    for day, day_counter in zip(timeseries_storages_stripped, range(len(
                                            timeseries_storages_stripped))):
        print("Storages volumes on day: " + str(day_counter))       
        print(day)
        print("")
        
    for day, day_counter in zip(timeseries_fluxes_stripped, range(len(
                                                timeseries_fluxes_stripped))):
        print("Fluxes volumes on day: " + str(day_counter))       
        print(day)
        print("")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

      