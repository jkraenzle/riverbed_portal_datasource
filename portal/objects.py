"""
    Portal's REST API has a defined set of "Models" that are used in GET and POST operations,
    typically in JSON format.
    This file creates Python classes, and their associated attributes, that map to each Model.
    The attributes are defined as dictionaries, or lists of dictionaries, as each Model is
    defined as a set of key/value pairs.
"""

import types

class BaseObject (object):
    """
        Base class for Portal objects
    """

    # Set up a standard function that will return the specific Model dictionary that matches to the Portal JSON 
    @property
    def attributes (self):
	# attrs = dictionary to return
        attrs = {}
	
	# loop through key/value pairs in the Class
        for key, val in vars (self).items():
            # if the value is a list, append each item to a list to be assigned to the key
            if isinstance (val, list):
                l = []
                for o in val:
                    # if the value is its own dictionary, recursively call the function
                    if hasattr (o, "attributes"):
                        l.append (o.attributes)
                    else:
                        l.append (o)
                attrs[key] = l
            else:
                attrs[key] = val
        return attrs

    # Python functions for better reporting of class names, attributes, and values while debugging
    # __str__ is called when printing the individual object
    # __repr__ is called when printing a set of objects contained in a list
    def __str__ (self):
        output = ""
        class_name = str(self.__class__).split(".")[-1].replace("'>","")
        for attribute, value in self.attributes.items():
            output += "%s - %s:%s\n" % (class_name, attribute, str(value))
        return output

    def __repr__ (self):
        return self.__str__()


class Granularity (BaseObject):
    """
        A data source can specify one or more granularity levels. If more than one
        granularity is defined, larger granularities must be defined with larger
        time windows than smaller granularities.

        granularity_id*	string
            A unique identifier representing the granularity level.

        value_seconds*	integer($int32)
            The granularity value in seconds. For example, data points representing an
            hour of data would have a 3600 second granularity.

        time_window_seconds*	number($double)
            The maximum window of time for which the granularity level should be used.
            This value is used to limit the amount of data requested for large time
            ranges. Smaller granularities should be shown for smaller time ranges and
            larger ones should be displayed for larger time ranges. For example, a
            value of 3600 would mean that this granularity should only be displayed
            for time ranges of less than one hour.

        display_name*	string
            Determines how this granularity appears to users.

        storage_duration*	integer($int32)
            The amount of time that data of this granularity is available. A value of 0
            means this data is kept forever. A value of 86400 would indicate that data
            of this granularity is only available for one day from the present time.

        description	string
            A text description of the granularity.

        is_global	boolean
            Does this granularity apply to all statistics? Note that for a non-global
            granularity to be utilized it must be included in the list of granularities
            that are defined in a Statistic definition. This list is used to add
            granularities that are not global to the statistic.
    """

    def __init__ (self, granularity_id, value_seconds, time_window_seconds,
                 display_name, storage_duration, description="", is_global=True):

        self.granularity_id = granularity_id
        self.value_seconds = value_seconds
        self.time_window_seconds = time_window_seconds
        self.display_name = display_name
        self.storage_duration = storage_duration
        self.description = description
        self.is_global = is_global


