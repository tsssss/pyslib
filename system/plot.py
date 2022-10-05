import matplotlib.pyplot as plt
import matplotlib as mpl
import system.manager as smg
from system.manager import data_quants
import numpy as np
from matplotlib import ticker
import libs.epoch as epoch
import libs.math as math

high_level_vars = ['combo_scalar','scalar_with_color','combo_vector']


default_position = [0.2,0.2,0.7,0.8]
default_linewidth = 1
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
default_fig_label_offset = 10



def set_plot_setting(var, settings):
    if plot_setting_key not in data_quants[var].attrs:
        data_quants[var].attrs[plot_setting_key] = default_plot_setting
    data_quants[var].attrs[plot_setting_key].update(settings)


@ticker.FuncFormatter
def slib_time_formatter(x, pos):
    msg = epoch.convert_time(x, input='unix', output='%H:%M\n%Y-%m-%d')
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



def open(
    figsize=(6,4),
):

    # fig = matplotlib.pyplot.gcf()
    # fig.set_size_inches(18.5, 10.5)
    return plt.figure(1, figsize=figsize)



def set_color(var, colors):
    if colors is not str:
        c = ''.join(colors)
    else:
        c = colors
    set_plot_setting(var, {'axes.prop_cycle': mpl.cycler('color',c)})



def make_title_from_unit(unit):
    if unit is None: return None
    return '('+unit+')'



