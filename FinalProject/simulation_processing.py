import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.axes_grid import inset_locator, make_axes_locatable

import os
import fnmatch
import numpy as np
import scipy.ndimage as ndi
import pandas as pd
import palettable as pbl
import h5py


cmap7 = pbl.colorbrewer.get_map('Set1', 'Qualitative', 7)
cmap11 = pbl.colorbrewer.get_map('Paired', 'Qualitative', 12)
c11s = cmap11.hex_colors
c11s = c11s[1::2] + c11s[::2] # unpair them

mpl.rc('image', cmap='viridis', interpolation='nearest')
mpl.rc('font', family='STIXGeneral')
mpl.rc('legend', fancybox=False, numpoints=1, markerscale=1.5, borderaxespad=0.5, fontsize=16)
mpl.rc('figure', figsize=(8,8))
mpl.rc('axes', linewidth=1.5, edgecolor='k', labelsize=22, grid=False, axisbelow=True,
        prop_cycle= mpl.cycler(color=c11s))
mpl.rc('grid', linewidth=1)
mpl.rc('ytick.major', size=5, width=1.5, pad=8)
mpl.rc('xtick.major', size=5, width=1.5, pad=8)
mpl.rc('xtick', labelsize=18)
mpl.rc('ytick', labelsize=18)
mpl.rc('lines', linewidth=2)

def get_pos_finite(arr):
    a = arr[np.isfinite(arr)]
    return a[a>0]

##############################################################

working_dir = "/Users/thanasi/ipynb/classes/Nanophotonics (18.369)/FinalProject/out/"
os.chdir(working_dir)

structures = ['air', 'straight', 'holes', 'bumps']

eps_lo = 1
eps_hi = 12
omega0 = 0.25
lmbda0 = 2*np.pi / omega0
lmbda_hi = lmbda0 / eps_hi
resolution = 30


class Results(object):
    pass

def get_epsilon(s, subdir):

    fn = './%s/%s/eps.h5' % (s,subdir)

    with h5py.File(fn, 'r') as eps_file:
        epsilon = eps_file["eps"].value.T
    return epsilon

def get_fluxes(s, subdir, scale=1):

    filename = './%s/%s/fluxes.out' % (s, subdir)

    fluxes = pd.read_csv(filename,
                     header=None, index_col=0, usecols=[1,2,3,4,5],
                     names=["freq", "top", "right","bottom","left"])

    fluxes = fluxes[0:0.5]

    # switch the sign of the fluxes to represent outward flux
    fluxes["bottom"] *= scale
    fluxes["left"] *= scale

    return fluxes

def get_ldos(s, subdir):

    fn = './%s/%s/ldos.out' % (s,subdir)

    ldos = pd.read_csv(fn,
                   header=None, index_col=0, usecols=[1,2],
                  names=['freq', 'ldos'])
    ldos = ldos[0:0.5]

    return ldos

def get_bands_re(s, subdir):

    fn = './%s/%s/fre.out' % (s,subdir)

    with open(fn, 'r') as infile:
        l = infile.readline()
        N = l.count(",")

    freqs_re = pd.read_csv(fn, header=None, index_col=0, usecols=range(2,N))

    return freqs_re

def get_kpwr(s):

    out_dir = './%s/bands/' % s
    kfolders = os.listdir(out_dir)
    kfolders = fnmatch.filter(kfolders, 'k*')
    parse_k = lambda x: float(x[1:])
    ks = list(map(parse_k, kfolders))

    omegas = pd.read_csv(out_dir+kfolders[0]+'/fluxes.out',
                     header=None,  usecols=[1],
                     names=["freq"])["freq"].values

    kpwr = pd.Panel(0,items=ks, major_axis=omegas, minor_axis=['top', 'right', 'bottom', 'left'], dtype=np.float32)
    kpwr.items.set_names('k', inplace=True)
    kpwr.major_axis.set_names('freq', inplace=True)

    for k, kf in zip(ks,kfolders):
        pwr = pd.read_csv(out_dir + kf + '/fluxes.out',
                            header=None, index_col=0, usecols=[1,2,3,4,5],
                             names=['freq', 'top','right','bottom','left'])

        kpwr.loc[k,:,:] = pwr.values

    return kpwr

################################################################
# functions for radiation simulations
################################################################