class Metric (BaseObject):
    """
        A metric is an entity that pairs with one or more object types. Internally,
        Portal combines objects and metrics to create dashboard elements. A user
        primarily interacts with dashboard elements when viewing dashboards.

        metric_id*	string
            A unique identifier representing the metric (e.g. cpu_usage, disk_usage).

        unique_display_name*	string
            A unique user-facing display name for this metric. Display names must be
            specified as all metrics for a data source can appear side-by-side in the
            thresholds and object property screens.

        suggested_aggregation_rule
            Enum representing the options for the suggested rule to be used when
            summarizing or aggregating time series data for this metric into a single
            value

        unit*  string
            The metric's unit (e.g. MB, MB/s, %, etc).  This unit is displayed to
            Portal users.

        suggested_color	string
            A string representing a hex value in the format 0xRRBBGG or

        stacked_area_weight	integer($int32)
            An integer indicating in what order the metric should be placed
            if aggregated into a stacked area chart. The lower the number,
            the higher in the stack the metric will appear.

        applicable_statistic_ids
            A list of statistic ids not marked as global that apply to this metric.
            string

        inapplicable_statistic_ids
            A list of global statistic ids that should not apply to this metric.
            string

        provided_summary_rules
            A list of the summary rules that the data source can calculate for this metric.
            If Portal needs to summarize or aggregate time series data according to one of
            these rules, it will ask the data source to perform the calculation.
    """
    def __init__ (self, metric_id, unique_display_name, unit,
                 suggested_aggregation_rule = None, suggested_color = None,
                 stacked_area_weight = None, applicable_statistic_ids = None,
                 inapplicable_statistic_ids = None, provided_summary_rules = None):
        self.metric_id = metric_id
        self.unique_display_name = unique_display_name
        self.unit = unit
        self.suggested_aggregation_rule = suggested_aggregation_rule
        self.suggested_color = suggested_color
        self.stacked_area_weight = stacked_area_weight
        self.applicable_statistic_ids = [] if applicable_statistic_ids is None else applicable_statistic_ids
        self.inapplicable_statistic_ids = [] if inapplicable_statistic_ids is None else inapplicable_statistic_ids
        self.provided_summary_rules = [] if provided_summary_rules is None else provided_summary_rules


class ObjectType (BaseObject):
    """
        Object types are entities that have a collection of unique metrics associated with them.

        id*	string
            A unique identifier representing the object type.

        display_name*	string
            The display string for the object type.

        plural_display_name*	string
            A string to display for plural instances of the object type.

        root_type*	boolean
            True if object type has no parents and false otherwise.

        enumerable*	boolean
            True if all objects of this type are enumerable.

        applicable_metrics*
            The ids of the metrics that are applicable to the object type string

        scopable_object_types
            A list of the definitions of object type relationships that should
            appear below this object type in the object hierarchy.

        has_free_text_search	boolean
            Should instances of this type be searchable in free text fields?

        has_data_source_provided_type_ahead	boolean
            default: false
            Should instances of this type be queryable via the type ahead endpoint?             

        has_ip_address_property	boolean
            Do instances of this type have an IP address associated with them?

        pre_cache_instances	boolean
            Should instances of this type be pre-cached so as to be immediately
            searchable?

        include_parent_type_metrics	boolean
            Are metrics that are applicable to parent object types also applicable
            to this object type?

        cache_duration	integer($int32)
            How long should instances of this type be cached?

        parent_type_metrics_intersection	boolean
            Should metrics only be included if all of the parent object types also
            include the metric?

        limit_instances_configuration   LimitInstancesConfiguration
    """
    def __init__ (self, id, display_name, root_type, enumerable, applicable_metrics = None,
                 scopable_object_types = None, has_free_text_search = True,
                 has_data_source_provided_type_ahead = False,
                 has_ip_address_property = False, pre_cache_instances = True,
                 include_parent_type_metrics = False, cache_duration = 7200,
                 plural_display_name = None, parent_type_metrics_intersection = False,
                 limit_instances_configuration = None):

        self.id = id
        self.display_name = display_name
        self.root_type = root_type
        self.enumerable = enumerable
        self.applicable_metrics = [] if applicable_metrics is None else applicable_metrics
        self.scopable_object_types = [] if scopable_object_types is None else scopable_object_types
        self.has_free_text_search = has_free_text_search
        self.has_ip_address_property = has_ip_address_property
        self.pre_cache_instances = pre_cache_instances
        self.include_parent_type_metrics = include_parent_type_metrics
        self.cache_duration = cache_duration
        self.parent_type_metrics_intersection = parent_type_metrics_intersection

        if plural_display_name is None:
            self.plural_display_name = self.display_name
        else:
            self.plural_display_name = plural_display_name

###
class ScopableObjectTypes(BaseObject):
    def __init__(self):
        pass

class LimitInstancesConfiguration(BaseObject):
    """
        nValue*	integer($int32)
            How many results should be requested?
        metric_id	string
            A unique identifier representing the metric that the top N search should use.
    """

    def __init__(self, nValue, metric_id=""):
        self.nValue = nValue
        self.metric_id = metric_id