class Fig():

    default_figure_size = (6,3)

    def __init__(self,
        size=default_figure_size,
    ):

        self.fig = plt.figure(figsize=size)
        self.abs_charsize = _get_abs_chsz()
        self.panels = None
        self.size = size

    
    def panel_pos(
        self,
        pansize=(2,0.5),
        panid=(0,0),
        nxpan=1,
        nypan=1,
        xpans=[1],
        ypans=[1],
        xpads=[8],
        ypads=[0.4],
        margins=[10,2,4,1],
        fit_method='as_is',
    ):

        self.panel_init(
            pansize=pansize,
            panid=panid,
            nxpan=nxpan,
            nypan=nypan,
            xpans=xpans,
            ypans=ypans,
            xpads=xpads,
            ypads=ypads,
            margins=margins,
        )

        if fit_method == 'as_is':
            pass
        elif fit_method == 'resize':
            fig_size = self.fig.get_size_inches()
            self.panel_resize(xsize=fig_size[0], ysize=fig_size[1])
        
        self.panel_normlize()

        panshape = self.panels['norm_pos'].shape
        axes = list()
        for xpan_id in range(panshape[1]):
            the_axes = list()
            for ypan_id in range(panshape[2]):
                rect = self.panels['norm_pos'][:,xpan_id,ypan_id].copy()
                rect[2] = rect[2]-rect[0]
                rect[3] = rect[3]-rect[1]
                the_axes.append(self.fig.add_axes(rect))
            axes.append(the_axes)

        shared_id = nypan-1
        for xpan_id in range(panshape[1]):
            for ypan_id in range(panshape[2]):
                if ypan_id != shared_id:
                    axes[xpan_id][ypan_id].get_shared_x_axes().join(axes[xpan_id][ypan_id],axes[xpan_id][shared_id])
                    axes[xpan_id][ypan_id].set_xticklabels([])
            
                axes[xpan_id][ypan_id].minorticks_on()
                axes[xpan_id][ypan_id].grid(linewidth=default_linewidth*0.5, color='gray', alpha=0.25)
                axes[xpan_id][ypan_id].tick_params(axis='y', which='major', left=True)
                axes[xpan_id][ypan_id].tick_params(axis='y', which='major', right=True)
                axes[xpan_id][ypan_id].tick_params(axis='y', which='minor', left=True)
                axes[xpan_id][ypan_id].tick_params(axis='y', which='minor', right=True)

                axes[xpan_id][ypan_id].tick_params(axis='x', which='major', top=True)
                axes[xpan_id][ypan_id].tick_params(axis='x', which='minor', top=True)
                axes[xpan_id][ypan_id].tick_params(axis='x', which='major', bottom=True)
                axes[xpan_id][ypan_id].tick_params(axis='x', which='minor', bottom=True)

        self.axes = axes
        return axes




    def panel_normlize(
        self
    ):

        abs_pos = self.panels['abs_pos']
        norm_pos = abs_pos
        norm_pos[[0,2],:,:] /= self.panels['xsize']
        norm_pos[[1,3],:,:] /= self.panels['ysize']
        self.panels['norm_pos'] = norm_pos



    def panel_resize(
        self,
        xsize=default_figure_size[0],
        ysize=default_figure_size[1],
    ):

        abs_pos = self.panels['abs_pos']
        if xsize is not None:
            xpans = self.panels['xpansize']
            abs_xspace = self.panels['xspace']
            xpans = (xsize-np.sum(abs_xspace))/np.sum(xpans)*xpans
            for xpan_id in range(len(xpans)):
                if xpan_id == 0:
                    x0 = 0
                else:
                    x0 = abs_pos[2,xpan_id-1,0]
                abs_pos[0,xpan_id,:] = x0+abs_xspace[xpan_id]
                abs_pos[2,xpan_id,:] = abs_pos[0,xpan_id,:]+xpans[xpan_id]
            self.panels['xpansize'] = xpans
            self.panels['xsize'] = xsize
        if ysize is not None:
            ypans = self.panels['ypansize']
            abs_yspace = self.panels['yspace']
            ypans = (ysize-np.sum(abs_yspace))/np.sum(ypans)*ypans
            for ypan_id in range(len(ypans)):
                if ypan_id == 0:
                    y0 = ysize
                else:
                    y0 = abs_pos[1,0,ypan_id-1]
                abs_pos[3,:,ypan_id] = y0-abs_yspace[ypan_id]
                abs_pos[1,:,ypan_id] = abs_pos[3,:,ypan_id]-ypans[ypan_id]
            self.panels['ypansize'] = ypans
            self.panels['ysize'] = ysize

    def panel_init(
        self,
        pansize=[2,0.5],
        panid=(0,0),
        nxpan=1,
        nypan=1,
        xpans=[1],
        ypans=[1],
        xpads=[8],
        ypads=[0.4],
        margins=[10,2,4,1],
    ):

        if len(xpans) != nxpan:
            xpans = np.full((nxpan), xpans[0])
        if len(ypans) != nypan:
            ypans = np.full((nypan), ypans[0])
        if len(xpads) != nxpan-1:
            xpads = np.full((nxpan-1), xpads[0])
        if len(ypads) != nypan-1:
            ypads = np.full((nypan-1), ypads[0])
        
        xpans = np.array(xpans)
        ypans = np.array(ypans)
        xpads = np.array(xpads)
        ypads = np.array(ypads)

        xpansize = pansize[0]*xpans/xpans[panid[0]]
        ypansize = pansize[1]*ypans/ypans[panid[1]]

        abs_xchsz, abs_ychsz = self.abs_charsize

        # Calc panel size.
        abs_xspace = np.array([margins[0],margins[2]])*abs_xchsz
        abs_yspace = np.array([margins[3],margins[1]])*abs_ychsz
        if len(xpads) != 0: abs_xspace = np.insert(abs_xspace, 1, xpads*abs_xchsz)
        if len(ypads) != 0: abs_yspace = np.insert(abs_yspace, 1, ypads*abs_ychsz)
        region_xsize = np.sum(xpansize)+np.sum(abs_xspace)
        region_ysize = np.sum(ypansize)+np.sum(abs_yspace)

        abs_pos = np.empty((4,nxpan,nypan))
        for ypan_id in range(nypan):
            if ypan_id == 0:
                y0 = region_ysize
            else:
                y0 = abs_pos[1,0,ypan_id-1]
            for xpan_id in range(nxpan):
                if xpan_id == 0:
                    x0 = 0
                else:
                    x0 = abs_pos[2,xpan_id-1,0]
                abs_pos[0,xpan_id,ypan_id] = x0+abs_xspace[xpan_id]
                abs_pos[3,xpan_id,ypan_id] = y0-abs_yspace[ypan_id]
                abs_pos[2,xpan_id,ypan_id] = abs_pos[0,xpan_id,ypan_id]+xpansize[xpan_id]
                abs_pos[1,xpan_id,ypan_id] = abs_pos[3,xpan_id,ypan_id]-ypansize[ypan_id]

        self.panels = {
            'xspace': abs_xspace,
            'xspace': abs_xspace,
            'yspace': abs_yspace,
            'xpansize': xpansize,
            'ypansize': ypansize,
            'abs_pos': abs_pos,
            'xsize': region_xsize,
            'ysize': region_ysize,
        }


    def plot_scalar(self,
        ax, var,
        colors='k',
        labels='',
    ):

        x = smg.get_time(var)
        y = smg.get_data(var)
        ax.plot(x,y, color=colors, label=labels, linewidth=default_linewidth)

    
    def plot_vector(self,
        ax, var,
        colors=list('rgb'),
        labels=list('xyz'),
    ):

        x = smg.get_time(var)
        y = smg.get_data(var)
        ndim = y.shape[1]
        for i in range(ndim):
            ax.plot(x,y[:,i], color=colors[i], label=labels[i], linewidth=default_linewidth)

    def plot_combo_vector(self,
        ax, var,
        colors=[],
        labels=[],
    ):

        vars = smg.get_data(var)
        nvar = len(vars)
        if len(colors) != nvar:
            if nvar == 1:
                colors = ['k']
            elif nvar == 2:
                colors = list('rb')
            elif nvar < 7:
                colors = list('rgbcmyk')[0:nvar-1]
            else:
                colors = get_color(nvar)
        
        if len(labels) != nvar:
            labels = vars.copy()
            for i in range(nvar):
                short_name = smg.get_setting(vars[i], 'short_name')
                if short_name is not None:
                    labels[i] = short_name
        

        x = smg.get_time(vars[0])
        for var, color, label in zip(vars, colors, labels):
            y = smg.get_data(var)
            ax.plot(x,y, color=color, label=label, linewidth=default_linewidth)


        self.add_legend(ax)

        settings = smg.get_setting(vars[0])
        unit = settings.get('unit', None)
        ytitle = make_title_from_unit(unit)
        ax.set_ylabel(ytitle)

        ylog = settings.get('ylog', False)
        if ylog is True:
            ax.set_yscale('log')
        yscale = settings.get('yscale', None)
        if yscale is not None:
            ax.set_yscale(yscale)



    def plot_scalar_with_color(self,
        ax, var,
        colors=[],
        labels=[],
    ):

        vars = smg.get_data(var)
        scalar_var = vars[0]
        color_var = vars[1]

        x = smg.get_time(scalar_var)
        y = smg.get_data(scalar_var)
        z = smg.get_data(color_var)
        z_setting = smg.get_setting(color_var)

        zlog = z_setting.get('ylog', False)
        z_unit = z_setting.get('unit', '')
        ztitle = make_title_from_unit(z_unit)
        if zlog is True:
            z = np.log10(z)
            ztitle = 'Log$_{10}$\n'+ztitle


        # Draw the color-coded line.
        color_table = smg.get_setting(var, 'color_table')
        if color_table is None: color_table = 'jet'
        sc = ax.scatter(x,y, c=z, cmap=color_table, s=default_linewidth)

        # Add ytitle and adjust y-scale.
        settings = smg.get_setting(scalar_var)
        unit = settings.get('unit', None)
        ytitle = make_title_from_unit(unit)
        short_name = settings.get('short_name', '')
        ytitle = short_name+' '+ytitle
        ax.set_ylabel(ytitle)

        ylog = settings.get('ylog', False)
        if ylog is True:
            ax.set_yscale('log')
        yscale = settings.get('yscale', None)
        if yscale is not None:
            ax.set_yscale(yscale)
        yrange = settings.get('yrange', None)
        if yrange is not None:
            ax.set_ylim(yrange[0], yrange[1])
        
        # Add colorbar.
        pos = ax.get_position()
        xchsz, _ = self.abs_charsize
        fig_xsz, _ = self.size
        xpad = xchsz/fig_xsz
        x0 = pos.x1+xpad
        width = xchsz/fig_xsz
        cbpos = [x0,pos.y0,width,pos.y1-pos.y0]
        cax = self.fig.add_axes(cbpos)
        cb = self.fig.colorbar(sc, cax=cax)
        cb.set_label(ztitle)
        zrange = settings.get('zrange', None)
        if zrange is not None:
            cb.set_clim(zrange[0], zrange[1])


    def plot_flux(self,
        ax, var,
        colors=[],
        labels=[],
    ):

        x = smg.get_time(var)
        y = smg.get_data(var)

        flux_index = smg.get_setting(var, 'flux_index').astype(int)
        if flux_index is not None:
            y = y[:,flux_index]
            labels = np.array(labels)[flux_index]
            colors = np.array(colors)[flux_index]


        ndim = y.shape[1]
        for i in range(ndim):
            ax.plot(x,y[:,i], color=colors[i], label=labels[i], linewidth=default_linewidth)
    
    def plot_combo_scalar(self,
        ax, var,
        colors=list('rgb'),
        labels=list('xyz'),
    ):

        vars = smg.get_data(var)
        x = smg.get_time(vars[0])
        y = smg.get_data(vars[0])
        ax.plot(x,y, color=colors[0], label=labels[0], linewidth=default_linewidth)
        ax.tick_params(axis='y', which='major', left=True)
        ax.tick_params(axis='y', which='minor', left=True)
        ax.tick_params(axis='y', which='major', right=False)
        ax.tick_params(axis='y', which='minor', right=False)
        ax.spines['right'].set_visible(False)

        ax2 = ax.twinx()
        x = smg.get_time(vars[1])
        y = smg.get_data(vars[1])
        ax2.plot(x,y, color=colors[1], label=labels[1], linewidth=default_linewidth)
        ax2.minorticks_on()
        ax2.tick_params(axis='y', which='major', left=False)
        ax2.tick_params(axis='y', which='minor', left=False)
        ax2.tick_params(axis='y', which='major', right=True)
        ax2.tick_params(axis='y', which='minor', right=True)
        ax2.spines['right'].set_color(colors[1])
        [t.set_color(colors[1]) for t in ax2.yaxis.get_ticklabels()]

        

        for the_var, the_ax, color in zip(vars,[ax,ax2], colors):
            settings = smg.get_setting(the_var)
            unit = settings.get('unit', None)
            ytitle = make_title_from_unit(unit)
            short_name = settings.get('short_name', '')
            ytitle = short_name+' '+ytitle
            the_ax.set_ylabel(ytitle, color=color)

            ylog = settings.get('ylog', False)
            if ylog is True:
                the_ax.set_yscale('log')
            yscale = settings.get('yscale', None)
            if yscale is not None:
                the_ax.set_yscale(yscale)

        
    
    def add_legend(self, ax,):
        
        lg = ax.legend(
            bbox_to_anchor=(1,0.5),
            loc='center left',
            frameon=False,
            handlelength=0,
            handletextpad=0,
        )
        for text, line in zip(lg.get_texts(),ax.get_lines()):
            text.set_color(line.get_color())


    def plot(self, vars=[], xrange=None, fig_labels=[],
        margins=[8,2,8,1],
        ypans=[],
        xstep=None,
        xticks=[],
        xminor=None,
    ):


        nvar = len(vars)
        if nvar == 0: return None


        if xrange is None:
            var = vars[-1]
            display_type = smg.get_setting(var, 'display_type')
            if display_type in high_level_vars:
                the_var = smg.get_data(var)[0]
                x = smg.get_time(the_var)
            else:
                x = smg.get_time(var)
            xrange = [min(x),max(x)]
        else:
            if type(xrange[0]) is str:
                xrange = smg.prepare_time_range(xrange)
            
        
        if len(fig_labels) != nvar:
            fig_labels = [chr(x+97)+')' for x in range(nvar)]

        nypan = nvar
        if len(ypans) != nypan: ypans = np.full(nypan,1)
        axes = (self.panel_pos(nypan=nypan, margins=margins, ypans=ypans))[0]
        for var, ax, fl in zip(vars, axes, fig_labels):
            self.plot_single_var(ax, var, xrange=xrange, fig_label=fl)


        # xticks.
        if xstep is None:
            xstep = get_xstep(xrange)
        if len(xticks) == 0:
            xticks = math.make_bins(xrange, xstep, inner=True)

        
        # Set xrange and xticks, xminor.
        for ax in axes:
            ax.set_xlim(xrange)
            ax.set_xticks(xticks)
            if xminor is not None:
                ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(xminor))

        # Convert unix time to string.
        ax = axes[-1]
        ax.xaxis.set_major_formatter(slib_time_formatter)

        # Some xticks are not shown because they are out of xrange.
        xticks = ax.get_xticks()
        labels = np.array([label.get_text() for label in ax.get_xticklabels()])
        label_index = (np.where(np.logical_and(xticks>=xrange[0], xticks<=xrange[1])))[0]

        # For xticks in xrange, remove duplicate dates.
        the_labels = labels[label_index]
        nlabel = len(the_labels)
        time_labels = list()
        date_labels = list()
        for i in range(nlabel):
            tmp = the_labels[i].split('\n')
            time_labels.append(tmp[0])
            date_labels.append(tmp[1])
        time_labels = np.array(time_labels)
        date_labels = np.array(date_labels)
        _, uniq_index = np.unique(date_labels, return_index=True)
        mask = np.ones(nlabel, dtype=bool)
        mask[uniq_index] = False
        date_labels[np.where(mask == True)] = ''

        # Set the new xlabels.
        for i in range(nlabel):
            the_labels[i] = time_labels[i]+'\n'+date_labels[i]
        labels[label_index] = the_labels
        ax.set_xticklabels(labels)

        # Add a xlabel title.
        xlabel_title = 'UT\nDate'
        pos = ax.get_position()
        xchsz, _ = self.abs_charsize
        fig_xsz, _ = self.size
        xchsz = xchsz/fig_xsz
        rect = [pos.x0-xchsz*default_fig_label_offset,pos.y0,0,pos.y1-pos.y0]
        ax_label = self.fig.add_axes(rect)
        # Remove the axis line.
        for t in ['top','bottom','right','left']:
            ax_label.spines[t].set_visible(False)
        # Remove y axis tick label and marker.
        ax_label.yaxis.set_ticklabels([])
        ax_label.tick_params(left=False)
        ax_label.tick_params(right=False)
        ax_label.tick_params(top=False)
        ax_label.tick_params(bottom=False)

        labels = [xlabel_title]
        for i in range(1,len(ax_label.get_xticklabels())): labels.append('')
        ax_label.set_xticklabels(labels, ha='left')

        """
        # One way is to manually print the tick labels.
        label = ax.get_xticklabels()[label_index[0]]
        xlabel_title = 'UT\nDate'
        xchsz, ychsz = self.abs_charsize
        fig_size = self.size
        xchsz /= fig_size[0]
        ychsz /= fig_size[1]
        ax_pos = ax.get_position()
        x = ax_pos.x0-default_fig_label_offset*xchsz
        y = ax_pos.y0-0.5*ychsz
        ax.text(x,y, xlabel_title, va='top', ha='left', transform=self.fig.transFigure)
        """
        

    
    def plot_single_var(self, ax, var, xrange=None, fig_label=None):

        settings = smg.get_setting(var)

        display_type = settings.get('display_type', 'scalar')
        short_name = settings.get('short_name','')
    
        if display_type == 'scalar':
            labels = short_name
            colors = settings.get('colors','k')
        elif display_type == 'vector':
            coord = settings.get('coord', '').upper()
            coord_labels = settings.get('coord_labels', list('xyz'))
            labels = [coord+' '+short_name+'$_{'+x+'}$' for x in coord_labels]
            colors = settings.get('colors', list('rgb'))
        elif display_type == 'flux':
            energy_var = settings['energy_var']
            energys = smg.get_data(energy_var)
            energy_unit = settings.get('energy_unit','')
            labels = [str(np.int(x))+' '+energy_unit for x in energys]
            color_table = settings.get('color_table', 'Blues')
            colors = get_color(len(energys), color_table=color_table)
        elif display_type == 'combo_scalar':
            colors = settings.get('colors',['k','r'])
            labels = settings.get('labels',[])
            if len(labels) == 0:
                labels = smg.get_data(var)
                if labels is None:
                    raise Exception('No combo_vars ...')
        elif display_type == 'combo_vector':
            colors = settings.get('colors', [])
            labels = settings.get('labels', [])
        else:
            colors = 'k'
            labels = var
        
        if display_type == 'scalar':
            self.plot_scalar(ax, var, colors=colors, labels=labels)
        elif display_type == 'vector':
            self.plot_vector(ax, var, colors=colors, labels=labels)
        elif display_type == 'flux':
            self.plot_flux(ax, var, colors=colors, labels=labels)
        elif display_type == 'combo_scalar':
            self.plot_combo_scalar(ax, var, colors=colors, labels=labels)
        elif display_type == 'scalar_with_color':
            self.plot_scalar_with_color(ax, var)
        elif display_type == 'combo_vector':
            self.plot_combo_vector(ax, var, colors=colors, labels=labels)
        else:
            try:
                self.plot_scalar(ax, var, colors=colors, labels=labels)
            except:
                pass
        
        if display_type not in high_level_vars:
            self.add_legend(ax)

            unit = settings.get('unit', None)
            ytitle = make_title_from_unit(unit)
            ax.set_ylabel(ytitle)

            ylog = settings.get('ylog', False)
            if ylog is True:
                ax.set_yscale('log')
            yscale = settings.get('yscale', None)
            if yscale is not None:
                ax.set_yscale(yscale)


        if xrange is not None:
            ax.set_xlim(xrange)

        
        if fig_label is not None:
            self.add_fig_label(ax, fig_label)


    def add_fig_label(self, ax, fig_label, offset=None):

        if fig_label is None: fig_label = 'a)'
        if offset is None: offset = default_fig_label_offset

        xchsz, ychsz = self.abs_charsize
        fig_size = self.size
        xchsz /= fig_size[0]
        ychsz /= fig_size[1]
        ax_pos = ax.get_position()
        x = ax_pos.x0-default_fig_label_offset*xchsz
        y = ax_pos.y1
        ax.text(x,y, fig_label+offset*' ', va='top', ha='left', transform=self.fig.transFigure)

        




