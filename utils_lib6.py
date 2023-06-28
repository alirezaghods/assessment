from bokeh.io import output_notebook, push_notebook, show
from bokeh.models import ColumnDataSource, BoxAnnotation, Slider, CustomJS, Range1d, Span, Div
from bokeh.plotting import figure
from bokeh.layouts import column, gridplot, layout
import numpy as np
import ipywidgets as widgets
from IPython.display import display
output_notebook()

class InteractivePlot:
    def __init__(self, data, window_size):
        self.data = data
        self.window_size = window_size
        
    def plot(self):
        

        # Generate an array of indices with the same length as the data array
        x = np.arange(len(self.data))
        source = ColumnDataSource(data=dict(x=x, y=self.data))

        self.p = figure(height=150, width=400, tools="", toolbar_location=None,
                   x_axis_type=None, x_axis_location="above",
                   background_fill_color="#efefef", y_axis_location=None)

        self.p.line('x', 'y', source=source, line_width=2)  # Increase line width
        self.p.yaxis.major_label_text_font_size = '0pt'  # Remove y-axis ticks

        select = figure(height=65, width=400, tools="", toolbar_location=None, 
                        x_axis_type=None, y_axis_type=None, 
                        background_fill_color="#efefef")

        select.line('x', 'y', source=source)
        select.ygrid.grid_line_color = None

        # Initial values for the highlight box
        left = x[0]
        right = x[self.window_size]
        box = BoxAnnotation(left=left, right=right, fill_color='red', fill_alpha=0.1)
        select.add_layout(box)

        # Slider
        slider = Slider(start=0, end=len(self.data), value=0, step=1, title="Drag to change the highlighted range")

        # JavaScript code to update the highlight box and top plot range
        callback = CustomJS(args=dict(p=self.p, box=box, slider=slider, window_size=self.window_size), code="""
            box.left = slider.value;
            box.right = slider.value + window_size;
            p.x_range.start = slider.value;
            p.x_range.end = slider.value + window_size;
        """)

        # Execute the callback whenever the slider value changes
        slider.js_on_change('value', callback)

        # Return the plot
        return column(self.p, select, slider)


    def plot_with_patterns(self, num_patterns):
        colors = ['red', 'green', 'blue', 'orange', 'purple', 'cyan', 'magenta']  # add more colors if needed
        sliders = []
        for i in range(num_patterns):
            # create the vertical line
            vline = Span(location=0, dimension='height', line_width=2, line_color=colors[i % len(colors)])
            self.p.renderers.extend([vline])

            # JS callback for the slider
            callback = CustomJS(args=dict(span=vline), code="""
                span.location = cb_obj.value;
            """)

            # create slider
            time_slider = Slider(start=0, end=len(self.data), value=1, step=.1, title="")
            time_slider.js_on_change('value', callback)
            
            # create div for label
            div = Div(text=f"Pattern {i+1} ends here:")

            # add slider and label to list
            sliders.append(column(div, time_slider))

        # Return all the sliders and the plot in a single column layout
        return column(self.p, *sliders)






def multi_plot_with_zoom(signals, window):
    # Create an interactive plot for each signal and arrange them in rows
    plots = [InteractivePlot(signal, window_size=window).plot() for signal in signals]
    rows = [plots[i:i+2] for i in range(0, len(plots), 2)]

    # Display the plots
    handle = show(layout(rows), notebook_handle=True)
    push_notebook(handle=handle)
    




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