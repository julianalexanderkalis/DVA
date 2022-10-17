import numpy as np
from bokeh.models import ColumnDataSource, Button, Select, Div
from bokeh.sampledata.iris import flowers
from bokeh.plotting import figure, curdoc, output_notebook, show
from bokeh.layouts import column, row

# defining the dataset
data = flowers.copy(deep=True)
data = data.drop(['species'], axis=1)

# setting starting color to grey
data["color"] = "grey"

# constructing DataSource and plot figures
source = ColumnDataSource(data = dict(sepal_length = data["sepal_length"], sepal_width = data["sepal_width"], petal_length = data["petal_length"], petal_width = data["petal_width"], color = data["color"]))

p1 = figure(plot_width = 600, plot_height = 500, tools="")
p1.scatter(y = 'sepal_length', x = 'petal_length', marker = "circle", size = 5, fill_color = 'color', line_color= 'color', fill_alpha = 0.5, source = source)
p1.title.text = 'Scatterplot of flower distribution by petal length and sepal length'
p1.yaxis.axis_label = "Sepal length"
p1.xaxis.axis_label = "Petal length"


p2 = figure(plot_width = 600, plot_height = 500, tools="")
p2.scatter(y = 'petal_length', x = 'petal_width', marker = "circle", size = 5, fill_color = 'color', line_color= 'color', fill_alpha = 0.5, source = source)
p2.title.text = 'Scatterplot of flower distribution by petal width and petal length'
p2.yaxis.axis_label = "Petal length"
p2.xaxis.axis_label = "Petal width"

# calculating distance matrix using manhattan distance to later access when computing the total costs
D = np.zeros(shape=(150,150))

for index, item in enumerate(D):
    for index_2, i in enumerate(item):
        
        D[index][index_2] = np.abs(data.loc[index, "sepal_length"] - data.loc[index_2, "sepal_length"]) + np.abs(data.loc[index, "petal_length"] - data.loc[index_2, "petal_length"]) + np.abs(data.loc[index, "petal_width"] - data.loc[index_2, "petal_width"]) + np.abs(data.loc[index, "sepal_width"] - data.loc[index_2, "sepal_width"])        

# calculating the cost by using vectorized function over array of datapoints
def get_cost(meds):
    
    cost = 0
    
    # calculating the minimal individual cost per point
    def ind_cost(i):
        
        l = np.min( [D[meds[0]][i], D[meds[1]][i], D[meds[2]][i]] )
        return l
    
    ind_cost_v = np.vectorize(ind_cost)
    t = ind_cost_v(np.arange(0,150))
    
    # return sum of all minimal distances
    return sum(t)


def k_medoids():

    k = 3
    
    # distinction between random == "True" or random == "False"
    if dropdown.value == "False":
        medoids = [24, 74, 124]
    else:
        medoids = list(np.random.choice(150, 3, replace = False))
    total_distance = get_cost(medoids)
    
    # to_remember variations to compare with last available distance and medoid cluster
    to_remember = medoids
    to_remember_cost = total_distance
        
    while True:
        
        # greedy search
        
        for item in np.arange(0, 150):

            result = get_cost([item, to_remember[1], to_remember[2]])

            if result < to_remember_cost:
                    to_remember_cost = result
                    to_remember = [item, to_remember[1], to_remember[2]]

            result = get_cost([to_remember[0], item, to_remember[2]])

            if result < to_remember_cost:
                    to_remember_cost = result
                    to_remember = [to_remember[0], item, to_remember[2]]

            result = get_cost([to_remember[0], to_remember[1], item])

            if result < to_remember_cost:
                    to_remember_cost = result
                    to_remember = [to_remember[0], to_remember[1], item]
                    
        # deciding whether to continue or terminate the algorithm
        if to_remember_cost < total_distance:
            total_distance = to_remember_cost
        else:
            break
       
    return total_distance, to_remember

# adjust dashboard performs the color mapping and the div.text update
def adjust_dashboard():
    
    total_distance, meds = k_medoids()
    
    print(total_distance)
    
    # same as calculating distances, but argmin returns the indices of the chosen medoid instead of the distance to it, used for colormapping
    def calc_clusters(i):
        
        l = np.argmin( [D[meds[0]][i], D[meds[1]][i], D[meds[2]][i]] )
        if l == 0: return "red"
        elif l == 1: return "blue"
        else: return "green"
    
    cluster_v = np.vectorize(calc_clusters)
    t = cluster_v(np.arange(0,150))

    # adjusting the dashboard
    source.data["color"] = t
    div.text =  "The final cost is: " + str(np.round(total_distance, 2))

# defining the necessary widgets
dropdown = Select(value="False", options = ["False", "True"], title = "Random Medoids")
button = Button(label="Cluster Data")
button.on_click(adjust_dashboard)
div = Div(text = "Nothing calculated yet", width = 200, height = 100)
#output_notebook()

curdoc().title = "DVA_ex_3"
curdoc().add_root(row(column(dropdown, button, div),p1,p2))
show(row(column(dropdown, button, div),p1,p2))