from portal.objects import *
from prometheus.api import time_range_values

def object_search (app, object_filters):

    search_response = SearchResponse (valid_interval = 120)

    for object_filter in object_filters:
        portal_objects = app.config ["objects"]
        for portal_object in portal_objects:
            if (object_filter.object_type_id == portal_object ["object_type_id"]):
                if (object_filter.instance_id == portal_object ["object_id"]) or (object_filter.instance_id == "*"):
                    obj = ObjectDefinition (object_type_id = portal_object ["object_type_id"], object_id = portal_object ["object_id"],
                        display_name = portal_object ["display_name"])  
                    search_result = SearchResult (obj = obj, value = 100, parent_object_filters = [object_filter])
                    search_response.add_search_result (search_result)
                
    return search_response

def topn_search (app, object_filters, metric_id, n_value, start_time, end_time, ascending):
    target_hostname = app.config ["systems"]["target_hostname"]
    target_port = app.config ["systems"]["target_port"]

    search_response = object_search (app, object_filters)
    step = int(end_time) - int(start_time)

    # pull objects out of search results

    # iterate over search results and update values
    for search_result in search_response.search_results:
        obj = search_result.object
        metric_query = "sum (" + metric_id + "{" + obj.object_type_id + "=\"" + obj.object_id + "\"})"
       
        search_result.value = time_range_values (hostname = target_hostname, port = target_port, query_string = metric_query, 
            start_time = start_time, end_time = end_time, step = step, top = True)

    # sort and top
    search_response.search_results.sort (reverse = not ascending)
    search_response.search_results [:int (n_value)]

    return search_response


def time_series_data (app, object_filters, metric_ids, statistic_id, request_id, suggested_summary_rule, start_time, end_time, step):
    
    target_hostname = app.config ["systems"]["target_hostname"]
    target_port = app.config ["systems"]["target_port"]

    search_response = object_search (app, object_filters)
     
    for search_result in search_response.search_results:
        obj = search_result.object
        for metric_id in metric_ids:
            metric_query = metric_id + "{" + obj.object_type_id + "=\"" + obj.object_id + "\"}"
                
            values = time_range_values (hostname = target_hostname, port = target_port, query_string = metric_query, 
                start_time = start_time, end_time = end_time, step = step, top = False)
   
            data_points = list (map (lambda m: DataPoint (timestamp = m[0], value = m[1]), values))
            mv = MetricValue (metric_id = metric_id, statistic_id = statistic_id, data_points = data_points, summary_rule = suggested_summary_rule)
            data_response = DataResponse (data_request_id = request_id, metric_values = [mv, ])

    return data_response
