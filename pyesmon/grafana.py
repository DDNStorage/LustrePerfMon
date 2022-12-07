# Copyright (c) 2017 DataDirect Networks, Inc.
# All Rights Reserved.
# Author: lixi@ddn.com
"""
Library for generating Grafana dashboard Json
Reference:
https://github.com/grafana/grafana/blob/master/docs/sources/reference/dashboard.md
http://docs.grafana.org/reference/dashboard/
"""
import json


class GrafanaTimePicker():
    """
    Each Grafana Timepicker has an object of this type
    """
    # pylint: disable=too-few-public-methods,too-many-instance-attributes
    def __init__(self):
        # whether timepicker is collapsed or not
        self.gtp_collapse = False
        # whether timepicker is enabled or not
        self.gtp_enable = True
        self.gtp_notice = False
        self.gtp_now = True
        self.gtp_refresh_intervals = ["1m"]
        self.gtp_status = "Stable"
        self.gtp_time_options = ["5m", "15m", "1h", "3h", "6h", "12h", "24h",
                                 "2d", "3d", "4d", "7d", "30d"]
        self.gtp_type = "timepicker"

    def gtp_json_encoder(self):
        """
        Json encoder
        """
        return {"collapse": self.gtp_collapse,
                "enable": self.gtp_enable,
                "notice": self.gtp_notice,
                "now": self.gtp_now,
                "refresh_intervals": self.gtp_refresh_intervals,
                "status": self.gtp_status,
                "time_options": self.gtp_time_options,
                "type": self.gtp_type}


class GrafanaTemplating():
    """
    Each Grafana Templating has an object of this type
    """
    # pylint: disable=too-few-public-methods
    def __init__(self):
        # whether templating is enabled or not
        self.gt_enable = False
        # an array of objects representing, each representing one template variable
        self.gt_list = []

    def gt_json_encoder(self):
        """
        Json encoder
        """
        return {"enable": self.gt_enable,
                "list": self.gt_list}


class GrafanaAnnotations():
    """
    Each Grafana Annotations has an object of this type
    """
    # pylint: disable=too-few-public-methods
    def __init__(self):
        # whether annotations is enabled or not
        self.ga_enable = False
        self.ga_list = []

    def ga_json_encoder(self):
        """
        Json encoder
        """
        return {"enable": self.ga_enable,
                "list": self.ga_list}


class GrafanaTime():
    """
    Each Grafana Time has an object of this type
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, from_time, to_time):
        self.gt_from = from_time
        self.gt_to = to_time

    def gt_json_encoder(self):
        """
        Json encoder
        """
        return {"from": self.gt_from,
                "to": self.gt_to}


class GrafanaRow():
    """
    Each Grafana Row has an object of this type
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, title):
        # whether row is collapsed or not
        self.gr_collapse = False
        # whether a row is editable or not
        self.gr_editable = True
        # height of the row in pixels
        self.gr_height = "200px"
        # panels metadata, see panels section for details
        self.gr_panels = []
        # title of row
        self.gr_title = title

    def gr_json_encoder(self):
        """
        Json encoder
        """
        return {"collapse": self.gr_collapse,
                "editable": self.gr_editable,
                "height": self.gr_height,
                "panels": self.gr_panels,
                "title": self.gr_title}


class GrafanaDashboard():
    """
    Each Grafana Dashboard has an object of this type
    # Use example:
    # Generate cluster status dashboard
    name = "Cluster Status"
    dashboard_obj = grafana.GrafanaDashboard(name)
    row_index = 1
    row_title = "Server Row %d" % row_index
    row_obj = grafana.GrafanaRow(row_title)
    dashboard_obj.gd_rows.append(row_obj)

    dashboard_string = json.dumps(dashboard_obj, cls=grafana.GrafanaEncoder,
                                  indent=4, separators=(',', ': '))
    dashboard = json.loads(dashboard_string)
    logging.debug("dashboard of [%s]: %s", name, dashboard_string)
    ret = self.es_grafana_dashboard_replace(name, dashboard)
    if ret:
        logging.error("failed to replace dashboard [%s]: %s", name,
                      dashboard_string)
        return ret
    """
    # pylint: disable=too-many-instance-attributes,too-few-public-methods
    def __init__(self, title):
        # unique dashboard id, an integer
        self.gd_id = None
        # current title of dashboard
        self.gd_title = title
        # tags associated with dashboard, an array of strings
        self.gd_tags = []
        # theme of dashboard, i.e. dark or light
        self.gd_style = "dark"
        # timezone of dashboard, i.e. utc or browser
        self.gd_timzone = "browser"
        # whether a dashboard is editable or not
        self.gd_editable = True
        # whether row controls on the left in green are hidden or not
        self.gd_hide_controls = False
        # 0 for no shared crosshair or tooltip (default), 1 for shared
        # crosshair, 2 for shared crosshair AND shared tooltip
        self.gd_graph_tooltip = 1
        # row metadata, see GrafanaRow for details
        self.gd_rows = []
        # time range for dashboard, i.e. last 6 hours, last 7 days, etc
        self.gd_time = GrafanaTime("now-1h", "now")
        # timepicker metadata, see GrafanaTimePicker for details
        self.gd_timpicker = GrafanaTimePicker()
        # templating metadata, see GrafanaTemplating for details
        self.gd_templating = GrafanaTemplating()
        # annotations metadata, see GrafanaAnnotations for details
        self.gd_annotations = GrafanaAnnotations()
        self.gd_schema_version = 14
        self.gd_version = 0
        self.gd_links = []

    def gd_json_encoder(self):
        """
        Json encoder
        """
        return {"id": self.gd_id,
                "title": self.gd_title,
                "tags": self.gd_tags,
                "style": self.gd_style,
                "timzone": self.gd_timzone,
                "editable": self.gd_editable,
                "hideControls": self.gd_hide_controls,
                "graphTooltip": self.gd_graph_tooltip,
                "rows": self.gd_rows,
                "time": self.gd_time,
                "timepicker": self.gd_timpicker,
                "annotations": self.gd_annotations,
                "schemaVersion": self.gd_schema_version,
                "version": self.gd_version,
                "links": self.gd_links}


class GrafanaEncoder(json.JSONEncoder):
    """
    Encoder for class GrafanaDashboard
    """
    # pylint: disable=method-hidden,too-many-return-statements
    def default(self, obj):
        """
        Overwrite the encoder of Json
        """
        if isinstance(obj, GrafanaDashboard):
            return obj.gd_json_encoder()
        elif isinstance(obj, GrafanaTime):
            return obj.gt_json_encoder()
        elif isinstance(obj, GrafanaTimePicker):
            return obj.gtp_json_encoder()
        elif isinstance(obj, GrafanaTemplating):
            return obj.gt_json_encoder()
        elif isinstance(obj, GrafanaAnnotations):
            return obj.ga_json_encoder()
        elif isinstance(obj, GrafanaRow):
            return obj.gr_json_encoder()
        return json.JSONEncoder.default(self, obj)
