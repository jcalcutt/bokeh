"""This is the Bokeh charts interface. It gives you a high level API to build
complex plot is a simple way.

This is the HeatMap class which lets you build your HeatMap charts just passing
the arguments to the Chart class and calling the proper functions.
"""
#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2014, Continuum Analytics, Inc. All rights reserved.
#
# Powered by the Bokeh Development Team.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function, division

from .._builder import Builder, create_and_build
from .._data_adapter import DataAdapter
from ...models import ColumnDataSource, FactorRange, GlyphRenderer, HoverTool
from ...models.glyphs import Rect

#-----------------------------------------------------------------------------
# Classes and functions
#-----------------------------------------------------------------------------


def HeatMap(values, xscale="categorical", yscale="categorical",
            xgrid=False, ygrid=False, **kw):
    chart = create_and_build(
        HeatMapBuilder, values, xscale=xscale, yscale=yscale,
        xgrid=xgrid, ygrid=ygrid, **kw
    )
    chart.add_tools(HoverTool(tooltips=[("value", "@rate")]))
    return chart

class HeatMapBuilder(Builder):
    """This is the HeatMap class and it is in charge of plotting
    HeatMap chart in an easy and intuitive way.

    Essentially, it provides a way to ingest the data, make the proper
    calculations and push the references into a source object.
    We additionally make calculations for the ranges.
    And finally add the needed glyphs (rects) taking the references
    from the source.

    Examples:
    from collections import OrderedDict
    from bokeh.charts import HeatMap

    xyvalues = OrderedDict()
    xyvalues['apples'] = [4,5,8]
    xyvalues['bananas'] = [1,2,4]
    xyvalues['pears'] = [6,5,4]
    hm = HeatMap(xyvalues, title="categorical heatmap", filename="cat_heatmap.html")
    hm.show()
    """

    def get_data(self):
        """Take the CategoricalHeatMap data from the input **value.

        It calculates the chart properties accordingly. Then build a dict
        containing references to all the calculated points to be used by
        the rect glyph inside the ``draw`` method.

        """
        self._catsx = list(self._values.columns)
        self._catsy = list(self._values.index)

        # Set up the data for plotting. We will need to have values for every
        # pair of year/month names. Map the rate to a color.
        catx = []
        caty = []
        color = []
        rate = []
        for y in self._catsy:
            for m in self._catsx:
                catx.append(m)
                caty.append(y)
                rate.append(self._values[m][y])

        # Now that we have the min and max rates
        factor = len(self._palette) - 1
        den = max(rate) - min(rate)
        for y in self._catsy:
            for m in self._catsx:
                c = int(round(factor*(self._values[m][y] - min(rate)) / den))
                color.append(self._palette[c])

        width = [0.95] * len(catx)
        height = [0.95] * len(catx)

        self._data = dict(catx=catx, caty=caty, color=color, rate=rate,
                         width=width, height=height)

    def get_source(self):
        """Push the CategoricalHeatMap data into the ColumnDataSource
        and calculate the proper ranges.
        """
        self._source = ColumnDataSource(self._data)
        self.x_range = FactorRange(factors=self._catsx)
        self.y_range = FactorRange(factors=self._catsy)

    def draw(self):
        """Use the rect glyphs to display the categorical heatmap.

        Takes reference points from data loaded at the ColumnDataSurce.
        """
        glyph = Rect(
            x="catx", y="caty",
            width="width", height="height",
            fill_color="color", fill_alpha=0.7,
            line_color="white"
        )
        renderer = GlyphRenderer(data_source=self._source, glyph=glyph)
        # TODO: Legend??
        yield renderer

    def prepare_values(self):
        """Prepare the input data.

        Converts data input (self._values) to a DataAdapter
        """
        self._values = DataAdapter(self._values, force_alias=True)