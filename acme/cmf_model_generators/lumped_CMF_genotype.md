# Lumped CMF model generator genotype
This file contains a detailed description on how the genotype for the lumped CMF model generator is implemented.

##Basic Layout
A model always consists of a least one storage with a linear connection to 
the outlet, as a model without any storages makes no sense. Also user 
defined calculation for the evapotranspiration is used. 

##Maximal Layout
If all possible things are implemented the model consists of:
- A snow storage were the snow melt temperature and the meltrate are calibrated
- A canopy where the LAI and the canopy closure are calibrated
- A first layer with nonlinear connections to the outlet, the river, and the
 second layer
- A second layer with nonlinear connections to the third layer and the river
- A third layer with nonlinear connections to the river
- A "river" layer with nonlinear connections to the outlet

##Creation
Starting from the basic layout all remaining possible elements are added at 
random. 

##Mutation
With a 1/3 chance up to three genes of the genotype are either swapped 
with a different gene, deleted or additional genes are added.

##Crossover
Crossover is performed using a simple single point crossover, meaning that two
 random point for the two genotypes of the parents are choosen. Then all 
 genes before the first point are taken from the first parent and all genes 
 after the second point are taken from the second parent. This is then 
 combined to form a new genotype. 
