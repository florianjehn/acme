## What is ACME?

ACME is unsurprisingly an acronym, which stands for "Automated construction of models by evolution".  It does not, as one might think, stand for "A company that manufactures everything", though in its core it is more or less meant to manufacture everything, at least in the field of conceptual hydrological models. 

## Well this seems interesting, but how does it do this?

Mainly by the the the combination of three tools: 

1) [The Catchment Modeling Framework (CMF)](http://fb09-pasig.umwelt.uni-giessen.de/cmf "The Catchment Modeling Framework")

2) [SPOTPY](http://fb09-pasig.umwelt.uni-giessen.de/cmf "SPOTPY")

3) [Evolutionary algorithms](https://en.wikipedia.org/wiki/Evolutionary_algorithm "Evo")


At first a starting population of models is constructed using CMF. Those models are then tested for their predictive capability using SPOTPY. All models not able to make at least somewhat realistic predictions are excluded. The remaining models are sorted along the quality of their prediction. Then a new generation of models is automatically created. The better performance of a given model, the higher the chance its properties will make it to this next generation. This new generation serves as the next starting point and the whole process is repeated until a sufficient performance is reached. 

## And then what?
The final model emerging from the process above is interesting for two reasons:

1) Predictive capability: As the models properties for prediction were selected and honed over several generations, the model should be able to give quite accurate predictions of the discharge in the catchment it was evolved for. Allowing precise predictions.

2) Insights in catchment structure: As the geology and the soils of a catchment do not change rapidly, its water flows always stride towards an equilibrium, as long as no chances are made. Thus, the model which describes the catchment best, should also be the model which is closest to the reality of the catchment. So if ACME is able to build a well matching model for the catchment, this model could give insights into how the catchment functions. 

## Sounds useful, can I participate?
Yeah, sure. Just comment on [Github](https://github.com/zutn/ACME) or contact me on [Research Gate](https://www.researchgate.net/profile/Florian_Jehn). Also, regular updates on the progress will be made on Research Gate. 