class ObjectDefinition(BaseObject):
    """
        An individual search result.

    object_id*	string
        The unique id of the object.

    display_name*	string
        The display name of the object.

    object_type_id*	string
        The id of the object's object type

    object_properties
        A list of portal_object_property
    """

    def __init__ (self, object_id, display_name, object_type_id, object_properties = None):
        self.object_id = object_id
        self.display_name = display_name
        self.object_type_id = object_type_id
        self.object_properties = [] if object_properties is None else object_properties


class ObjectPropertyDefinition (BaseObject):
    """
        The definition of an object property.

        id*	string
            The id of the object property.

        display_name*	string
            The display name of the object property.

        hidden	boolean
            Is this property visible to the user?

        url_pass_through	boolean
            Should the property value be escaped when using it for variable substitution?
    """

    def __init__ (self, id, display_name, hidden=False,
                 url_pass_through=False):
        self.id = id
        self.display_name = display_name
        self.hidden = hidden
        self.url_pass_through = url_pass_through


class ObjectProperty (BaseObject):
    """
        A property of an object that can be used for grouping.

        id*	string
            The id of the object property.

        value*	string
            The value of the property.
    """
    def __init__ (self, id, value):
        self.id = id
        self.value = value


class SearchResult (BaseObject):
    """
        An individual search result.

        object*	PortalObjectDefinition

        value	number($double)
            The value of the metric that is being topped by if this is a
            result for a top N search.

        parent_object_filters
            The object filters to specify the parent of the object in the
            case of a * * search.
    """
    def __init__ (self, obj, value = None, parent_object_filters = None):
        self.object = obj
        self.value = value
        self.parent_object_filters = [] if parent_object_filters is None else parent_object_filters
    
    def __lt__ (self, other):
        return self.value < other.value

class ScopableType (BaseObject):
    """
        The definition for a relationship between two object types
        this type and a parent type.

        object_type_id*	string
            The id of the child type to which the parent type is scoped

        all_instances*	boolean
            Whether or not all instances of this type are applicable to
            instances of the parent type

        filter_object_instances	boolean
            Whether the instances of this type displayed in the object selection
            wizard should be filtered to only include those that are applicable
            to the parent type.

        top_n_wildcarding	boolean
            Whether or not the top N functionality will allow wildcarding for this
            type. The default value is false but this is is not useful in most cases.

    """
    def __init__ (self, object_type_id, all_instances,
                 filter_object_instances = True, top_n_wildcarding = False):
        self.object_type_id = object_type_id
        self.all_instances = all_instances
        self.filter_object_instances = filter_object_instances
        self.top_n_wildcarding = top_n_wildcarding

class DataPoint (BaseObject):
    """
        An individual time series data point.

        timestamp*	integer($int64)
            The UTC +0 timestamp of the data point.

        value*	number($double)
            The value of the data point. Return NaN if there is not a valid
            data point at this time.

        weight_value	number($double)
            The weight value that should be associated with this data point
            when calculating average values.
    """
    def __init__ (self, timestamp, value, weight_value = 1.0):
        self.timestamp = timestamp
        self.value = value
        self.weight_value = weight_value


class MetricValue (BaseObject):
    """
        A set of time series data for an individual metric.

        metric_id*	string
            The id of the metric.

        statistic_id*	string
            The id of the statistic.

        summary_rule	PortalSummaryRule
            Enum representing the options for the suggested rule to be used
            when summarizing or aggregating time series data for this metric
            into a single value

        data_points	[
            The data points for the metric/statistic pair.
            Data_Point{...}
        ]

        last_valid_timestamp	integer($int64)
            A value to be passed and used as DCLDataFragment.setLastValidTimestamp().
            This can be used to control how the data in this response is cached by
            the proxy.
    """
    def __init__ (self, metric_id, statistic_id, data_points,
                 summary_rule = None, last_valid_timestamp = None):
        self.metric_id = metric_id
        self.statistic_id = statistic_id
        self.data_points = data_points
        self.summary_rule = summary_rule
        self.last_valid_timestamp = last_valid_timestamp


