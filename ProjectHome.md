This project consists in implementation of **metaheuristics** for combinatorial optimization problems, as part of a [graduate course](http://www-di.inf.puc-rio.br/~poggi/mheu081.html) at PUC-Rio/Brazil.

The following metaheuristics were implemented:
  * GRASP
  * Simulated Annealing
  * Tabu Search

Those metaheuristics were applied to the following problems:
  * Traveling Salesman Problem ([TSP](TSP.md))
  * Unconstrained Binary Quadratic Problem ([UBQP](UBQP.md))
  * Dominant Set Problem ([DSP](DSP.md))
  * Capacitated Vehicle Routing Problem ([CVRP](CVRP.md))

Also, there are unfinished applications for the following problems:
  * Graph Coloring Problem (GCP)
  * University Course Timetabling Problem (UCTP)

All code implemented in Python is available at the [code repository](http://code.google.com/p/mh081/source/browse/trunk/src) and all experiments can be reproduced. The "template code" for the metaheuristics is implemented at the module local\_search.py. The module reports.py contains support code for generating graphs and reports. The "filling" code for metaheuristics is implemented on individual modules for each problem.

The [Project Report](http://mh081.googlecode.com/files/mh081_report.pdf) (in Portuguese) is available for download.