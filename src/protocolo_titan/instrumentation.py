import math
import pandas as pd

from .config import AnalyzerConfig


LOG_DETECTOR_CORRECTION_DB = 2.51


def analyzer_noise_floor_dbm(rbw_hz: float, noise_figure_db: float = 6.0) -> float:
    """Calcula el suelo de ruido integrado en el RBW del analizador."""
    if rbw_hz <= 0:
        raise ValueError("RBW debe ser positivo.")
    return -174.0 + 10.0 * math.log10(rbw_hz) + noise_figure_db


def analyzer_danl_dbm(rbw_hz: float, noise_figure_db: float = 6.0) -> float:
    """Aproxima el DANL incluyendo la corrección típica del detector logarítmico."""
    return analyzer_noise_floor_dbm(rbw_hz, noise_figure_db) - LOG_DETECTOR_CORRECTION_DB


def rbw_noise_table(config: AnalyzerConfig = AnalyzerConfig()) -> pd.DataFrame:
    rows = []
    reference = None

    for rbw in config.rbw_values_hz:
        noise = analyzer_noise_floor_dbm(rbw, config.noise_figure_db)
        danl = analyzer_danl_dbm(rbw, config.noise_figure_db)

        if reference is None:
            reference = noise

        rows.append(
            {
                "rbw_hz": rbw,
                "rbw_khz": rbw / 1e3,
                "noise_figure_db": config.noise_figure_db,
                "noise_floor_dbm": noise,
                "danl_dbm": danl,
                "delta_vs_100khz_db": noise - reference,
                "measurement_interpretation": (
                    "RBW ancho: medida rápida, más ruido integrado y menor sensibilidad."
                    if rbw >= 100e3
                    else "RBW estrecho: menor ruido integrado, mejor sensibilidad y barrido más lento."
                ),
            }
        )

    return pd.DataFrame(rows)


def red_compliance_checklist() -> pd.DataFrame:
    """Checklist teórico de conformidad RED para el informe del alumno."""
    rows = [
        {
            "area": "Uso eficiente del espectro",
            "evidence": "planificación ARFCN, clúster N=4, distancia de reutilización y control de co-canal",
            "student_task": "Justificar que la asignación espectral reduce interferencias y evita solapamientos.",
        },
        {
            "area": "Emisiones no deseadas",
            "evidence": "medida con analizador de espectro y ajuste de RBW",
            "student_task": "Explicar cómo se distinguirían señales débiles de ruido instrumental.",
        },
        {
            "area": "Estabilidad de canal",
            "evidence": "Doppler, tiempo de coherencia y comparación con timeslot GSM",
            "student_task": "Defender si el enlace es viable durante la ráfaga en movilidad.",
        },
        {
            "area": "Documentación técnica",
            "evidence": "tablas, gráficas, hipótesis y trazabilidad de cálculos",
            "student_task": "Incluir ecuaciones, unidades y discusión ingenieril.",
        },
    ]
    return pd.DataFrame(rows)
