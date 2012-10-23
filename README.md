#EvolveConfig
An EA that will tune a slicing profile to print optimally for any printer.

#Motivation
Not all models and printers are made equal; some print jobs requrie more tuning than others.  In an attempt to ameleorate this hardships, EvolveConfig is a python evolutionary algorithms that attempts to evolve slicing configs for you.

#Slicing Configs
Slicing configs are expected in JSON.  A map should be supplied, which both delineates the values to be evolved and the max/min values for each entry.  We expect something that looks like this:

{
    "slicingprofile" : {
        "layerheight" : ["r", 0, 1],
        "someparam" : ["r", -50.0, 50.0],
        "someSubTree" : {
            "paramA" : ["l", 0, 1],
            "paramB" : ["l", 0, 1, 2, 3, 4, 5],
}

Each entry can be one of two types: a min/max random pair or a selection list (delineated by a r or l, respectively).  A min/max random pair will generate a number greater than or equal to the min and less than or equal to the max.  If the number is a decimal, a random decimal will be generated (similarly, an int yields an int).  For selection, and value can be used.  The config map should be a subset of the standard config, and only those that are evolvable should be included.
