import panel as pn
import param
import pandas as pd
import numpy as np
import holoviews as hv
from holoviews import streams
from holoviews import opts, dim
hv.extension('bokeh')
pn.extension()


class FlagChecker(param.Parameterized):
    flag = param.ObjectSelector(default="UNCHECKED", objects=[
                                "UNCHECKED", "CHECKED", "BAD"])
    undo_level = param.Integer(0, precedence=-1)

    def __init__(self, df, df_ref, **kwargs):
        super().__init__(**kwargs)  # param.Parameterized requires calling their super first
        self.init(df, df_ref)

    def init(self, df, df_ref):
        self.x_col_name = 'x'
        self.y_col_name = 'y'
        self.flag_col_name = 'user_flag'
        self.flag_map = {'CHECKED': 0, 'BAD': 1, 'UNCHECKED': -1}
        self.flag2markers = dict(zip([-1, 0, 1], ['triangle', 'circle', 'x']))
        self.flag2colors = dict(zip([-1, 0, 1], ['blue', 'green', 'red']))
        self.do_list = []  # do list builds when new stuff is marked
        self.redo_list = []  # only builds when undo is executed and reset when new stuff is marked
        self.df = df
        self.df_ref = df_ref
        self.value_col_index = df.columns.get_loc(self.y_col_name)
        self.user_col_index = df.columns.get_loc(self.flag_col_name)
        self.df_flagged = self.df.copy()  # copy on which flags are set
        # copy with flags setting col 2 values for NA or BAD values
        self.dfg = self.df_flagged.copy()
        self._update_dfg_vals()
        self.points = hv.Points(self.df_flagged, kdims=[
                                self.x_col_name, self.y_col_name]).opts(alpha=0)
        # Declare points as source of selection stream
        selection = streams.Selection1D(source=self.points)
        self.dmap = hv.DynamicMap(self.mark_flag, streams=[selection])

    @param.depends('flag', 'undo_level')
    def view(self):
        curves = hv.Curve(self.df_ref) * self.points * self.dmap
        return curves.opts(width=700, height=400, title='Ready to mark selections: ' + self.flag)

    def create_undo_redo_buttons(self):
        backward = pn.widgets.Button(name='\u25c0', width=50)
        backward.on_click(self.undo_mark)
        forward = pn.widgets.Button(name='\u25b6', width=50)
        forward.on_click(self.redo_mark)
        return pn.Row(backward, forward)

    def _update_dfg_vals(self):
        self.dfg.iloc[:, self.value_col_index] = self.df_flagged.iloc[:,
                                                                      self.value_col_index]
        self.dfg.loc[self.df_flagged[self.flag_col_name] > 0, self.y_col_name] = np.nan

    def do_mark(self, mark_data):
        self.do_list.append(mark_data)
        if len(self.redo_list) > 0:  # clear out redos if marking again
            self.redo_list = []
            self.undo_level = 0

    def undo_mark(self, event=None):
        if len(self.do_list) == 0:
            return
        mark_data = self.do_list.pop()
        self.redo_list.append(mark_data)
        df_flag_selected = mark_data[0]
        self.df_flagged.loc[df_flag_selected.index, [
            self.flag_col_name]] = df_flag_selected[self.flag_col_name]
        self._update_dfg_vals()
        self.undo_level += 1

    def redo_mark(self, event=None):
        if len(self.redo_list) == 0:
            return
        mark_data = self.redo_list.pop()
        self.do_list.append(mark_data)
        df_flag_selected = mark_data[0]
        flag = mark_data[1]
        self.df_flagged.loc[df_flag_selected.index, [
            self.flag_col_name]] = self.flag_map[flag]
        self._update_dfg_vals()
        self.undo_level -= 1

    def mark_flag(self, index):
        selected = self.points.iloc[index]
        if len(index) > 0:
            self.do_mark(
                (self.df_flagged.loc[selected.data.index, [self.flag_col_name]], self.flag))
            self.df_flagged.loc[selected.data.index, [
                self.flag_col_name]] = self.flag_map[self.flag]
        self._update_dfg_vals()
        crv_layout = hv.Curve(
            self.dfg, kdims=[self.x_col_name]).opts(color='blue')
        pts_layout = hv.Points(self.df_flagged, kdims=[self.x_col_name, self.y_col_name])\
            .opts(marker=dim(self.flag_col_name).categorize(self.flag2markers),
                  color=dim(self.flag_col_name).categorize(self.flag2colors),
                  size=5)
        return crv_layout * pts_layout
