import random

class Param:
    def __init__(self, thres, min, max, test=False):
        self.test=test

    def applies(self):
        return random.random()<self.thres or self.test
class Gene:
    def __init__(self, **kwargs):
        self.params = kwargs
genes={['snow'] : Gene(meltrate=Param(0.5,0.5,20),
            melt_temp=Param(0.5, -2., 2.))}
        
        
expressed_genes = []
