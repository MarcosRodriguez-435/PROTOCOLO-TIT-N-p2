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
    lines = []
    lines.append("# Informe de resultados — Protocolo Titán")
    lines.append("")
    lines.append("## Escenario A — Convoy de alta velocidad")
    lines.append("")
    lines.append(mobility.to_markdown(index=False))
    lines.append("")
    lines.append(
        f"Interpretación: el criterio principal es comparar el tiempo de coherencia con el timeslot GSM de {timeslot_ms * 1e3:.0f} µs."
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
    lines.append("### Canales lógicos y físicos")
    lines.append("")
    lines.append(logical_channels.to_markdown(index=False))
    lines.append("")
    lines.append("### Instrumentación y RBW")
    lines.append("")
    lines.append(rbw_noise.to_markdown(index=False))
    lines.append("")
    lines.append("## Conclusión técnica")
    lines.append("")
    lines.append(
        "El escenario A está dominado por movilidad, Doppler y variación temporal del canal. "
        "El escenario B está dominado por eficiencia espectral, reutilización de frecuencias, "
        "control de interferencia co-canal y criterio instrumental para medidas RED."
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