def _get_abs_chsz():
    fig = plt.figure(figsize=(1,1))
    fig_size = fig.get_size_inches()

    ax = fig.add_axes([0,0,1,1])
    x = 'x'
    txt = ax.text(0.5,0.5,x)
    bbox = txt.get_window_extent()
    bbox_norm = bbox.transformed(fig.transFigure.inverted())

    # The x and y sizes in inch of a typical character.
    abs_xchsz = (bbox_norm.x1-bbox_norm.x0)*fig_size[0]
    abs_ychsz = (bbox_norm.y1-bbox_norm.y0)*fig_size[1]

    plt.close(fig)

    return abs_xchsz, abs_ychsz
    

def get_color(
    ncolor,
    color_table='jet',
    color_range=[0.3,0.9],
    reverse_color=False):

    cmap = plt.get_cmap(color_table)
    color_bottom = color_range[0]
    color_top = color_range[1]
    colors = [cmap(x) for x in np.linspace(color_bottom,color_top, ncolor)]
    if reverse_color is True: colors.reverse()
    return colors


def get_xstep(
    xrange,
    optimal_nxtick=5,
):

    duration = xrange[1]-xrange[0]
    xsteps = np.array([1,2,3,4,5,
        20,30,60,120,300,600,1200,1800,
        3600,2*3600,6*3600,12*3600,24*3600])

    nx = duration/xsteps
    index = np.where(np.logical_and(nx>=1,nx<=optimal_nxtick))
    if len(index) == 0:
        return duration/(optimal_nxtick-1)

    return min(xsteps[index])
