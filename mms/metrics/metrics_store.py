# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#     http://www.apache.org/licenses/LICENSE-2.0
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""
Metrics collection module
"""
from mms.metrics.metric import Metric
from mms.metrics.dimension import Dimension


class MetricsStore(object):
    """
    Class for creating, modifying different metrics. And keep them in a dictionary
    """

    def __init__(self, request_ids, model_name):
        """
        Initialize metrics map,model name and request map
        """
        self.store = list()
        self.request_ids = request_ids
        self.model_name = model_name
        self.cache = {}

    def _add_or_update(self, name, value, req_id, unit, metrics_method=None, dimensions=None):
        """
        Add a metric key value pair

        Parameters
        ----------
        name : str
            metric name
        value: int, float
            value of metric
        req_id: str
            request id
        unit: str
            unit of metric
        value: int, float , str
            value of metric
        metrics_method: str, optional
            indicates type of metric operation if it is defined
        """
        # IF req_id is none error Metric
        if dimensions is None:
            dimensions = list()
        elif not isinstance(dimensions, list):
            raise ValueError("Please provide a list of dimensions")
        if req_id is not None:
            dimensions.append(Dimension("ModelName", self.model_name))
            dimensions.append(Dimension("Level", "Model"))
        if req_id is None:
            dimensions.append(Dimension("Level", "Error"))
        # Cache the metric with an unique key for update
        dim_str = [name, unit, str(req_id)] + [str(d) for d in dimensions]
        dim_str = '-'.join(dim_str)
        if dim_str not in self.cache:
            metric = Metric(name, value, unit, dimensions, req_id, metrics_method)
            self.store.append(metric)
            self.cache[dim_str] = metric
        else:
            self.cache[dim_str].update(value)

    def _get_req(self, idx):
        """
        Provide the request id dimension

        Parameters
        ----------

        idx : int
            request_id index in batch
        """
        # check if request id for the metric is given, if so use it else have a list of all.
        req_id = self.request_ids
        if isinstance(req_id, dict):
            req_id = ','.join(self.request_ids.values())
        if idx is not None and self.request_ids is not None and idx in self.request_ids:
            req_id = self.request_ids[idx]
        return req_id

    def add_counter(self, name, value, idx=None, dimensions=None):
        """
        Add a counter metric or increment an existing counter metric

        Parameters
        ----------
        name : str
            metric name
        value: int
            value of metric
        idx: int
            request_id index in batch
        dimensions: list
            list of dimensions for the metric
        """
        unit = 'count'
        req_id = self._get_req(idx)
        self._add_or_update(name, value, req_id, unit, 'counter', dimensions)

    def add_time(self, name, value, idx=None, unit='ms', dimensions=None):
        """
        Add a time based metric like latency, default unit is 'ms'

        Parameters
        ----------
        name : str
            metric name
        value: int
            value of metric
        idx: int
            request_id index in batch
        unit: str
            unit of metric,  default here is ms, s is also accepted
        """
        if unit not in ['ms', 's']:
            raise ValueError("the unit for a timed metric should be one of ['ms', 's']")
        req_id = self._get_req(idx)
        self._add_or_update(name, value, req_id, unit, dimensions)

    def add_size(self, name, value, idx=None, unit='MB', dimensions=None):
        """
        Add a size based metric

        Parameters
        ----------
        name : str
            metric name
        value: int, float
            value of metric
        idx: int
            request_id index in batch
        unit: str
            unit of metric, default here is 'MB', 'kB', 'GB' also supported
        """
        if unit not in ['MB', 'kB', 'GB']:
            raise ValueError("The unit for size based metric is one of ['MB','kB', 'GB']")
        req_id = self._get_req(idx)
        self._add_or_update(name, value, req_id, unit, dimensions)

    def add_percent(self, name, value, idx=None, dimensions=None):
        """
        Add a percentage based metric

        Parameters
        ----------
        name : str
            metric name
        value: int, float
            value of metric
        idx: int
            request_id index in batch
        """
        unit = 'percent'
        req_id = self._get_req(idx)
        self._add_or_update(name, value, req_id, unit, dimensions)

    def add_error(self, name, value, dimensions=None):
        """
        Add a Error Metric
        Parameters
        ----------
        name : str
            metric name
        value: str
            value of metric, in this case a str
        """
        unit = ''
        self._add_or_update(name, value, None, unit, dimensions)

    def add_metric(self, name, value, idx=None, unit=None, dimensions=None):
        """
        Add a metric which is generic with custom metrics

        Parameters
        ----------
        name : str
            metric name
        value: int, float
            value of metric
        idx: int
            request_id index in batch
        unit: str
            unit of metric
        """
        req_id = self._get_req(idx)
        self._add_or_update(name, value, req_id, unit, dimensions)