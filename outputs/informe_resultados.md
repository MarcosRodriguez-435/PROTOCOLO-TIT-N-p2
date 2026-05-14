# Informe de resultados — Protocolo Titán

## Resumen ejecutivo

El análisis confirma que, para GSM-900 y un timeslot de 577 µs, el escenario A sigue operando en fading lento tanto a 50 km/h como a 250 km/h, aunque el margen temporal cae desde 17.59 hasta 3.52.
En el escenario B, la planificación con N=4 reparte 24 portadoras en 6 portadoras por celda y obtiene C/I ≈ 13.80 dB, superando en 4.80 dB el umbral GSM de referencia.

## Metodología reproducible

1. Conversión de velocidades de km/h a m/s para el cálculo Doppler.
2. Cálculo de Doppler máximo con `f_d = v · f_c / c`.
3. Estimación del tiempo de coherencia con `T_c ≈ 0.423 / f_d` y comparación con el timeslot GSM.
4. Simulación docente de fading Rayleigh y Rician durante una ráfaga GSM.
5. Planificación celular con `D/R = sqrt(3N)` y estimación de `C/I ≈ (D/R)^n / 6`, con `n = 4`.
6. Evaluación instrumental del ruido integrado con `-174 + 10log10(RBW) + NF` y DANL aproximado corregido.

## Escenario A — Convoy de alta velocidad

| scenario                |   cell_radius_km |   speed_kmh |   speed_ms |   carrier_frequency_mhz |   max_doppler_hz |   coherence_time_ms |   gsm_timeslot_ms |   coherence_to_timeslot_ratio | stability_class             |
|:------------------------|-----------------:|------------:|-----------:|------------------------:|-----------------:|--------------------:|------------------:|------------------------------:|:----------------------------|
| A_convoy_alta_velocidad |                3 |          50 |    13.8889 |                     900 |          41.6667 |             10.152  |             0.577 |                      17.5945  | cuasiestatico               |
| A_convoy_alta_velocidad |                3 |         250 |    69.4444 |                     900 |         208.333  |              2.0304 |             0.577 |                       3.51889 | estable_con_margen_reducido |

Interpretación: el criterio principal es comparar el tiempo de coherencia con el timeslot GSM de 577 µs.

### Hallazgos clave

- A 50 km/h, `f_d = 41.67 Hz` y `T_c = 10.15 ms`, por lo que el canal se comporta como cuasiestático durante la ráfaga.
- A 250 km/h, `f_d = 208.33 Hz` y `T_c = 2.03 ms`; el enlace sigue siendo viable, pero con margen temporal claramente menor.
- Desde un punto de vista de ingeniería, este resultado justifica el uso cuidadoso de entrenamiento de ráfaga, ecualización y esquemas robustos de codificación/interleaving.

### Métricas de fading

| model    |   doppler_hz |   envelope_min |   envelope_max |   envelope_std |   relative_peak_to_peak |   speed_kmh |   coherence_time_ms | stability_class             |
|:---------|-------------:|---------------:|---------------:|---------------:|------------------------:|------------:|--------------------:|:----------------------------|
| rayleigh |      41.6667 |     0.00894961 |        3.32166 |       0.586993 |                3.31271  |          50 |             10.152  | cuasiestatico               |
| rician   |      41.6667 |     0.734056   |        1.25486 |       0.100871 |                0.5208   |          50 |             10.152  | cuasiestatico               |
| rayleigh |     208.333  |     0.145474   |        3.0415  |       0.453328 |                2.89602  |         250 |              2.0304 | estable_con_margen_reducido |
| rician   |     208.333  |     0.694197   |        1.2311  |       0.105082 |                0.536901 |         250 |              2.0304 | estable_con_margen_reducido |

## Escenario B — Campamento base

### Planificación de frecuencias

| scenario          | cell   |   cell_radius_km |   cluster_size_N |   total_carriers |   carriers_per_cell | arfcn_range   | arfcn_list             |   reuse_ratio_D_over_R |   reuse_distance_km |   first_tier_interferers |   path_loss_exponent |   cochannel_ci_linear |   cochannel_ci_db |   ci_margin_vs_gsm_db |
|:------------------|:-------|-----------------:|-----------------:|-----------------:|--------------------:|:--------------|:-----------------------|-----------------------:|--------------------:|-------------------------:|---------------------:|----------------------:|------------------:|----------------------:|
| B_campamento_base | A      |              1.5 |                4 |               24 |                   6 | 1-6           | 1, 2, 3, 4, 5, 6       |                 3.4641 |             5.19615 |                        6 |                    4 |                    24 |           13.8021 |               4.80211 |
| B_campamento_base | B      |              1.5 |                4 |               24 |                   6 | 7-12          | 7, 8, 9, 10, 11, 12    |                 3.4641 |             5.19615 |                        6 |                    4 |                    24 |           13.8021 |               4.80211 |
| B_campamento_base | C      |              1.5 |                4 |               24 |                   6 | 13-18         | 13, 14, 15, 16, 17, 18 |                 3.4641 |             5.19615 |                        6 |                    4 |                    24 |           13.8021 |               4.80211 |
| B_campamento_base | D      |              1.5 |                4 |               24 |                   6 | 19-24         | 19, 20, 21, 22, 23, 24 |                 3.4641 |             5.19615 |                        6 |                    4 |                    24 |           13.8021 |               4.80211 |

