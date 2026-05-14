from pathlib import Path
import pandas as pd


def build_markdown_report(
    mobility: pd.DataFrame,
    fading_metrics: pd.DataFrame,
    frequency_planning: pd.DataFrame,
    logical_channels: pd.DataFrame,
    rbw_noise: pd.DataFrame,
) -> str:
    """Genera el contenido Markdown del informe."""
    timeslot_ms = float(mobility["gsm_timeslot_ms"].iloc[0])
    low_speed = mobility.iloc[0]
    high_speed = mobility.iloc[-1]
    plan_row = frequency_planning.iloc[0]
    rbw_reference = rbw_noise[rbw_noise["rbw_khz"] == 10.0].iloc[0]
    lines = []
    lines.append("# Informe de resultados — Protocolo Titán")
    lines.append("")
    lines.append("## Resumen ejecutivo")
    lines.append("")
    lines.append(
        f"El análisis confirma que, para GSM-900 y un timeslot de {timeslot_ms * 1e3:.0f} µs, el escenario A sigue "
        f"operando en fading lento tanto a {low_speed['speed_kmh']:.0f} km/h como a {high_speed['speed_kmh']:.0f} km/h, "
        f"aunque el margen temporal cae desde {low_speed['coherence_to_timeslot_ratio']:.2f} hasta {high_speed['coherence_to_timeslot_ratio']:.2f}."
    )
    lines.append(
        f"En el escenario B, la planificación con N={int(plan_row['cluster_size_N'])} reparte {int(plan_row['total_carriers'])} portadoras en "
        f"{int(plan_row['carriers_per_cell'])} portadoras por celda y obtiene C/I ≈ {plan_row['cochannel_ci_db']:.2f} dB, "
        f"superando en {plan_row['ci_margin_vs_gsm_db']:.2f} dB el umbral GSM de referencia."
    )
    lines.append("")
    lines.append("## Metodología reproducible")
    lines.append("")
    lines.append("1. Conversión de velocidades de km/h a m/s para el cálculo Doppler.")
    lines.append("2. Cálculo de Doppler máximo con `f_d = v · f_c / c`.")
    lines.append("3. Estimación del tiempo de coherencia con `T_c ≈ 0.423 / f_d` y comparación con el timeslot GSM.")
    lines.append("4. Simulación docente de fading Rayleigh y Rician durante una ráfaga GSM.")
    lines.append("5. Planificación celular con `D/R = sqrt(3N)` y estimación de `C/I ≈ (D/R)^n / 6`, con `n = 4`.")
    lines.append("6. Evaluación instrumental del ruido integrado con `-174 + 10log10(RBW) + NF` y DANL aproximado corregido.")
    lines.append("")
    lines.append("## Escenario A — Convoy de alta velocidad")
    lines.append("")
    lines.append(mobility.to_markdown(index=False))
    lines.append("")
    lines.append(
        f"Interpretación: el criterio principal es comparar el tiempo de coherencia con el timeslot GSM de {timeslot_ms * 1e3:.0f} µs."
    )
    lines.append("")
    lines.append("### Hallazgos clave")
    lines.append("")
    lines.append(
        f"- A {low_speed['speed_kmh']:.0f} km/h, `f_d = {low_speed['max_doppler_hz']:.2f} Hz` y `T_c = {low_speed['coherence_time_ms']:.2f} ms`, "
        f"por lo que el canal se comporta como cuasiestático durante la ráfaga."
    )
    lines.append(
        f"- A {high_speed['speed_kmh']:.0f} km/h, `f_d = {high_speed['max_doppler_hz']:.2f} Hz` y `T_c = {high_speed['coherence_time_ms']:.2f} ms`; "
        f"el enlace sigue siendo viable, pero con margen temporal claramente menor."
    )
    lines.append(
        "- Desde un punto de vista de ingeniería, este resultado justifica el uso cuidadoso de entrenamiento de ráfaga, ecualización y esquemas robustos de codificación/interleaving."
    )
    lines.append("")
    lines.append("### Métricas de fading")
    lines.append("")
    lines.append(fading_metrics.to_markdown(index=False))
    lines.append("")
    lines.append("## Escenario B — Campamento base")
    lines.append("")
    lines.append("### Planificación de frecuencias")
    lines.append("")
    lines.append(frequency_planning.to_markdown(index=False))
    lines.append("")
    lines.append(
        "Interpretación: además de D/R y D, se incluye la relación co-canal C/I usando el modelo hexagonal "
        "aproximado C/I = (D/R)^n / 6 con n = 4, para contrastar el margen frente al umbral GSM de 9 dB."
    )
    lines.append("")
    lines.append("### Hallazgos clave")
    lines.append("")
    lines.append(
        f"- El reparto exacto de {int(plan_row['total_carriers'])} portadoras en N={int(plan_row['cluster_size_N'])} produce {int(plan_row['carriers_per_cell'])} portadoras por celda."
    )
    lines.append(
        f"- La distancia de reutilización calculada es `D = {plan_row['reuse_distance_km']:.2f} km`, con `D/R = {plan_row['reuse_ratio_D_over_R']:.2f}`."
    )
    lines.append(
        f"- La estimación `C/I = {plan_row['cochannel_ci_db']:.2f} dB` deja un margen de `+{plan_row['ci_margin_vs_gsm_db']:.2f} dB` sobre el umbral de referencia, por lo que la reutilización es defendible en el marco docente planteado."
    )
    lines.append("")
    lines.append("### Canales lógicos y físicos")
    lines.append("")
    lines.append(logical_channels.to_markdown(index=False))
    lines.append("")
    lines.append("### Instrumentación y RBW")
    lines.append("")
    lines.append(rbw_noise.to_markdown(index=False))
    lines.append("")
    lines.append(
        "Nota instrumental: `noise_floor_dbm` representa el cálculo térmico base `-174 + 10log10(RBW) + NF`, "
        "mientras que `danl_dbm` añade la corrección típica de 2,51 dB del detector logarítmico usada en analizadores."
    )
    lines.append("")
    lines.append(
        f"Con `RBW = {rbw_reference['rbw_khz']:.0f} kHz` y `NF = {rbw_reference['noise_figure_db']:.0f} dB`, el suelo de ruido térmico es `"
        f"{rbw_reference['noise_floor_dbm']:.2f} dBm` y el DANL aproximado corregido es `{rbw_reference['danl_dbm']:.2f} dBm`."
    )
    lines.append("")
    lines.append("## Conclusión técnica")
    lines.append("")
    lines.append(
        "El escenario A está dominado por movilidad, Doppler y variación temporal del canal. "
        "El escenario B está dominado por eficiencia espectral, reutilización de frecuencias, "
        "control de interferencia co-canal y criterio instrumental para medidas RED. En conjunto, la configuración analizada resulta "
        "coherente con los requerimientos del reto: la física del canal sigue siendo compatible con la ráfaga GSM en alta velocidad, "
        "mientras que la planificación N=4 y el análisis RBW aportan una base técnica defendible para el campamento y su validación espectral."
    )
    return "\n".join(lines)


def write_markdown_report(
    output_path: Path,
    mobility: pd.DataFrame,
    fading_metrics: pd.DataFrame,
    frequency_planning: pd.DataFrame,
    logical_channels: pd.DataFrame,
    rbw_noise: pd.DataFrame,
) -> None:
    """Genera un resumen Markdown que puede usarse como base del informe."""
    output_path.write_text(
        build_markdown_report(
            mobility=mobility,
            fading_metrics=fading_metrics,
            frequency_planning=frequency_planning,
            logical_channels=logical_channels,
            rbw_noise=rbw_noise,
        ),
        encoding="utf-8",
    )
