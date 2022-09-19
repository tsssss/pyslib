import matplotlib.pyplot as plt
import matplotlib as mpl
import system.manager as smg
from system.manager import data_quants
import libs.math as math
import system.constant as constant

plot_setting_key = 'plot_setting'
default_plot_setting = {
    'lines.linewidth': 1,
    'axes.grid': 'on',
    'xtick.direction': 'out',
    'xtick.top': True,
    'xtick.bottom': True,
    'xtick.minor.visible': True,
    'xtick.minor.top': True,
    'xtick.minor.bottom': True,
    'ytick.direction': 'out',
    'ytick.left': True,
    'ytick.right': True,
    'ytick.minor.visible': True,
    'ytick.minor.left': True,
    'ytick.minor.right': True,
    'legend.frameon': False,
    'legend.loc': 'center left',
    'legend.handlelength': 0,
    'legend.handletextpad': 0,
}
default_figsize = (6,3)
default_fig_label_offset = 12



def set_plot_setting(var, settings):
    if plot_setting_key not in data_quants[var].attrs:
        data_quants[var].attrs[plot_setting_key] = default_plot_setting
    data_quants[var].attrs[plot_setting_key].update(settings)


from matplotlib import ticker
import libs.epoch as epoch
@ticker.FuncFormatter
def slib_time_formatter(x, pos):
    msg = epoch.convert_time(x, input='unix', output='%H:%M')
    if pos == 0 or x % constant.secofday == 0:
        msg += '\n'+epoch.convert_time(x, input='unix', output='%Y-%m-%d')
#        msg += '\n'+epoch.convert_time(x, input='unix', output='%b %d %Y')
    return msg


def get_plot_setting(var, key=None):
    if plot_setting_key not in data_quants[var].attrs:
        data_quants[var].attrs[plot_setting_key] = default_plot_setting
    plot_setting = data_quants[var].attrs[plot_setting_key]
    if key is not None:
        return plot_setting.get(key, None)
    else:
        return plot_setting

# A link explains OO of matplotlib.
# https://matplotlib.org/matplotblog/posts/pyplot-vs-object-oriented-interface/ 
# Matplot anatomy example.
# https://matplotlib.org/2.0.2/examples/showcase/anatomy.html


def add_fig_label(ax, fig_label, offset=None):

    if fig_label is None: fig_label = 'a)'
    if offset is None: offset = default_fig_label_offset
    ax.text(0,1, fig_label+offset*' ', va='top', ha='right', transform=ax.transAxes)


def plot_scalar(var,
    position=None,
    xrange=None,
    ytitle=None,
    fig_label=None,
    fig=None,
):

    if position is None:
        position = [0.15,0.15,0.7,0.8]
    ax = fig.add_axes(position)

    x = smg.get_time(var)
    y = smg.get_data(var)
    var_settings = smg.get_setting(var)

    if ytitle is None:
        unit = var_settings.get('UNITS', None)
        ytitle = make_title_from_unit(unit)
    labels = var_settings['short_name']
    colors = 'black'

    ax.plot(x,y, color=colors, label=labels)

    # Add lagend.
    lg = ax.legend(
        bbox_to_anchor=(1,0.5),
        loc='center left',
        frameon=False,
        handlelength=0,
        handletextpad=0,
    )
    text = (lg.get_texts())[0]
    text.set_color(colors)

    if ytitle is not None:
        ax.set_ylabel(ytitle)
    ax.tick_params(axis='x', which='major', bottom=True)
    ax.tick_params(axis='x', which='major', top=True)
    ax.tick_params(axis='y', which='major', left=True)
    ax.tick_params(axis='y', which='major', right=True)

    plt.minorticks_on()
    ax.tick_params(axis='x', which='minor', bottom=True)
    ax.tick_params(axis='x', which='minor', top=True)
    ax.tick_params(axis='y', which='minor', left=True)
    ax.tick_params(axis='y', which='minor', right=True)
    ax.grid(linewidth=0.5, color='gray', alpha=0.25)

    # Set xticks.
    if xrange is None: xrange = [min(x),max(x)+60]
    xminor = 6
    xstep = 3600*xminor
    xticks = math.mkarthm(xrange[0], xrange[1], xstep, 'dx')
    ax.set_xticks(xticks)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(xminor))
    ax.set_xlim(xrange)
    ax.xaxis.set_major_formatter(slib_time_formatter)

    # Add figure label.
    add_fig_label(ax, fig_label)


def plot_vector(var,
    position=None,
    xrange=None,
    ytitle=None,
    fig_label=None,
    fig=None,
):

    if position is None:
        position = [0.15,0.15,0.7,0.8]
    ax = fig.add_axes(position)

    x = smg.get_time(var)
    y = smg.get_data(var)
    var_settings = smg.get_setting(var)

    if ytitle is None:
        unit = var_settings.get('UNITS', None)
        ytitle = make_title_from_unit(unit)

    colors = list('rgb')
    coord = var_settings['coord']
    short_name = var_settings['short_name']
    coord_labels = var_settings['coord_labels']
    labels = [coord.upper()+' $'+short_name+'_'+x+'$' for x in coord_labels]
    ndim = len(colors)
    for i in range(ndim):
        ax.plot(x,y[:,i], color=colors[i], label=labels[i])

    if ytitle is not None:
        ax.set_ylabel(ytitle)
    ax.tick_params(axis='x', which='major', bottom=True)
    ax.tick_params(axis='x', which='major', top=True)
    ax.tick_params(axis='y', which='major', left=True)
    ax.tick_params(axis='y', which='major', right=True)

    plt.minorticks_on()
    ax.tick_params(axis='x', which='minor', bottom=True)
    ax.tick_params(axis='x', which='minor', top=True)
    ax.tick_params(axis='y', which='minor', left=True)
    ax.tick_params(axis='y', which='minor', right=True)
    ax.grid(linewidth=0.5, color='gray', alpha=0.25)

    # Add lagend.
    lg = ax.legend(
        bbox_to_anchor=(1,0.5),
        loc='center left',
        frameon=False,
        handlelength=0,
        handletextpad=0,
    )
    for text, color in zip(lg.get_texts(),colors):
        text.set_color(color)

    # Set xticks.
    if xrange is None: xrange = [min(x),max(x)+60]
    xminor = 6
    xstep = 3600*xminor
    xticks = math.mkarthm(xrange[0], xrange[1], xstep, 'dx')
    ax.set_xticks(xticks)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(xminor))
    ax.set_xlim(xrange)
    ax.xaxis.set_major_formatter(slib_time_formatter)

    # Add figure label.
    add_fig_label(ax, fig_label)

    return ax



def set_color(var, colors):
    if colors is not str:
        c = ''.join(colors)
    else:
        c = colors
    set_plot_setting(var, {'axes.prop_cycle': mpl.cycler('color',c)})


def plot(var,
    position=None,
    xrange=None,
    figsize=default_figsize,
):

    if xrange is not None:
        xrange = smg.prepare_time_range(xrange)

    fig = plt.figure(1, figsize=figsize)
    fig_label = 'a)'

    display_type = smg.get_setting(var, 'display_type')
    if display_type == 'vector':
        ax = plot_vector(var, fig=fig, xrange=xrange, fig_label=fig_label)
    elif display_type == 'scalar':
        ax = plot_scalar(var, fig=fig, xrange=xrange, fig_label=fig_label)
    
    return ax


def make_title_from_unit(unit):
    if unit is None: return None
    return '('+unit+')'