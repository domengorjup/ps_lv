"""
fourier_risanje.py — Pomožne funkcije za izris v fourier_vodic.ipynb.

Vsebuje eno funkcijo plot_* na primer iz notebooka. Matematično/
algoritmična vsebina (koeficient_cn, rfft_eno) ostaja v predlogi;
tukaj so le funkcije, ki skrijejo ponavljajočo se matplotlib kodo.
"""

import numpy as np
import matplotlib.pyplot as plt


# Osnovna gradnika za spektralne grafe

def ax_spekter(ax, freqs=None, y=None, *, title='', xlabel='Frekvenca [Hz]',
               ylabel='Amplituda', xlim=None, stem=True, color='C0', **kwargs):
    """Izris spektra (stem ali line) s standardnimi oznakami osi.

    Če sta freqs in y podana, nariše podatke; vedno nastavi oznake osi.
    stem=True  → stem plot (za redke diskretne koše / c_n)
    stem=False → line plot (za gost zvezni spekter)
    """
    if freqs is not None and y is not None:
        if stem:
            ax.stem(freqs, y, markerfmt=f'{color}o', linefmt=f'{color}-',
                    basefmt='k-', **kwargs)
        else:
            ax.plot(freqs, y, color=color, **kwargs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if xlim is not None:
        ax.set_xlim(xlim)


def ax_faza(ax, freqs=None, F_complex=None, *, title='Fazni spekter',
            xlim=None, **kwargs):
    """Izris faznega spektra (scatter) z standardnimi oznakami osi.

    Če sta freqs in F_complex podana, nariše podatke; vedno nastavi oznake osi.
    """
    if freqs is not None and F_complex is not None:
        ax.scatter(freqs, np.degrees(np.angle(F_complex)), s=4, color='C1',
                   **kwargs)
    ax.set_xlabel('Frekvenca [Hz]')
    ax.set_ylabel('Faza [°]')
    if title:
        ax.set_title(title)
    if xlim is not None:
        ax.set_xlim(xlim)



# Primer 1.1

def plot_cas_primerjava(t, referenca, signali, ref_label='referenca',
                        xlabel='Čas [s]', title=None):
    """Izris referenčnega signala (siva črt.) in serije signalov za primerjavo.

    signali: seznam parov (oznaka, signal_array)
    """
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(t, referenca, 'k--', alpha=0.3, label=ref_label)
    for oznaka, sig in signali:
        ax.plot(t, sig, label=oznaka)
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Amplituda')
    if title:
        ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    return fig, ax