Interpretación: además de D/R y D, se incluye la relación co-canal C/I usando el modelo hexagonal aproximado C/I = (D/R)^n / 6 con n = 4, para contrastar el margen frente al umbral GSM de 9 dB.

### Hallazgos clave

- El reparto exacto de 24 portadoras en N=4 produce 6 portadoras por celda.
- La distancia de reutilización calculada es `D = 5.20 km`, con `D/R = 3.46`.
- La estimación `C/I = 13.80 dB` deja un margen de `+4.80 dB` sobre el umbral de referencia, por lo que la reutilización es defendible en el marco docente planteado.

### Canales lógicos y físicos

| cell   |   arfcn |   uplink_frequency_mhz | carrier_role      | frequency_hopping_recommended   | power_policy          |   available_timeslots | engineering_note                                                             |
|:-------|--------:|-----------------------:|:------------------|:--------------------------------|:----------------------|----------------------:|:-----------------------------------------------------------------------------|
| A      |       1 |                  890.2 | BCCH/CCCH control | False                           | fixed/stable          |                     8 | BCCH debe ser detectable y estable para camping, sincronización y control.   |
| A      |       2 |                  890.4 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| A      |       3 |                  890.6 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| A      |       4 |                  890.8 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| A      |       5 |                  891   | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| A      |       6 |                  891.2 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| B      |       7 |                  891.4 | BCCH/CCCH control | False                           | fixed/stable          |                     8 | BCCH debe ser detectable y estable para camping, sincronización y control.   |
| B      |       8 |                  891.6 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| B      |       9 |                  891.8 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| B      |      10 |                  892   | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| B      |      11 |                  892.2 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| B      |      12 |                  892.4 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| C      |      13 |                  892.6 | BCCH/CCCH control | False                           | fixed/stable          |                     8 | BCCH debe ser detectable y estable para camping, sincronización y control.   |
| C      |      14 |                  892.8 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| C      |      15 |                  893   | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| C      |      16 |                  893.2 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| C      |      17 |                  893.4 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| C      |      18 |                  893.6 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| D      |      19 |                  893.8 | BCCH/CCCH control | False                           | fixed/stable          |                     8 | BCCH debe ser detectable y estable para camping, sincronización y control.   |
| D      |      20 |                  894   | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| D      |      21 |                  894.2 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| D      |      22 |                  894.4 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| D      |      23 |                  894.6 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |
| D      |      24 |                  894.8 | TCH traffic       | True                            | adaptive if supported |                     8 | TCH transporta tráfico; puede beneficiarse de hopping y control de potencia. |

### Instrumentación y RBW

|   rbw_hz |   rbw_khz |   noise_figure_db |   noise_floor_dbm |   danl_dbm |   delta_vs_100khz_db | measurement_interpretation                                                   |
|---------:|----------:|------------------:|------------------:|-----------:|---------------------:|:-----------------------------------------------------------------------------|
|   100000 |       100 |                 6 |              -118 |    -120.51 |                    0 | RBW ancho: medida rápida, más ruido integrado y menor sensibilidad.          |
|    10000 |        10 |                 6 |              -128 |    -130.51 |                  -10 | RBW estrecho: menor ruido integrado, mejor sensibilidad y barrido más lento. |
|     1000 |         1 |                 6 |              -138 |    -140.51 |                  -20 | RBW estrecho: menor ruido integrado, mejor sensibilidad y barrido más lento. |

Nota instrumental: `noise_floor_dbm` representa el cálculo térmico base `-174 + 10log10(RBW) + NF`, mientras que `danl_dbm` añade la corrección típica de 2,51 dB del detector logarítmico usada en analizadores.

Con `RBW = 10 kHz` y `NF = 6 dB`, el suelo de ruido térmico es `-128.00 dBm` y el DANL aproximado corregido es `-130.51 dBm`.

## Conclusión técnica

El escenario A está dominado por movilidad, Doppler y variación temporal del canal. El escenario B está dominado por eficiencia espectral, reutilización de frecuencias, control de interferencia co-canal y criterio instrumental para medidas RED. En conjunto, la configuración analizada resulta coherente con los requerimientos del reto: la física del canal sigue siendo compatible con la ráfaga GSM en alta velocidad, mientras que la planificación N=4 y el análisis RBW aportan una base técnica defendible para el campamento y su validación espectral.