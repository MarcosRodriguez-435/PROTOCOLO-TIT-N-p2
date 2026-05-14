import math
from typing import Dict, List
import pandas as pd

from .config import CampScenario, GSMConfig


GSM_MINIMUM_CI_DB = 9.0


def carriers_per_cell(total_carriers: int, cluster_size: int) -> int:
    if total_carriers <= 0 or cluster_size <= 0:
        raise ValueError("total_carriers y cluster_size deben ser positivos.")
    if total_carriers % cluster_size != 0:
        raise ValueError("El reparto exacto exige que total_carriers sea divisible por cluster_size.")
    return total_carriers // cluster_size


def reuse_ratio(cluster_size: int) -> float:
    if cluster_size <= 0:
        raise ValueError("cluster_size debe ser positivo.")
    return math.sqrt(3 * cluster_size)


def reuse_distance_km(cell_radius_km: float, cluster_size: int) -> float:
    if cell_radius_km <= 0:
        raise ValueError("cell_radius_km debe ser positivo.")
    return cell_radius_km * reuse_ratio(cluster_size)


def cochannel_interference_linear(
    cluster_size: int,
    path_loss_exponent: float = 4.0,
    first_tier_interferers: int = 6,
) -> float:
    if path_loss_exponent <= 0:
        raise ValueError("path_loss_exponent debe ser positivo.")
    if first_tier_interferers <= 0:
        raise ValueError("first_tier_interferers debe ser positivo.")
    return (reuse_ratio(cluster_size) ** path_loss_exponent) / first_tier_interferers


def cochannel_interference_db(
    cluster_size: int,
    path_loss_exponent: float = 4.0,
    first_tier_interferers: int = 6,
) -> float:
    return 10.0 * math.log10(
        cochannel_interference_linear(cluster_size, path_loss_exponent, first_tier_interferers)
    )


def gsm900_uplink_frequency_mhz(arfcn: int) -> float:
    if arfcn <= 0:
        raise ValueError("arfcn debe ser positivo para GSM-900.")
    return 890.0 + 0.2 * arfcn


def assign_arfcns(
    scenario: CampScenario = CampScenario(),
) -> Dict[str, List[int]]:
    """Asigna ARFCNs consecutivos a las celdas del clúster.

    Para docencia se usa una asignación consecutiva. En ingeniería real se
    contrastaría con drive tests, coordinación espectral y medidas de campo.
    """
    n = carriers_per_cell(scenario.total_carriers, scenario.cluster_size)
    assignments: Dict[str, List[int]] = {}

    current = scenario.first_arfcn
    for idx in range(scenario.cluster_size):
        cell = chr(ord("A") + idx)
        assignments[cell] = list(range(current, current + n))
        current += n

    return assignments


def channel_logical_mapping(
    scenario: CampScenario = CampScenario(),
    config: GSMConfig = GSMConfig(),
) -> pd.DataFrame:
    """Propone una asignación didáctica BCCH/TCH por celda.

    - El primer ARFCN de cada celda se reserva como portadora BCCH.
    - El resto de portadoras se asignan preferentemente a TCH.
    - Se marca BCCH como potencia estable y sin frequency hopping.
    """
    assignments = assign_arfcns(scenario)
    rows = []

    for cell, arfcns in assignments.items():
        for idx, arfcn in enumerate(arfcns):
            is_bcch = idx == 0
            rows.append(
                {
                    "cell": cell,
                    "arfcn": arfcn,
                    "uplink_frequency_mhz": gsm900_uplink_frequency_mhz(arfcn),
                    "carrier_role": "BCCH/CCCH control" if is_bcch else "TCH traffic",
                    "frequency_hopping_recommended": False if is_bcch else True,
                    "power_policy": "fixed/stable" if is_bcch else "adaptive if supported",
                    "available_timeslots": config.timeslots_per_frame,
                    "engineering_note": (
                        "BCCH debe ser detectable y estable para camping, sincronización y control."
                        if is_bcch
                        else "TCH transporta tráfico; puede beneficiarse de hopping y control de potencia."
                    ),
                }
            )

    return pd.DataFrame(rows)


def frequency_planning_table(
    scenario: CampScenario = CampScenario(),
) -> pd.DataFrame:
    assignments = assign_arfcns(scenario)
    d = reuse_distance_km(scenario.cell_radius_km, scenario.cluster_size)
    d_over_r = reuse_ratio(scenario.cluster_size)
    per_cell = carriers_per_cell(scenario.total_carriers, scenario.cluster_size)
    ci_linear = cochannel_interference_linear(scenario.cluster_size)
    ci_db = cochannel_interference_db(scenario.cluster_size)

    rows = []
    for cell, arfcns in assignments.items():
        rows.append(
            {
                "scenario": "B_campamento_base",
                "cell": cell,
                "cell_radius_km": scenario.cell_radius_km,
                "cluster_size_N": scenario.cluster_size,
                "total_carriers": scenario.total_carriers,
                "carriers_per_cell": per_cell,
                "arfcn_range": f"{arfcns[0]}-{arfcns[-1]}",
                "arfcn_list": ", ".join(map(str, arfcns)),
                "reuse_ratio_D_over_R": d_over_r,
                "reuse_distance_km": d,
                "first_tier_interferers": 6,
                "path_loss_exponent": 4.0,
                "cochannel_ci_linear": ci_linear,
                "cochannel_ci_db": ci_db,
                "ci_margin_vs_gsm_db": ci_db - GSM_MINIMUM_CI_DB,
            }
        )

    return pd.DataFrame(rows)
