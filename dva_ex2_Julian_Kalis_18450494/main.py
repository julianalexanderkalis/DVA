import glob
import os
import numpy as np
from PIL import Image

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, ImageURL, Line, Circle, Ellipse
from bokeh.layouts import layout


N = len(glob.glob("static/*.jpg"))

ROOT = os.path.split(os.path.abspath("."))[1] + "/"
N_BINS_COLOR = 16
N_BINS_CHANNEL = 50

#defining histograms
color_histograms = np.zeros((N, 4096), dtype=object)
channel_histograms = np.zeros(N, dtype=object)

# initialize an empty list for the image file paths
image_file_paths = []

# Compute the color and channel histograms
for idx, f in enumerate(glob.glob("static/*.jpg")):

    im = Image.open(f)
    im_array = np.array(im)
    im_array = im_array.reshape((184320, 3))
    
    md_hist, md_bounds = np.histogramdd(sample = im_array, bins = N_BINS_COLOR)
    md_hist = np.reshape(md_hist, 4096) 
    color_histograms[idx] = md_hist

    url = ROOT + f
    image_file_paths.append(url)
   
    r = [i[0] for i in im_array]
    g = [i[1] for i in im_array]
    b = [i[2] for i in im_array]
    
    norm_r_hist, norm_bounds = np.histogram(r, bins = N_BINS_CHANNEL)
    norm_g_hist, norm_bounds = np.histogram(g, bins = N_BINS_CHANNEL)
    norm_b_hist, norm_bounds = np.histogram(b, bins = N_BINS_CHANNEL)
    
    channel_histograms[idx] = np.array([norm_r_hist, norm_g_hist, norm_b_hist])


tsne = TSNE().fit_transform(color_histograms) 
pca = PCA().fit_transform(color_histograms)

source = ColumnDataSource(data = dict(tsne_x = [i[0] for i in tsne], tsne_y = [i[1] for i in tsne], pca_x = [i[0] for i in pca], pca_y = [i[1] for i in pca], image_path = image_file_paths))

p1 = figure(plot_height = 500, plot_width = 600, title = 't-SNE', tools = ("lasso_select", "wheel_zoom", "pan", "reset"))
p1.yaxis.axis_label = "x"
p1.xaxis.axis_label = "y"

#defining selected and non-selected glyphs behavior
selected_c = Circle(fill_color='green', fill_alpha = 0, line_color=None)
nonselected_c = Circle(fill_color='red', fill_alpha = 0, line_color=None)

selected_i = ImageURL(global_alpha = 1, h = 20, w = 32, w_units = "screen", h_units = "screen", anchor = "center")
nonselected_i = ImageURL(global_alpha = 0,h = 20, w = 32, w_units = "screen", h_units = "screen", anchor = "center")

#add image_url to plot
for item in range(N + 1):

    renderer_i = p1.image_url(source = source, url = "image_path", x = "tsne_x", y = "tsne_y", h = 20, w = 32, w_units = "screen", h_units = "screen", anchor = "center")
    renderer_i.selection_glyph = selected_i
    renderer_i.nonselection_glyph = nonselected_i

    renderer_c = p1.circle(x = "tsne_x", y = "tsne_y", size = 5,source=source, fill_alpha = 0, line_color=None)
    renderer_c.selection_glyph = selected_c
    renderer_c.nonselection_glyph = nonselected_c


p2 = figure(plot_height = 500, plot_width = 600, title = 'PCA', tools = ("lasso_select", "wheel_zoom", "pan", "reset"))
p2.yaxis.axis_label = "x"
p2.xaxis.axis_label = "y"

#add image_url to plot
for item in range(N + 1):

    renderer_i = p2.image_url(source = source, url = "image_path", x = "pca_x", y = "pca_y", h = 20, w = 32, w_units = "screen", h_units = "screen", anchor = "center")
    renderer_i.selection_glyph = selected_i
    renderer_i.nonselection_glyph = nonselected_i

    renderer_c = p2.circle(x = "pca_x", y = "pca_y", size = 5,source=source, fill_alpha = 0, line_color=None)
    renderer_c.selection_glyph = selected_c
    renderer_c.nonselection_glyph = nonselected_c


#computing the histogram
r = [i[0] for i in channel_histograms]
r_final = np.zeros(50, dtype=object)

for i in r:
    for index, item in enumerate(i):
        r_final[index] += item

max_r = max(r_final)
r_final = [i/max_r for i in r_final]


g = [i[1] for i in channel_histograms]
g_final = np.zeros(50, dtype=object)

for i in g:
    for index, item in enumerate(i):
        g_final[index] += item

max_g = max(g_final)
g_final = [i/max_g for i in g_final]



b = [i[2] for i in channel_histograms]
b_final = np.zeros(50, dtype=object)

for i in b:
    for index, item in enumerate(i):
        b_final[index] += item

max_b = max(b_final)
b_final = [i/max_b for i in b_final]


channel_source = ColumnDataSource(data = dict(r = r_final, g = g_final, b = b_final, bins = np.arange(1,51)))

#plotting the histogram
p3 = figure(plot_height = 500, plot_width = 800, title = 'Channel Histogram', tools = ("wheel_zoom", "pan", "reset"))

p3.yaxis.axis_label = "Frequency"
p3.xaxis.axis_label = "bin"

line = Line(x="bins", y="r", line_color="red", line_width=5, line_alpha=0.6)
p3.add_glyph(channel_source, line)

line = Line(x="bins", y="g", line_color="green", line_width=5, line_alpha=0.6)
p3.add_glyph(channel_source, line)

line = Line(x="bins", y="b", line_color="blue", line_width=5, line_alpha=0.6)
p3.add_glyph(channel_source, line)

#defining the histogram update function, works in the same way as default, just different data as input
def update(attr, old, new):
    values = new
    new_channel_hist = [channel_histograms[item] for item in values]
    
    r = [i[0] for i in new_channel_hist]
    r_final = np.zeros(50, dtype=object)
    
    for i in r:
        for index, item in enumerate(i):
            r_final[index] += item
    max_r = max(r_final)
    r_final = [i/max_r for i in r_final]


    g = [i[1] for i in new_channel_hist]
    g_final = np.zeros(50, dtype=object)

    for i in g:
        for index, item in enumerate(i):
            g_final[index] += item

    max_g = max(g_final)
    g_final = [i/max_g for i in g_final]

    b = [i[2] for i in new_channel_hist]
    b_final = np.zeros(50, dtype=object)

    for i in b:
        for index, item in enumerate(i):
            b_final[index] += item

    max_b = max(b_final)
    b_final = [i/max_b for i in b_final]


    channel_source.data = dict(r = r_final, g = g_final, b = b_final, bins = np.arange(1,51))

source.selected.on_change("indices", update)
    
p = layout(
    [[p1, p2, p3]]
)
curdoc().add_root(p)