from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure, curdoc
from bokeh.models import Span, CustomJS, Slider, ColumnDataSource, Div, RangeTool, FreehandDrawTool
from bokeh.layouts import layout, column, gridplot
from bokeh.themes import Theme
from bokeh.palettes import Category10
import ipywidgets as widgets
from IPython.display import display
from bokeh.models import DataRange1d
from bokeh.models import Range1d
import numpy as np
output_notebook()


from bokeh.models import FixedTicker, FuncTickFormatter

class InteractivePlot:
    def __init__(self, t, signal):
        self.t = t
        self.signal = signal

        # create a data source to enable refreshing of fill
        self.source = ColumnDataSource(data=dict(x=self.t, y=self.signal))

        # create main scatter plot, as a line (with fill)
        self.p = figure(height=300, width=600, tools="", x_range=(min(self.t), max(self.t)), background_fill_color='black')
        self.p.line('x', 'y', source=self.source, line_color='white')


        # Set x and y tick values
        x_ticks = list(range(0, len(self.t), len(self.t) // 150)) # pick every 10th index for the x-axis
        y_ticks = list(np.linspace(min(self.signal), max(self.signal), 10)) # 10 evenly spaced values for the y-axis
        self.p.xaxis.ticker = FixedTicker(ticks=x_ticks)
        self.p.yaxis.ticker = FixedTicker(ticks=y_ticks)

        # Customize tick labels
        self.p.xaxis.formatter = FuncTickFormatter(code="""
            return Math.floor(tick);
        """)
        self.p.yaxis.formatter = FuncTickFormatter(code="""
            return parseFloat(tick.toFixed(2));
        """)
       

        # theme everything for a cleaner look
        curdoc().theme = Theme(json={
            "attrs": {
                "Plot": { "toolbar_location": None },
                "Grid": { "grid_line_color": None },
                "Axis": {
                    "axis_line_color": None,
                    "major_label_text_color": "black",
                    "major_tick_line_color": "black",
                    "minor_tick_line_color": "black",
                }
            }
        })



    def plot_with_patterns(self, num_patterns):
        sliders = []
        for i in range(num_patterns):
            # create the vertical line
            vline = Span(location=0, dimension='height', line_color=Category10[10][i%10], line_width=2)
            self.p.renderers.extend([vline])

            # JS callback for the slider
            callback = CustomJS(args=dict(span=vline), code="""
                span.location = cb_obj.value;
            """)

            # create slider
            time_slider = Slider(start=min(self.t), end=max(self.t), value=1, step=.1, title="")
            time_slider.js_on_change('value', callback)
            
            # create div for label
            div = Div(text=f"Pattern {i+1} ends here:")

            # add slider and label to list
            sliders.append(column(div, time_slider))

        show(layout([[self.p], sliders]), notebook_handle=True)

    def plot_with_zoom(self):
        # create the range tool (smaller plot)
        select = figure(height=100, width=600, y_range=self.p.y_range,
                        x_axis_type=None, y_axis_type=None,
                        tools="", toolbar_location=None, background_fill_color="#efefef")

        range_tool = RangeTool(x_range=self.p.x_range)
        range_tool.overlay.fill_color = "navy"
        range_tool.overlay.fill_alpha = 0.2

        select.line('x', 'y', source=self.source)
        select.ygrid.grid_line_color = None
        select.add_tools(range_tool)
        select.toolbar.active_multi = range_tool

        return column(self.p, select)

    # def plot_with_fixed_window(self, window_start, window_end):
    #     # create the range tool (smaller plot)
    #     select = figure(height=100, width=600, y_range=self.p.y_range,
    #                     x_axis_type=None, y_axis_type=None,
    #                     tools="", toolbar_location=None, background_fill_color="#efefef")

    #     # set the fixed window size to the main plot's x_range
    #     self.p.x_range = Range1d(window_start, window_end)

    #     range_tool = RangeTool(x_range=self.p.x_range)
    #     range_tool.overlay.fill_color = "navy"
    #     range_tool.overlay.fill_alpha = 0.2

    #     select.line('x', 'y', source=self.source)
    #     select.ygrid.grid_line_color = None
    #     select.add_tools(range_tool)
    #     select.toolbar.active_multi = range_tool

    #     return column(self.p, select)
    def plot_with_fixed_window(window_start, window_end):
        # create the range tool (smaller plot)
        select = figure(height=100, width=600, y_range=p.y_range,
                        x_axis_type=None, y_axis_type=None,
                        tools="", toolbar_location=None, background_fill_color="#efefef")
    
        # set the fixed window size to the main plot's x_range
        p.x_range.start = window_start
        p.x_range.end = window_end
    
        range_tool = RangeTool(x_range=p.x_range)
        range_tool.overlay.fill_color = "navy"
        range_tool.overlay.fill_alpha = 0.2
    
        select.line('x', 'y', source=source)
        select.ygrid.grid_line_color = None
        select.add_tools(range_tool)
        select.toolbar.active_multi = range_tool
        for tool in range_tool.tools:
            if isinstance(tool, PanTool) or isinstance(tool, WheelZoomTool):
                tool.disabled = True
    
        return column(p, select)

# def multi_plot_with_zoom(self, signals, window):
#         plots = []
#         for signal in signals:
#             plot = self.plot_with_fixed_window(0, window)
#             p = plot.children[0]
#             source = plot.children[1].renderers[0].data_source
#             p.line('x', 'y', source=source)
#             plots.append(plot)

#         rows = [plots[i:i+2] for i in range(0, len(plots), 2)]
#         show(layout(rows), notebook_handle=True)





def multi_plot_with_zoom(t, signals, window):
    plots = []
    for signal in signals:
        p = InteractivePlot(t, signal).p
        source = InteractivePlot(t, signal).source
        plot = plot_with_fixed_window(p, source, 0, window)
        plots.append(plot)

    rows = [plots[i:i+2] for i in range(0, len(plots), 2)]
    show(layout(rows), notebook_handle=True)

# def multi_plot_with_zoom(t, signals,window):
#     # plots = [InteractivePlot(t, signal).plot_with_zoom() for signal in signals]
#     plots = [InteractivePlot(t, signal).plot_with_fixed_window(0,window) for signal in signals]
#     rows = [plots[i:i+2] for i in range(0, len(plots), 2)]
    
#     show(layout(rows), notebook_handle=True)



class InteractiveDrawing:
    def __init__(self, num_plots):
        self.num_plots = num_plots
        self.plots = []
        self.grid = None
        self.text_areas = []
        output_notebook()
        
    def create_plot(self):
        for _ in range(self.num_plots):
            source = ColumnDataSource({
                'x': [], 'y': []
            })

            p = figure(x_range=(0, 10), y_range=(0, 10), width=400, height=400,
                       title='Draw on the plot',
                       tools='')

            # Change grid line color and dash
            p.xgrid.grid_line_color = "lightgray"
            p.ygrid.grid_line_color = "lightgray"
            p.xgrid.grid_line_dash = [4, 4]
            p.ygrid.grid_line_dash = [4, 4]

            renderer = p.multi_line('x', 'y', source=source)

            draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=3)
            p.add_tools(draw_tool)
            p.toolbar.active_drag = draw_tool

            # Add tap tool for clearing the data
            clear_source_code = """
            source.data = {'x': [], 'y': []};
            """
            clear_source_callback = CustomJS(args=dict(source=source), code=clear_source_code)
            p.js_on_event('tap', clear_source_callback)

            self.plots.append(p)

            # Add a Button and TextAreaInput for each plot
            # button = Button(label='Save', width=100)
            # text_area = TextAreaInput(value='', rows=6, title='source data:')
            
            # callback_code = """
            # text_area.value = JSON.stringify(source.data);
            # """
            # button.js_on_click(CustomJS(args=dict(source=source, text_area=text_area), code=callback_code))

            # self.plots.append(column(p, button, text_area))
        
        self.grid = gridplot(self.plots, ncols=2)
        
    def show_plot(self):
        if self.grid is not None:
            show(self.grid)
        else:
            print("No plots to show. Please create a plot first.")

class PatternSelector:
    def __init__(self):
        print('How many different patterns do you see in the data shown above? Please indicate by clicking on the corresponding number below.')
        self.value = None
        self.button1 = widgets.Button(description = '1')
        self.button2 = widgets.Button(description = '2')
        self.button3 = widgets.Button(description = '3')
        self.button4 = widgets.Button(description = '4')
        self.button5 = widgets.Button(description = '5')
        self.button1.on_click(self.on_button_clicked)
        self.button2.on_click(self.on_button_clicked)
        self.button3.on_click(self.on_button_clicked)
        self.button4.on_click(self.on_button_clicked)
        self.button5.on_click(self.on_button_clicked)
        display(self.button1, self.button2, self.button3, self.button4, self.button5)
        
    def on_button_clicked(self, b):
        print("Number of patterns you selected:", b.description)
        self.value = int(b.description)

class ModelSelection:
    def __init__(self):
        print('Considering the summaries provided by the two methods, please rate your preference for each method.')
        self.value = None
        self.button1 = widgets.Button(description = '1 - Strongly Prefer A')
        self.button2 = widgets.Button(description = '2 - Prefer A')
        self.button3 = widgets.Button(description = '3 - No Preference')
        self.button4 = widgets.Button(description = '4 - Prefer B')
        self.button5 = widgets.Button(description = '5 - Strongly Prefer B')
        self.button1.on_click(self.on_button_clicked)
        self.button2.on_click(self.on_button_clicked)
        self.button3.on_click(self.on_button_clicked)
        self.button4.on_click(self.on_button_clicked)
        self.button5.on_click(self.on_button_clicked)
        display(self.button1, self.button2, self.button3, self.button4, self.button5)
        
    def on_button_clicked(self, b):
        print("You select: ", b.description)
        self.value = b.description

class PairingComparison:
    def __init__(self):
        print('Considering how each method labaled data with corresponding patterns.')
        self.value = None
        self.button1 = widgets.Button(description = '1 - Strongly Prefer A')
        self.button2 = widgets.Button(description = '2 - Prefer A')
        self.button3 = widgets.Button(description = '3 - No Preference')
        self.button4 = widgets.Button(description = '4 - Prefer B')
        self.button5 = widgets.Button(description = '5 - Strongly Prefer B')
        self.button1.on_click(self.on_button_clicked)
        self.button2.on_click(self.on_button_clicked)
        self.button3.on_click(self.on_button_clicked)
        self.button4.on_click(self.on_button_clicked)
        self.button5.on_click(self.on_button_clicked)
        display(self.button1, self.button2, self.button3, self.button4, self.button5)
        
    def on_button_clicked(self, b):
        print("You select: ", b.description)
        self.value = b.description