def plot_radiation_data(res):

    sx = 16
    sy = 8
    X_max = sx // 2
    X_min = - X_max
    Y_max = sy //2
    Y_min =  - Y_max

    plt.figure(res["fig"].number)

    gs1 = gridspec.GridSpec(nrows=2,ncols=1)
    gs1.update(left=0.05, right=0.65, wspace=0.15)

    ax1 = plt.subplot(gs1[0,0])
    ax2 = plt.subplot(gs1[1,0], sharex=ax1)

    gs2 = gridspec.GridSpec(nrows=3, ncols=1)
    gs2.update(left=0.67, right=0.95, wspace=0.01)
    ax3 = plt.subplot(gs2[0,0])
    ax4 = plt.subplot(gs2[1,0])
    ax5 = plt.subplot(gs2[2,0])

    im_axs = {"straight": ax3, "holes": ax4, "bumps": ax5}

    for s in structures:


        x1 = res[s].flux_ratio[np.pi/sx:0.5].index.values
        y1 = res[s].flux_ratio[np.pi/sx:0.5].values
        ax1.plot(x1,y1, lw=3, label=s)

        x2 = res[s].ldos[np.pi/sx:0.5].index.values
        y2 = res[s].ldos[np.pi/sx:0.5].values
        ax2.plot(x2,y2, lw=3, label=s)

        if s is not 'air':
            i = structures.index(s)
            a = im_axs[s]
            a.imshow(res[s].epsilon, extent=(X_min,X_max, Y_min, Y_max), cmap=plt.cm.gray)
            a.contour(res[s].epsilon, [5], extent=(X_min, X_max, Y_min, Y_max), colors=c11s[i], linewidths=2)


    for s,a in im_axs.items():
        a.set_aspect("equal")
        plt.setp(a.xaxis, visible=False)
        plt.setp(a.yaxis, visible=False)

    ax1.set_ylabel("Radiation Efficiency")
    ax2.set_ylabel("LDOS/"r"$\varepsilon_{hi}$")
    ax2.set_xlabel("$\omega a / (2 \pi c)$")


    ax1.set_ylim(0,1)
    ax1.set_xlim(np.pi/sx,0.5)
    ax2.set_ylim(0,1)

    plt.setp(ax1.get_xticklabels(), visible=False)
    ax2.legend(loc=2)


################################################################
# functions for multi-k band structure
################################################################

def build_composite_band_plot(res, res0):

    sx = 1
    sy = 8

    X_min = - sx / 2
    X_max = sx / 2
    Y_min = -sy / 2
    Y_max = sy / 2

    fig = plt.figure()
    gs1 = mpl.gridspec.GridSpec(1,1)
    gs1.update(left=0.05, right=0.71, bottom=0.05, top=0.71)
    gs2 = mpl.gridspec.GridSpec(1,1)
    gs2.update(left=0.79, right=0.95, bottom=0.05, top=0.71)

    ax1 = plt.subplot(gs1[:,:])
    ax2 = plt.subplot(gs2[:,:], sharey=ax1)
    ax3 = ax2.twiny()

    plt.setp(ax2.get_yticklabels(), visible=False)

    # ratio.plot(ax=ax2, lw=3)
    r = res0.flux_ratio[0.15:0.5]
    rx = r.values
    ry = r.index
    ax2.plot(rx, ry, 'k', lw=3)

    ax2.set_xticks([0,0.5,1])
    ax2.set_xlim(0,1)

    c3 = cmap7.mpl_colors[0]
    l = res0.ldos[0.15:0.5]
    lx = l.values
    ly = l.index

    ax3.plot(lx, ly, c=c3, lw=3)
    ax3.set_xlim(0,1)
    ax3.set_xticks([0,1])
    ax3.set_xlabel("LDOS/"r"$\varepsilon_{hi}$")

    for obj in ax3.get_xticklabels() + [ax3.spines['top'], ax3.xaxis.label] + ax3.get_xticklines():
        obj.set_color(c3)
        obj.set_zorder(2)

    ax2.spines['top'].set_visible(False)
    ax2.set_xticks([0,1])
    ax2.set_xlabel("$P_{rad} / P_0$")

    ax1.set_xlabel("$k_x a / (2 \pi)$")
    ax1.set_ylabel("$\omega a / (2 \pi c)$")
    ax1.set_xlim(0,0.5)
    ax1.set_ylim(0,0.5)
    ax1.set_aspect('equal')
    ax1.set_autoscale_on(False)

    # add an inset image of epsilon
    a = inset_locator.inset_axes(ax1, height=1.8, width=0.225, loc=8,
                                 bbox_to_anchor=(0.9, 0.01), bbox_transform=ax1.transAxes)
    a.imshow(res.epsilon, extent=(X_min,X_max, Y_min, Y_max), cmap=plt.cm.gray_r)

    a.set_aspect("equal")

    for s in [a.spines["right"], a.spines["left"]]:
        s.set_linestyle("--")


    plt.setp(a.xaxis, visible=False)
    plt.setp(a.yaxis, visible=False)

    return fig

