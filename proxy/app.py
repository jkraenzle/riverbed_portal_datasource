from datetime import datetime
import yaml
import importlib.util
from importlib import import_module

from flask import Flask, jsonify, request
from flask.json import JSONEncoder
# from flask_caching import Cache

from portal.objects import *

# Define custom JSON encoder for Portal Objects
class PortalObjectJSONEncoder (JSONEncoder):
    def default (self, obj):
        if hasattr (obj, "attributes"):
            return obj.attributes
        else:
            return JSONEncoder.default (self, obj)

def object_filters_from_json (object_filters):
    
    ofs = []
    for object_filter in object_filters:
        of = ObjectFilter (object_filter ["object_type_id"], object_filter ["instance_id"]) 
        ofs.append (of)

    return ofs

def object_filters_from_request (request):

    object_filters_json = request.get_json (force = True)
    
    return object_filters_from_json (object_filters_json)

def granularity_from_request (request):
    granularity_json = request.args.get ("granularity_id")

    step = 60

    options = {"1m": 60,
               "5m": 300,
               "15m": 900,
               "1h": 3600,
               "8h": 28800,
               "1d": 86400}

    if granularity_json in options:
       step = options [granularity_json]
      
    return step  

def start_end_times_from_request (request):
    start_time_seconds = int (request.args.get ("start_time_seconds"))
    end_time_seconds = int (request.args.get ("end_time_seconds"))

    # start and end times from Portal are Epoch - GMT/UTC
    start_time = datetime.utcfromtimestamp (start_time_seconds)
    end_time = datetime.utcfromtimestamp (end_time_seconds)

    return (start_time_seconds, end_time_seconds)

def load_config (conf_file = ""):
    config = {}

    cfg = None
    with open (conf_file) as f:
        cfg = yaml.full_load (f)
    config ["systems"] = cfg
 
    return config
    
def load_models (softwareversion = "", metrics = "", objects = "", objecttypes = "", granularities = "", statistics = ""):
   
    config = {}

    sv = None
    with open (softwareversion) as f:
        sv = yaml.full_load (f)
    config ["softwareversion"] = sv 
    
    m = None
    with open (metrics) as f:
        m = yaml.full_load (f)
    config ["metrics"] = m

    o = None
    with open (objects) as f:
        o = yaml.full_load (f)
    config ["objects"] = o

    ot = None
    with open (objecttypes) as f:
        ot = yaml.full_load (f)
    config ["objecttypes"] = ot

    g = None
    with open (granularities) as f:
        g = yaml.full_load (f)
    config ["granularities"] = g

    s = None
    with open (statistics) as f:
        s = yaml.full_load (f)
    config ["statistics"] = s

    return config 

def get_function (callback):
    imported_function = None

    module_name, function_name = callback.rsplit (".", 1)
    spec = importlib.util.find_spec (module_name)
    if (spec is not None):
        module = spec.loader.load_module ()
        imported_function = getattr (module, function_name) 
    
    return imported_function

def load_callbacks (callbacks):
    config = {}

    cs = None
    with open (callbacks) as f:
        cs = yaml.full_load (f)
    config ["callbacks"] = cs

    # If loaded, check that module and function are imported, and if not, import right away
    callback_names = ["object_search", "topn_search", "time_series_data"]

    for callback_name in callback_names:

        module_function_name = config ["callbacks"][callback_name]
        if module_function_name == "":
            continue
        
        imported_function = get_function (module_function_name)

        if imported_function is not None:
            continue
        else:
            return None

    return config