class DataResponse (BaseObject):
    """
    The response to a request for data.

    data_request_id*	integer($int64)
        The unique id of this data request. This value should be echoed back to
        the client in the data response so that the request and response match up.

    metric_values
        An array of the metric values in for the request.
    """
    def __init__ (self, data_request_id, metric_values):
        self.data_request_id = data_request_id
        self.metric_values = metric_values


class SearchResponse (BaseObject):
    """
        A response to a search.

        search_results
            A list of PortalSearchResult

        valid_interval	number($double)
            The amount of time for which these search results are valid. Portal
            may cache these results for this duration. If not specified a
            value of 300 is used.
        
        search_error_string	string
            An error message explaining the reason for a search failure.            
    """
    def __init__ (self, search_results = None, valid_interval = 300, search_error_string = None):
        self.search_results = [] if search_results is None else search_results
        self.valid_interval = valid_interval
        self.search_error_string = search_error_string

    def add_search_result (self, sr):
        self.search_results.append(sr)


class Statistic (BaseObject):
    """
        A data source can specify one of more different statistics for a metric.
        A statistic defines how data has been calculated for a metric. Every data
        source should have at least one statistic, but may have more. Examples of
        statistics would be a maximum rollup, or a typical value, or a
        high critical threshold.

        id*	string
            A unique identifier for the statistic.

        display_name	string
            The display name of the statistic.

        is_global	boolean
            Does this statistic apply to all metrics? Note that for a non-global statistic
            to be utilized it must be included in the list of statistics that are defined
            in a Metric definition. This list is used to add statistics that are not global
            to the metric.

        is_default	boolean
            Is this the default statistic that should be used? If the statistic is a status
            statistic, indicates that this is the default status statistic. If the statistic
            is a roll-up statistic, indicates that it is the default roll-up statistic.

        is_rollup	boolean
            Does this statistic represent rollup data? Should this be presented as an option
            to the user when selecting large time ranges?

        is_primary	boolean
            Does this statistic represent the primary "raw" data for the data source?
            There should generally only be one primary statistic.

        is_non_periodic	boolean
            Is the statistic only updated when changes occur, rather than being updated at
            a regular (ie, periodic) interval?

        is_status_data	boolean
            Should this data be interpreted as status information?

        granularity_ids	[
            The granularities that are applicable to the statistic. If no granularities are
            specified, all of the granularities will be applicable to this statistic.
            ]

        data_points_time_aligned	boolean
            Are the data points in this statistic time aligned to the granularity?

        suggested_aggregation_rule	PortalSuggestedSummaryRule
            Enum representing the options for the suggested rule to be used when summarizing
            or aggregating time series data for this metric into a single value

        data_tags	[
            Tags that indicate what type of data this statistic represents. These tags are
            used by Portal to perform built-in operations with this data. For example, a
            statistic tagged with "typical" would be used to render the typical line for
            a river graph.
            string
            Enum:
                Array[6]
                0:"upper_critical"
                1:"upper_warning"
                2:"typical"
                3:"lower_warning"
                4:"lower_critical"
                5:"status"
    """
    def __init__ (self, id, display_name, is_global = True, is_default = False,
                 is_rollup = False, is_primary = False, is_non_periodic = False,
                 is_status_data = False, granularity_ids = None,
                 data_points_time_aligned = True, suggested_aggregation_rule = None,
                 data_tags = None):
        self.id = id
        self.display_name = display_name
        self.is_global = is_global
        self.is_default = is_default
        self.is_rollup = is_rollup
        self.is_primary = is_primary
        self.is_non_periodic = is_non_periodic
        self.is_status_data = is_status_data
        self.granularity_ids = [] if granularity_ids is None else granularity_ids
        self.data_points_time_aligned = data_points_time_aligned
        self.suggested_aggregation_rule = suggested_aggregation_rule
        self.data_tags = [] if data_tags is None else data_tags


class SuggestedSummaryRule (BaseObject):
    """
        Enum representing the options for the suggested rule to be used when
        summarizing or aggregating time series data for this metric into a
        single value

        rule string
        Enum:
            Array[5]
            0:"sum"
            1:"max"
            2:"min"
            3:"avg"
            4:"last_value"
    """
    def __init__ (self, rule):
        self.rule = rule