def plot_band_structures(res, res0):

    fig = build_composite_band_plot(res, res0)

    ax = fig.get_axes()[0]

    k0 = [0,0.5]
    ax.plot(k0,k0,c='k')
    ax.fill_betweenx(k0, k0, facecolor='#cccccc', zorder=-1)

    x1 = res.freqs_re.index.values
    y1 = res.freqs_re.values
    ax.plot(x1, y1, c='k', marker='o', linestyle='')

    return fig

def plot_omega_k_power(res, res0, norm=None):

    fig = build_composite_band_plot(res, res0)
    ax = fig.get_axes()[0]

    gs3 = mpl.gridspec.GridSpec(1,1)
    gs3.update(left=0.05, right=0.71, bottom=0.72, top=0.74)

    cax = plt.subplot(gs3[:,:], )

    im = res.kpwr.sum(2).values

    # make the arrays square
    si, sj = im.shape
    I, J = np.mgrid[:si, :sj-1:0.25]
    I = np.floor(I).astype(np.uint)
    J = np.floor(J).astype(np.uint)

    im = im[I,J]

    vmin = 0
    vmax = 2

    if norm is not None:
        norm = norm[I,J]

        im /= norm
        vmin = -1
        vmax = 3

    # get rid of data outside of the light cone
    im *= np.tril(im)

    i0 = ax.imshow(np.log10(im), extent=(0,0.5,0.5,0),
                    cmap=plt.cm.viridis, vmin=vmin, vmax=vmax,
                    interpolation='nearest')

    plt.colorbar(i0, cax=cax, orientation='horizontal', ticks=[vmin, vmax])
    cax.xaxis.set_label_position('top')
    cax.xaxis.set_ticks_position('top')

    if norm is not None:
        cax.set_xlabel("Radiated Power rel. to air (log scale)", labelpad=-10, fontdict=dict(fontsize=14))
    else:
        cax.set_xlabel("Radiated Power (log scale)", labelpad=-10, fontdict=dict(fontsize=14))

    k0 = [0,0.5]
    ax.plot(k0,k0,c='k')
    # ax.fill_betweenx([0,0.5], [0,0.5], 0.5, facecolor='#000000')

    return fig



################################################################
# functions that put together data for different geometries
################################################################
def output_radiation_data(save=True):

    res = {"fig" : plt.figure(figsize=(16,8))}

    for s in structures:

        if s is "air":
            eps_max = eps_lo
        else:
            eps_max = eps_hi

        r = Results()
        r.epsilon = get_epsilon(s, 'radiation')
        r.ldos = get_ldos(s, 'radiation') / eps_max
        r.fluxes = get_fluxes(s, 'radiation', -1) # -1 adjusts bottom and left fluxes so that they are outward-oriented

        r.flux_ratio = (r.fluxes["top"] + r.fluxes["bottom"]) / r.fluxes.sum(axis=1)

        res[s] = r

    plot_radiation_data(res)

    if save:
        res["fig"].savefig("./fig/all.radiation.pdf", facecolor='none', bbox_inches='tight')

    return res


def output_band_diagram(res0, structs = structures, save=True):

    res = {}

    for s in structs:

        r = Results()
        r.epsilon = get_epsilon(s, 'bands/multi-k')
        r.freqs_re = get_bands_re(s, 'bands/multi-k')

        r.fig = plot_band_structures(r,res0[s])

        if save:
            r.fig.savefig("./fig/%s.bands.pdf" % s, facecolor='none', bbox_inches='tight')

        res[s] = r

    return res

def output_omega_k_power(res0, structs = structures, save=True, norm=False):

    res = {}

    for s in structs:

        r = Results()
        r.epsilon = get_epsilon(s, 'bands/multi-k')
        r.kpwr = get_kpwr(s)

        if norm and ("air" in res.keys()):
            nrm = res["air"].kpwr.sum(axis=2).values
        else:
            nrm = None

        r.fig = plot_omega_k_power(r, res0[s], norm=nrm)
        if save:
            r.fig.savefig("./fig/%s.omega_k_power.pdf" % s, facecolor='none', bbox_inches='tight')

        res[s] = r

    return res