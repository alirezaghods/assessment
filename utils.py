from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure, curdoc
from bokeh.models import Span, CustomJS, Slider, ColumnDataSource, Div, RangeTool, FreehandDrawTool
from bokeh.layouts import layout, column, gridplot
from bokeh.themes import Theme
from bokeh.palettes import Category10
import ipywidgets as widgets
from IPython.display import display
output_notebook()

class InteractivePlot:
    def __init__(self, t, signal):
        self.t = t
        self.signal = signal

        # create a data source to enable refreshing of fill
        self.source = ColumnDataSource(data=dict(x=self.t, y=self.signal))

        # create main scatter plot, as a line (with fill)
        self.p = figure(height=300, width=600, tools="", x_range=(min(self.t), max(self.t)), background_fill_color='black')
        self.p.line('x', 'y', source=self.source, line_color='white')

        # theme everything for a cleaner look
        curdoc().theme = Theme(json={
            "attrs": {
                "Plot": { "toolbar_location": None },
                "Grid": { "grid_line_color": None },
                "Axis": {
                    "axis_line_color": None,
                    "major_label_text_color": "white",
                    "major_tick_line_color": "white",
                    "minor_tick_line_color": "white",
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



def multi_plot_with_zoom(t, signals):
    plots = [InteractivePlot(t, signal).plot_with_zoom() for signal in signals]
    
    rows = [plots[i:i+2] for i in range(0, len(plots), 2)]
    
    show(layout(rows), notebook_handle=True)


from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, FreehandDrawTool
from bokeh.layouts import gridplot

class InteractiveDrawing:
    def __init__(self, num_plots):
        self.num_plots = num_plots
        self.plots = []
        self.grid = None
        output_notebook()
        
    def create_plot(self):
        for _ in range(self.num_plots):
            source = ColumnDataSource({
                'x': [], 'y': []
            })

            p = figure(x_range=(0, 10), y_range=(0, 10), width=400, height=400,
                       title='Draw on the plot',
                       tools='')

            renderer = p.multi_line('x', 'y', source=source)

            draw_tool = FreehandDrawTool(renderers=[renderer], num_objects=3)
            p.add_tools(draw_tool)
            p.toolbar.active_drag = draw_tool

            self.plots.append(p)
        
        self.grid = gridplot(self.plots, ncols=2)
        
    def show_plot(self):
        if self.grid is not None:
            show(self.grid)
        else:
            print("No plots to show. Please create a plot first.")

class PatternSelector:
    def __init__(self):
        print('How many distinct patterns you see in the given signal?')
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
        print("Number of patterns, selected by you is: ", b.description)
        self.value = int(b.description)