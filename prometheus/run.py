
if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname as dir
    path.append (dir (path [0]))
    __package__ = "prometheus"

    from proxy.app import create_app
    from prometheus.callbacks import *

    app = create_app (softwareversion = "models-softwareversion.yaml", 
                      metrics = "models-metrics.yaml", 
                      objects = "models-objects.yaml",
                      objecttypes = "models-objecttypes.yaml", 
                      granularities = "models-granularities.yaml", 
                      statistics = "models-statistics.yaml",
                      config = "config.yaml",
                      callbacks = "callbacks.yaml")

    app.run (app.config ["systems"]["proxy_hostname"], app.config ["systems"]["proxy_port"], debug = True, use_reloader = False, threaded = True) 
