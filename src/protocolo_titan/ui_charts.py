from __future__ import annotations

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import pandas as pd


def _dark_axes(fig, ax):
    fig.patch.set_facecolor('#091426')
    ax.set_facecolor('#0E1B2E')
    for spine in ax.spines.values():
        spine.set_color('#2D4060')
    ax.tick_params(colors='#C7D5F2')
    ax.xaxis.label.set_color('#C7D5F2')
    ax.yaxis.label.set_color('#C7D5F2')
    ax.title.set_color('#F2F7FF')
    ax.grid(True, color='#1D3352', alpha=0.45, linewidth=0.8)
    return fig, ax


def figure_timeslot_signal(trace: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    _dark_axes(fig, ax)
    x = trace['time_us'].to_numpy()
    y = trace['envelope_normalized'].to_numpy()
    timeslot_us = float(x.max()) if len(x) else 0.0
    total_bits = 156.25
    burst_data_end = timeslot_us * (61.0 / total_bits) if timeslot_us else 0.0
    training_end = timeslot_us * (87.0 / total_bits) if timeslot_us else 0.0
    y_max = float(y.max()) if len(y) else 1.0
    ax.plot(x, y, color='#46C6FF', linewidth=1.8)
    ax.axvspan(0, burst_data_end, color='#123A5E', alpha=0.25)
    ax.axvspan(burst_data_end, training_end, color='#1B5D74', alpha=0.22)
    ax.axvspan(training_end, timeslot_us, color='#2E4E6F', alpha=0.22)
    ax.text(timeslot_us * 0.16, y_max * 0.96, 'DATA + TAIL', color='#AFC4E8', fontsize=8, fontweight='bold')
    ax.text(timeslot_us * 0.48, y_max * 0.96, 'TRAINING (26 bits)', color='#AFC4E8', fontsize=8, fontweight='bold')
    ax.text(timeslot_us * 0.82, y_max * 0.96, 'DATA + GUARD', color='#AFC4E8', fontsize=8, fontweight='bold')
    ax.set_title(f'ANÁLISIS TEMPORAL DE LA VARIACIÓN DE SEÑAL ({timeslot_us:.0f} µs)', loc='left', fontsize=13, fontweight='bold')
    ax.set_xlabel('TIME (µs)')
    ax.set_ylabel('AMP. NORM.')
    ax.set_xlim(0, timeslot_us)
    ax.axhline(1.0, linestyle='--', color='#7ED7FF', alpha=0.5)
    return fig


def figure_noise(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    _dark_axes(fig, ax)
    ax.plot(df['rbw_khz'], df['noise_floor_dbm'], color='#46C6FF', marker='o', linewidth=2)
    if 'danl_dbm' in df:
        ax.plot(df['rbw_khz'], df['danl_dbm'], color='#FFD166', marker='s', linewidth=1.6)
    ax.set_xscale('log')
    ax.set_title('ANÁLISIS DE ESPECTRO Y RUIDO', loc='left', fontsize=13, fontweight='bold')
    ax.set_xlabel('RBW (kHz)')
    ax.set_ylabel('Nivel (dBm)')
    if 'danl_dbm' in df:
        ax.legend(['Ruido térmico + NF', 'DANL corregido'], facecolor='#0E1B2E', edgecolor='#2D4060', labelcolor='#DDE9FF')
    return fig


def figure_cluster_map(cluster_size: int, cell_radius_km: float):
    fig, ax = plt.subplots(figsize=(8, 7))
    _dark_axes(fig, ax)
    ax.set_title(f'MAPEO DE CLÚSTER (N={cluster_size})', loc='left', fontsize=13, fontweight='bold')

    if cluster_size != 4:
        ax.text(
            0.5,
            0.56,
            'Visualización geométrica disponible\nsolo para clúster N=4',
            ha='center',
            va='center',
            color='#F2F7FF',
            fontsize=16,
            fontweight='bold',
            transform=ax.transAxes,
        )
        ax.text(
            0.5,
            0.38,
            f'Configuración actual: N={cluster_size}, R={cell_radius_km:.1f} km',
            ha='center',
            va='center',
            color='#C7D5F2',
            fontsize=11,
            transform=ax.transAxes,
        )
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

    # pattern of repeating 4-cell cluster across a hex layout
    cell_colors = {
        'A': '#35E1E8',
        'B': '#2B8CFF',
        'C': '#3F6ED8',
        'D': '#6BB7D8',
    }
    labels = [
        (-1, 1, 'A'), (0, 1, 'B'), (1, 1, 'D'),
        (-1.5, 0, 'C'), (-0.5, 0, 'A'), (0.5, 0, 'B'), (1.5, 0, 'D'),
        (-1, -1, 'C'), (0, -1, 'D'), (1, -1, 'B'),
        (-0.5, 2, 'D'), (0.5, 2, 'C'),
        (-0.5, -2, 'B'), (0.5, -2, 'A')
    ]

    r = 0.55
    for x, y, lab in labels:
        hexagon = RegularPolygon((x, y), numVertices=6, radius=r, orientation=np.radians(30),
                                 facecolor=cell_colors[lab], edgecolor='#A6F7FF', alpha=0.85, linewidth=1.2)
        ax.add_patch(hexagon)
        ax.text(x, y, f'Cell {lab}', ha='center', va='center', color='#08213A', fontsize=9, fontweight='bold')

    ax.text(1.95, 1.95, f'Cell Radius\nR={cell_radius_km:.1f} km', color='#C7D5F2', fontsize=9)
    ax.text(1.95, -1.9, f'Reuse pattern\nN={cluster_size}', color='#C7D5F2', fontsize=9)
    ax.set_xlim(-2.4, 2.8)
    ax.set_ylim(-2.6, 2.6)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    return fig


def figure_carrier_distribution(plan_df: pd.DataFrame, logical_df: pd.DataFrame, total_carriers: int):
    bcch = logical_df[logical_df['carrier_role'].str.contains('BCCH')].groupby('cell').size()
    tch = logical_df[logical_df['carrier_role'].str.contains('TCH')].groupby('cell').size()
    cells = plan_df['cell'].tolist()
    bcch_vals = [int(bcch.get(c, 0)) for c in cells]
    tch_vals = [int(tch.get(c, 0)) for c in cells]

    fig, ax = plt.subplots(figsize=(6.3, 3.3))
    _dark_axes(fig, ax)
    ax.bar(cells, bcch_vals, label='BCCH', color='#7EE6FF')
    ax.bar(cells, tch_vals, bottom=bcch_vals, label='TCH', color='#278DFF')
    ax.set_title(f'DISTRIBUCIÓN DE PORTADORAS ({total_carriers} CH)', loc='left', fontsize=12, fontweight='bold')
    ax.set_xlabel('Cell ID')
    ax.set_ylabel('Número de portadoras')
    ax.legend(facecolor='#0E1B2E', edgecolor='#2D4060', labelcolor='#DDE9FF')
    return fig


def figure_cochannel_interference(plan_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(6.3, 3.3))
    _dark_axes(fig, ax)
    cells = plan_df['cell'].tolist()
    ci_db = plan_df['cochannel_ci_db'].to_numpy()
    ax.bar(cells, ci_db, color='#46C6FF')
    ax.axhline(9.0, color='#FFD166', linestyle='--', linewidth=1.3)
    ax.set_title('RELACIÓN C/I POR REUTILIZACIÓN', loc='left', fontsize=12, fontweight='bold')
    ax.set_xlabel('Cell ID')
    ax.set_ylabel('C/I (dB)')
    ax.legend(['Umbral GSM 9 dB', 'C/I calculada'], facecolor='#0E1B2E', edgecolor='#2D4060', labelcolor='#DDE9FF')
    return fig


def figure_spectrum_from_arfcns(logical_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    _dark_axes(fig, ax)

    logical = logical_df.sort_values('uplink_frequency_mhz').copy()
    logical['estimated_level_dbm'] = np.where(
        logical['carrier_role'].str.contains('BCCH'),
        -58.0,
        -68.0 + (logical['arfcn'].to_numpy() % 4) * 1.8,
    )
    bcch = logical[logical['carrier_role'].str.contains('BCCH')]
    tch = logical[logical['carrier_role'].str.contains('TCH')]

    ax.vlines(tch['uplink_frequency_mhz'], -110, tch['estimated_level_dbm'], color='#46C6FF', linewidth=2.2, alpha=0.9)
    ax.scatter(tch['uplink_frequency_mhz'], tch['estimated_level_dbm'], color='#46C6FF', s=26, zorder=3, label='TCH')
    ax.vlines(bcch['uplink_frequency_mhz'], -110, bcch['estimated_level_dbm'], color='#FFD166', linewidth=2.6, alpha=0.95)
    ax.scatter(bcch['uplink_frequency_mhz'], bcch['estimated_level_dbm'], color='#FFD166', s=36, zorder=4, label='BCCH')

    ax.set_ylim(-110, -40)
    ax.set_xlim(logical['uplink_frequency_mhz'].min() - 0.3, logical['uplink_frequency_mhz'].max() + 0.3)
    ax.set_xlabel('Frecuencia uplink (MHz)')
    ax.set_ylabel('Nivel estimado (dBm)')
    ax.set_title('PORTADORAS UPLINK GSM POR ARFCN', loc='left', fontsize=12, fontweight='bold')
    ax.legend(facecolor='#0E1B2E', edgecolor='#2D4060', labelcolor='#DDE9FF')
    return fig


def figure_small_camera_placeholder():
    # self-contained synthetic view resembling a live RF corridor panel
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    fig.patch.set_facecolor('#091426')
    ax.set_facecolor('#10243B')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    # sky and terrain
    ax.fill_between([0, 10], 10, 6.7, color='#92BFE6')
    ax.fill_between([0, 2.3, 4.8, 6.8, 10], [6.1, 6.8, 6.0, 6.5, 6.2], 0, color='#7FA772')
    # viaduct
    ax.plot([0.8, 9.2], [2.0, 3.3], color='#B7C7D9', linewidth=12, solid_capstyle='round')
    for p in [1.7, 3.2, 4.7, 6.2, 7.7, 9.0]:
        y = 1.8 + (p-0.8)*(1.3/8.4)
        ax.plot([p, p], [0.4, y], color='#CBD8E8', linewidth=3)
    # mast
    ax.plot([5.3, 5.3], [3.8, 7.1], color='#9AA9BA', linewidth=4)
    ax.plot([5.1, 5.5], [5.9, 5.9], color='#9AA9BA', linewidth=3)
    ax.plot([5.0, 5.6], [6.3, 6.3], color='#9AA9BA', linewidth=3)
    for r in [0.7, 1.2, 1.8]:
        circ = plt.Circle((5.3, 5.0), r, color='#55C8FF', fill=False, alpha=0.22, linewidth=1.4)
        ax.add_patch(circ)
    # train
    ax.plot([7.0, 8.8], [2.8, 3.05], color='#16324F', linewidth=16, solid_capstyle='round')
    ax.plot([7.1, 8.7], [2.95, 3.18], color='#E5F2FF', linewidth=2.2)
    return fig
