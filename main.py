"bokeh serve main.py"
from os.path import join, dirname

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput, Plot, Paragraph, Div
from bokeh.plotting import figure, show


toutchanged = []
def th(u): # temp in heater calculated with signal u from regulator
    input_start = 0
    input_end = 10

    output_start = 15
    output_end = 65

    if u < input_start:
        u = input_start
    elif u > input_end:
        u = input_end

    slope = (output_end - output_start) / (input_end - input_start)

    return output_start + slope * (u - input_start)


#def get_room_temp_list(KP, TI, TD, wanted_temp, temp_out, length, width, window_area):
def get_room_temp_list(KP, TI, TD, wanted_temp, temp_out):
    t = []  # temperatura w pokoju
    e_tab = []  # uchyb
    e_sum = 0  # suma uchybow

    KP = KP
    TI = TI
    TD = TD

    wanted_temp = wanted_temp
    temp_out = temp_out
    #room_len = length
    #room_wid = width
    #wall_area = (2.5 * length * 2) + (2.5 * width * 2) #pole scian
    #window_area = window_area

    #v = 2.5 * room_len * room_wid
    #mp = 1.2 * v #masa powietrza
    c = 1005.4

    m_heater = 3600 #constant rate of air mass passing through heater (kg/hour)
    c_air = 1005.4 #heat capacity (J/kg C)
    k = 1.7 #Thermal conductivity coefficient (W/m C)
    #A = 2.5 * 4 #Cross section area (m^2)
    #A = cross_section_area
    D = 0.2 #wall thickness
    R2 = 0.000000427
    m_roomair = 1470

    #calculate R
    D_wall = 0.2 #grubosc sciany [m]
    D_window = 0.015 #grubość szyby [m]
    glass_coefficient = 0.17
    concrete_coefficient = 0.8
    #R_concrete = D_wall / (concrete_coefficient * wall_area)
    #R_window = D_window / (glass_coefficient * window_area)
    #R = (R_concrete * R_window) / (R_concrete + R_window)

    for i in range(0, n):
        if i == 0:
            t.append(temp_out)#start temp in room
            e = wanted_temp - t[i]
            e_tab.append(e)
            e_sum += e

        else:
            #obliczenie uchybu e
            e = wanted_temp - t[i - 1]
            e_tab.append(e)
            e_sum += e

            #obliczenie sygnalu z regulatora U
            u = KP * (e_tab[i] + ((TP / TI) * e_sum) + ((TD / TP) * (e_tab[i] - e_tab[i - 1])))

            t_heater = th(u)

            #q_gain = (t_heater - t[i - 1]) * (mp * c)
            #q_loss = (t[i-1] - temp_out)/R
            #tr = ((q_gain - q_loss)/(mp * c)) * TP + t[i-1]


            q_gain = (m_heater * c_air) * (t_heater - t[i-1])
            q_loss = ((t[i-1] - temp_out) / R2)
            #q_loss = ((t[i-1] - toutchanged[i-1]) / R2)

            tr = ((q_gain - q_loss) / (m_roomair * c_air)) * TP + t[i-1]


            t.append(tr)
            #print(i, u)
    return t


wanted_tmp = 25
Tout = 10
KP = 0.015#0.6
TI = 0.5
TD = 0.25#0.12
leng = 5
wid = 5
A_window = 5 #powierzchnia okien [m^2]


time = 360 #* 24 #sekundy
TP = 0.1
n = int(time / TP)


for x in range(0, n):
    if x >= n/2:
        toutchanged.append(0)
    else:
        toutchanged.append(10)


# Set up data
y = get_room_temp_list(KP, TI, TD, wanted_tmp, Tout)

x = [x/10 for x in range(0, len(y))]

y2 = [wanted_tmp for i in range(0, len(y))] #want temp
Tout2 = [Tout] * n #temp out
#Tout2 = toutchanged


source = ColumnDataSource(data=dict(x=x, y=y, y2=y2, Tout2=Tout2))

# Set up plot
plot = figure(height=400, width=700, title="Symulacja temperatury w pomieszczeniu",
              tools="crosshair,pan,reset,save,wheel_zoom",
              y_axis_label="Temperatura w pomieszczeniu [C]",
              x_axis_label="Czas [s]")

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.3, legend_label="Temp. w pomieszczeniu")
plot.line('x', 'y2', source=source, line_width=2, line_alpha=1, color="green", legend_label="Temp. pożądana")
plot.line('x', 'Tout2', source=source, line_width=2, line_alpha=1, color="red", legend_label="Temp. na zewnątrz")



#Set up widgets

want_temp_input = Slider(title="Temperatura pożądana", value=wanted_tmp, start=-30, end=60, step=1)
temp_out_input = Slider(title="Temperatura na zewnątrz", value=Tout, start=-30, end=60, step=1)
KP_slider = Slider(title="KP", value=0.015, start=0, end=1, step=0.005)
TI_slider = Slider(title="TI", value=0.5, start=0, end=1, step=0.05)
TD_slider = Slider(title="TD", value=0.25, start=0, end=1, step=0.05)


#setup callbacks
def update_data(attrname, old, new):
    w_temp = want_temp_input.value
    t_out = temp_out_input.value
    kp = KP_slider.value
    ti = TI_slider.value
    td = TD_slider.value
    #a_wind = Area_window_slider.value
    #leng = room_length_slider.value
    #wid = room_width_slider.value
    #a = Area_cross_section_slider.value

    #new plots
    y_ = get_room_temp_list(kp, ti, td, w_temp, t_out)
    x_ = [i/10 for i in range(0, len(y))]
    y2_ = [w_temp for i in range(0, len(y))]  # want temp
    tout_ = [t_out] * n  # temp out
    #tout_ = toutchanged

    source.data = dict(x=x_, y=y_, y2=y2_, Tout2=tout_)


#for w in [want_temp_input, temp_out_input, KP_slider, TD_slider, TI_slider, Area_window_slider, room_length_slider, room_width_slider]:
for w in [want_temp_input, temp_out_input, KP_slider, TD_slider, TI_slider]:
    w.on_change('value', update_data)



#Set up layouts and add to document

div = Div(text="""
<h1>SYMULACJA TEMPERATURY W POMIESZCZENIU </h1>
<p>Wykres przedstawia zachowanie temperatury regulowanej przez termowentylator w zalezżności od nastepujacych parametrów: <br />
    1) temperatury pożądanej <br />
    2) temperatury panującej na dworze <br />
    3) wzmocnienia regulatora KP<br />
    4) czasu zdwojenia TI<br />
    5) czasu wyprzedzenia TD.<br />
</p>""", width=700, height=220)
inputs = column(want_temp_input, temp_out_input, KP_slider, TI_slider, TD_slider)
p = Paragraph(text="Jakub Cichowicz \nJakub Ciulęba", width=100, height=100)
#desc = Div(text=open(join(dirname(__file__), "desc.html")).read(), sizing_mode="stretch_width")

curdoc().add_root(column(div, row(inputs, plot), p, width=900))
curdoc().title = "Temperature in room"


show(plot)