def create_app (softwareversion, metrics, objects, objecttypes, granularities, statistics, config, callbacks):
    
    app = Flask (__name__)

    # Assign custom JSON encoder
    app.json_encoder = PortalObjectJSONEncoder

    # Initialize configurations and definitions
    app.config.update (load_config (conf_file = config))

    app.config.update (load_callbacks (callbacks = callbacks))

    app.config.update (load_models (softwareversion = softwareversion, metrics = metrics, objects = objects, 
        objecttypes = objecttypes, granularities = granularities, statistics = statistics))

    # Initialize cache?

    # Connect to targets?
    @app.route('/portal-api/v1/software_version')
    def software_version ():
        sv = app.config ["softwareversion"]
        version = SoftwareVersion (data_source_type = sv ["data_source_type"],
                          major_version = sv ["major_version"],
                          minor_version = sv ["minor_version"],
                          display_string = sv ["display_string"],
                          revision_number = sv ["revision_number"],
                          build_number = sv ["build_number"])

        return jsonify (version)

    @app.route('/portal-api/v1/preferences')
    def preferences ():
        return jsonify (Preferences (update_object_cache_on_initial_sync = True,
                               data_request_max_thread_count = 4,
                               data_request_batch_limit = 500,
                               heartbeat_request_interval_seconds = 60,
                               always_request_recent_data = True
                               ))

    @app.route('/portal-api/v1/granularities')
    def granularities():
        gs = []

        for g in app.config ["granularities"]:
            ### removed description and is_global while troubleshooting
            gs.append (Granularity (granularity_id = g ["granularity_id"], value_seconds = g ["value_seconds"],
                        time_window_seconds = g ["time_window_seconds"], display_name = g ["display_name"],
                        storage_duration = g ["storage_duration"]))

        return jsonify (gs)


    @app.route('/portal-api/v1/object_types')
    def object_types():
        ots = []

        for ot in app.config ["objecttypes"]:
           ### add more options from file?
           ots.append (ObjectType (id = ot ["id"], display_name = ot ["display_name"], 
               plural_display_name = ot ["plural_display_name"], root_type = ot ["root_type"], enumerable = ot ["enumerable"],
               applicable_metrics = ot ["applicable_metrics"]))

        return jsonify (ots)


    @app.route('/portal-api/v1/launch_urls')
    def launch_urls():
        urls = []
        return jsonify(urls)


    @app.route('/portal-api/v1/default_thresholds')
    def default_thresholds():
        thresholds=[]
        return jsonify(thresholds)


    @app.route('/portal-api/v1/metrics')
    def metrics():

        ms = []
        for m in app.config ["metrics"]:
            ms.append (Metric (metric_id = m ["metric_id"], unique_display_name = m ["unique_display_name"],
                unit = m ["unit"]))

        return jsonify (ms)

    @app.route('/portal-api/v1/statistics')
    def statistics():
  
        ### update with pull from file for all parameters 
        stats = []
        for s in app.config ["statistics"]:
            stats.append (Statistic (id = s ["id"],
                        display_name = s ["display_name"],
                        is_default = s ["is_default"],
                        is_primary = s ["is_primary"],
                        suggested_aggregation_rule = None,
                        data_points_time_aligned = False))
                               
        return jsonify (stats)


    @app.route('/portal-api/v1/object_property_definitions')
    def object_property_definitions():
    
        prop_defs = []
        return jsonify(prop_defs)


    @app.route('/portal-api/v1/object_search', methods = ["post"])
    def object_search():
        object_search_callback = get_function (app.config ["callbacks"]["object_search"])

        object_filters = object_filters_from_request (request)

        ### for now, do not use time in object search
        ### start_time, end_time = start_end_times_from_request (request)
        
        result = object_search_callback (app, object_filters) 

        return jsonify (result)

    @app.route("/portal-api/v1/time_series_data", methods = ["post"])
    def time_series_data():
        time_series_data_callback = get_function (app.config ["callbacks"]["time_series_data"])

        data_responses = []
        suggested_summary_rule = None
        start_time, end_time = start_end_times_from_request (request)
        granularity = granularity_from_request (request)

        for data_request in request.json:
            request_id = data_request ["data_request_id"]
            object_filters = object_filters_from_json (data_request ["object_filters"])

            metric_ids = list (map (lambda m: m ["metric_id"], data_request ["metric_statistic_ids"]))
            ### for now, make an assumption here
            statistic_id = "raw"

            data_responses_from_request = time_series_data_callback (app, object_filters, metric_ids, statistic_id, request_id, 
                suggested_summary_rule, start_time, end_time, granularity)
            data_responses.extend (data_responses_from_request)

        return jsonify (data_responses)

    @app.route("/portal-api/v1/topn_search", methods=["post"])
    def topn_search():
        topn_search_callback = get_function (app.config ["callbacks"]["topn_search"])

        object_filters = object_filters_from_request (request)
        start_time, end_time = start_end_times_from_request (request)
        metric_id = request.args.get ("metric_id")
        n_value = request.args.get ("n_value")
        ascending = request.args.get ("ascending")

        result = topn_search_callback (app, object_filters, metric_id, n_value, start_time, end_time, ascending)

        return  jsonify (result)
   
    return app 