class Preferences (BaseObject):
    """
    The various options that can be configured by the data source

    update_object_cache_on_initial_sync:
        If true, Portal will trigger a call to update the object cache during the
        initial sync of the object model. This update will use the time range specified
        by the update_object_cache_request_duration_seconds setting.

    object_cache_update_duration_seconds:
        The interval (in seconds) at which a timer triggers an update of the object cache.
        By default, Portal will send requests for new objects every 2 hours, using the time
        range specified by the update_object_cache_request_duration_seconds setting.

    initial_object_cache_request_duration_seconds:
        The duration (in seconds) to use for the initial call to sync the object model.
        The default is 4 weeks.

    update_object_cache_request_duration_seconds:
        The duration (in seconds) to use for updating the object model cache.
        The default is 1 day.

    data_request_batch_limit:
        The limit for how many objects can be requested in a single batch.

    data_request_max_thread_count:
        The maximum number data requests to the data source that Portal can have
        outstanding at a time.

    heartbeat_request_interval_seconds:
        The interval (in seconds) at which Portal will send a version request to the
        data source to verify that the data source is still running. If the version
        request fails two consecutive times, the data source will be marked as
        disconnected. Once it is disconnected, Portal will retry the version request
        at this same interval to determine when the data source is running again.

    utc_offset:
        The offset (in seconds) of this data source from UTC. For example, a data source
        that is UTC +4 would advertise an offset of 14400. A data source that is UTC -1
        would advertise an offset of -3600.

    management_web_url:
        The url used to launch the data source's native web page from the Portal home
        page in a new tab/browser. If not set, Portal will automatically compose a
        management web url.

    supports_object_specific_launches:
    	boolean
        default: false
        Does the data source support object specific launches? If this value is true, 
        each time the user right clicks on an object, a request will be made to the data 
        source to learn about any launches that are specific to this object.

    always_request_recent_data:
        boolean
        default: false
        Does the recent data from the data source sometimes change? In other words, when a 
        data point is advertised to Portal, could it’s value change at a later time? If this 
        is the case set this value to true. This can be used in conjunction with 
        last_valid_timestamp to allow data to be re-requested.    

    create_scoped_objects	boolean
        default: true
        Should portal create scoped objects when performing searches? For example for a set of filters 
        like group:Bethesda,Device:lab-router, should portal create an object 
        like Bethesda > lab-router (true) or lab-router(false)

    supports_type_ahead_searches	boolean
        default: false
        Does the data source support data source side type ahead searches? If this value is true, 
        strings the user types into the search bar will be sent to the data source via the type_ahead_search endpoint        

    """
    def __init__ (self, update_object_cache_on_initial_sync = True,
                 object_cache_update_duration_seconds = 7200,
                 initial_object_cache_request_duration_seconds = 2419200,
                 update_object_cache_request_duration_seconds = 86400,
                 data_request_batch_limit = 250,
                 data_request_max_thread_count = 8,
                 heartbeat_request_interval_seconds = 15,
                 utc_offset = None,
                 management_web_url = "", supports_object_specific_launches = False,
                 always_request_recent_data = False,
                 create_scoped_objects = True,
                 supports_type_ahead_searches = False):

        self.update_object_cache_on_initial_sync = update_object_cache_on_initial_sync
        self.object_cache_update_duration_seconds = object_cache_update_duration_seconds
        self.initial_object_cache_request_duration_seconds = initial_object_cache_request_duration_seconds
        self.update_object_cache_request_duration_seconds = update_object_cache_request_duration_seconds
        self.data_request_batch_limit = data_request_batch_limit
        self.data_request_max_thread_count = data_request_max_thread_count
        self.heartbeat_request_interval_seconds = heartbeat_request_interval_seconds
        self.utc_offset = utc_offset
        self.management_web_url = management_web_url
        self.supports_object_specific_launches = supports_object_specific_launches
        self.always_request_recent_data = always_request_recent_data
        self.create_scoped_objects = create_scoped_objects
        self.supports_type_ahead_searches = supports_type_ahead_searches


