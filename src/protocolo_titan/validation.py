from .cellular_planning import carriers_per_cell
from .config import CampScenario, ConvoyScenario


def validate_inputs(convoy: ConvoyScenario, camp: CampScenario) -> list[str]:
    errors = []

    if len(convoy.speeds_kmh) != len(set(convoy.speeds_kmh)):
        errors.append('Las velocidades del escenario A deben ser distintas para evitar resultados ambiguos.')

    try:
        carriers_per_cell(camp.total_carriers, camp.cluster_size)
    except ValueError as exc:
        errors.append(str(exc))

    return errors
