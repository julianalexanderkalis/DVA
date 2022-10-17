import pandas as pd
from bokeh.layouts import row, layout
from bokeh.models import ColumnDataSource, HoverTool, Select, FactorRange, Range1d
from bokeh.plotting import figure, curdoc, output_notebook, show

def callback(attr, old, new):

    if new == "Mammalia":
        final_source.data = dict(mammalia_source.data)
    elif new == "Aves":
        final_source.data = dict(aves_source.data)
    elif new == "Reptilia":
        final_source.data = dict(reptilia_source.data)
    p.y_range.factors = list(final_source.data["species"].values)
    
fulldata = pd.read_csv('dataset.csv', encoding='utf-8')
cols = [1, 3]
cols.extend([i for i in range(7, 15)])
fulldata.drop(fulldata.columns[cols], axis=1, inplace=True)

#renaming column labels
fulldata = fulldata.rename(columns = {"Species Common Name": "species", "TaxonClass" : "tacon_class", "Overall CI - lower" : "ci_lower", "Overall CI - upper" : "ci_upper", "Overall MLE" : "mle", "Male Data Deficient" : "male_deficient", "Female Data Deficient" : "female_deficient"})

#removing outliers
df_mammalia = fulldata[fulldata["tacon_class"] == "Mammalia"]
df_mammalia = df_mammalia[(df_mammalia["male_deficient"] != "yes") & (df_mammalia["female_deficient"] != "yes")]

df_aves = fulldata[fulldata["tacon_class"] == "Aves"]
df_aves = df_aves[(df_aves["male_deficient"] != "yes") & (df_aves["female_deficient"] != "yes")]

df_reptilia = fulldata[fulldata["tacon_class"] == "Reptilia"]
df_reptilia = df_reptilia[(df_reptilia["male_deficient"] != "yes") & (df_reptilia["female_deficient"] != "yes")].reset_index(drop = True)

#sorting and cutting the dataframes
df_mammalia = df_mammalia.sort_values(by = "mle", ascending = False).reset_index(drop = True)
df_aves = df_aves.sort_values(by = "mle", ascending = False).reset_index()
df_reptilia = df_reptilia.sort_values(by = "mle", ascending = False).reset_index()

df_mammalia = df_mammalia[0:10]
df_aves = df_aves[0:10]
df_reptilia = df_reptilia[0:10]

df_mammalia = df_mammalia.sort_values(by = "mle", ascending = True).reset_index()
df_mammalia.loc[:,"index"] = [0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5]

df_aves = df_aves.sort_values(by = "mle", ascending = True).reset_index(drop = True)
df_aves.loc[:,"index"] = [0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5]

df_reptilia = df_reptilia.sort_values(by = "mle", ascending = True).reset_index(drop = True)
df_reptilia.loc[:,"index"] = [0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5]

df_aves.loc[5, "species"] = "Penguin, Rockhopper"

#creating ColumnDataSources
mammalia_source = ColumnDataSource(dict(df_mammalia))
aves_source = ColumnDataSource(dict(df_aves))
reptilia_source = ColumnDataSource(dict(df_reptilia))
final_source = ColumnDataSource(mammalia_source.data)

y_label = final_source.data["species"]

#configuring the plot
p = figure(plot_width = 1500, plot_height = 750, y_range = y_label, title = "Medium Life Expectancy of Animals in Zoos")
p.yaxis.axis_label = "Species"
p.xaxis.axis_label = "Medium life expectancy [Years]"
    
p.x_range = Range1d(0, 50)
p.hbar(source = final_source, y = "index", left = "ci_lower", right = "ci_upper", height = 0.5)

hover = HoverTool(tooltips = [
    ("low", "@ci_lower"),
    ("high", "@ci_upper"),

    ])
p.add_tools(hover)

dropdown = Select(value="Mammalia", options = ["Mammalia", "Aves", "Reptilia"], title = "Taxonomic Class")

dropdown.on_change('value', callback)
    
lt = layout([[p, dropdown]])

curdoc().add_root(lt)