class LaunchURL (BaseObject):
    """
        A launch URL defined for a specific object type combination. The URL is applicable
        if the dashboard element contains exactly the object types specified.

        url_string:
            A parameterized URL that will be launchable from dashboard elements that contains
            all the specified objects. For example, if you want to launch to the host groups
            page for any Host Group object, and the launch target is something like
            (for the Boston Host Group) http://mydatasource.riverbed.com/navigator'&host_group=Boston'
            you would configure the parameterized url as follows --
            http://mydatasource.riverbed.com/navigator'&host_group=$$host_group$$'. Your Host Group
            objects would need to have a host_group facet and you would set the valid object id to the
            object type id of a Host Group.

        applies_to_all_scoped_types:
        	boolean
            default: false
            Determines whether the applicable object types are listed individually or if Portal should apply 
            a launch URL for all object types scoped to or from a specified object type. For example, 
            Set applies_to_all_scoped_types to false if only explicitly listed object types in valid_objects 
            are applicable (e.g., specifying “Location” applies the URL only to the Location object type). 
            Set applies_to_all_scoped_types to true if all object types in valid_objects involving a specified 
            object type are applicable 
            (e.g. specifying “Location” applies the URL to Location, Location > Department, 
            Application > Location > Department, etc.). Multiple object types may be included, 
            but applies_to_all_scoped_types is applied unilaterally.
        
        valid_objects:
        [ A list of valid object type id ]

        valid_metrics:
        [ A list of  valid metric id. ]

        id:
            A unique id for this launch URL.

        display_name:
            A display name for this URL (for the launch menu).

        sub_menu:
            The submenu heading under which this launch should be displayed.

        description:
            Description of this URL launch

    """
    def __init__ (self, url_string,  id,
                 display_name, description, sub_menu = None,
                 valid_objects = None, valid_metrics = None, 
                 applies_to_all_scoped_types = False):
        self.url_string = url_string
        self.valid_objects = [] if valid_objects is None else valid_objects
        self.valid_metrics = [] if valid_metrics is None else valid_metrics
        self.id = id
        self.display_name = display_name
        self.sub_menu = sub_menu
        self.description = description
        self.applies_to_all_scoped_types = applies_to_all_scoped_types

class SoftwareVersion (BaseObject):

    def __init__ (self, data_source_type, major_version, minor_version,
                 display_string="", revision_number=0, build_number=0):
        self.data_source_type = data_source_type
        self.major_version = major_version
        self.minor_version = minor_version
        self.display_string = display_string
        self.revision_number = revision_number
        self.build_number = build_number

class ObjectFilter (BaseObject):
    def __init__ (self, object_type_id, instance_id):
        self.object_type_id = object_type_id
        self.instance_id = instance_id

class AlertObject (BaseObject):
    """
        A representation of a Portal Alert object.

        alert_id: integer
            Alert ID from the data source
        
        name: string
            The name of the alert

        start_time_seconds: integer
            The start time in seconds

        description: string
            A short user-friendly description of the alert specific to a data source and the 
            alert’s violations.

        duration_seconds: integer
            The duration in seconds

        value: integer
            The value that triggered the alert

        ongoing: boolean
            Flag indicating whether the alert is ongoing or stopped

        severity: string
            Field indicating how severe this alert is based on the thresholds configured on the data source.
            [ LOW, MEDIUM, HIGH, NONE ]

        additional_infos: [AlertAdditionalInfo, ]
            Additional information about this alert.
    """
    
    def __init__ (self, alert_id, name, start_time_seconds,
                 description, duration_seconds, value,
                 ongoing, severity, additional_info=[]):
        self.alert_id = alert_id
        self.name = name
        self.start_time_seconds = start_time_seconds
        self.description = description
        self.duration_seconds = duration_seconds
        self.value = value
        self.ongoing = ongoing
        self.severity = severity
        self.additional_info = additional_info

class AlertAdditionalInfo (BaseObject):
    """
        An object to define any data source specific additional properties that an alert might have

        name: string
            The name of the property

        type: string
            the type contained in the value object

        value: dictionary
            {description: Specifies a property in the form of a JSON object}
    """
    
    def __init__ (self, name, alert_type, value={}):
        self.name = name
        self.type = alert_type
        self.value = value
