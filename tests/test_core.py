import math

from protocolo_titan.propagation import kmh_to_ms, max_doppler_hz, coherence_time_s
from protocolo_titan.cellular_planning import (
    carriers_per_cell,
    reuse_distance_km,
    reuse_ratio,
    cochannel_interference_db,
    gsm900_uplink_frequency_mhz,
)
from protocolo_titan.instrumentation import analyzer_noise_floor_dbm, analyzer_danl_dbm, rbw_noise_table
from protocolo_titan.config import GSMConfig, ConvoyScenario, CampScenario, AnalyzerConfig
from protocolo_titan.scenario_a import analyze_convoy_mobility, analyze_convoy_fading, fading_trace_key
from protocolo_titan.scenario_b import analyze_camp_base
from protocolo_titan.report import build_markdown_report
from protocolo_titan.validation import validate_inputs


def test_speed_conversion():
    assert math.isclose(kmh_to_ms(50), 13.8888888889)


def test_doppler_50_kmh_900mhz():
    v = kmh_to_ms(50)
    assert math.isclose(max_doppler_hz(v, 900e6), 41.6666666667)


def test_coherence_250_kmh():
    v = kmh_to_ms(250)
    fd = max_doppler_hz(v, 900e6)
    assert math.isclose(coherence_time_s(fd) * 1e3, 2.0304, rel_tol=1e-3)


def test_carriers_per_cell():
    assert carriers_per_cell(24, 4) == 6


def test_reuse_distance():
    assert math.isclose(reuse_ratio(4), math.sqrt(12))
    assert math.isclose(reuse_distance_km(1.5, 4), 5.1961524, rel_tol=1e-6)


def test_noise_floor():
    assert math.isclose(analyzer_noise_floor_dbm(100e3, 6), -118.0)
    assert math.isclose(analyzer_noise_floor_dbm(10e3, 6), -128.0)
    assert math.isclose(analyzer_noise_floor_dbm(1e3, 6), -138.0)


def test_danl_floor_with_log_detector_correction():
    assert math.isclose(analyzer_danl_dbm(100e3, 6), -120.51, rel_tol=1e-6)


def test_gsm900_arfcn_frequency_mapping():
    assert math.isclose(gsm900_uplink_frequency_mhz(1), 890.2)
    assert math.isclose(gsm900_uplink_frequency_mhz(24), 894.8)


def test_cochannel_ratio_for_cluster_four():
    assert math.isclose(cochannel_interference_db(4), 13.8021124171, rel_tol=1e-6)


def test_invalid_carrier_distribution_raises():
    try:
        carriers_per_cell(25, 4)
    except ValueError as exc:
        assert 'divisible' in str(exc)
    else:
        raise AssertionError('Se esperaba ValueError para una distribución no divisible.')


def test_convoy_mobility_preserves_custom_speeds():
    mobility = analyze_convoy_mobility(
        ConvoyScenario(speeds_kmh=(60.0, 180.0)),
        GSMConfig(timeslot_duration_s=600e-6),
    )

    assert mobility['speed_kmh'].tolist() == [60.0, 180.0]
    assert math.isclose(float(mobility['gsm_timeslot_ms'].iloc[0]), 0.6)


def test_convoy_fading_trace_matches_custom_speed_keys():
    _, traces = analyze_convoy_fading(ConvoyScenario(speeds_kmh=(60.0, 180.0)))

    assert fading_trace_key('rician', 60.0) in traces
    assert fading_trace_key('rician', 180.0) in traces


def test_convoy_fading_trace_preserves_decimal_speeds():
    _, traces = analyze_convoy_fading(ConvoyScenario(speeds_kmh=(60.5, 180.5)))

    assert fading_trace_key('rician', 60.5) in traces
    assert fading_trace_key('rician', 180.5) in traces


def test_validate_inputs_rejects_duplicate_speeds():
    errors = validate_inputs(
        ConvoyScenario(speeds_kmh=(60.0, 60.0)),
        CampScenario(total_carriers=24, cluster_size=4),
    )

    assert any('deben ser distintas' in error for error in errors)


def test_validate_inputs_rejects_invalid_carrier_plan():
    errors = validate_inputs(
        ConvoyScenario(speeds_kmh=(60.0, 180.0)),
        CampScenario(total_carriers=25, cluster_size=4),
    )

    assert any('divisible' in error for error in errors)


def test_validate_inputs_accepts_valid_configuration():
    errors = validate_inputs(
        ConvoyScenario(speeds_kmh=(60.0, 180.0)),
        CampScenario(total_carriers=24, cluster_size=4),
    )

    assert errors == []


def test_build_markdown_report_uses_dynamic_timeslot():
    gsm = GSMConfig(timeslot_duration_s=600e-6)
    convoy = ConvoyScenario(speeds_kmh=(60.0, 180.0))
    analyzer = AnalyzerConfig()
    mobility = analyze_convoy_mobility(convoy, gsm)
    fading_metrics, _ = analyze_convoy_fading(convoy, gsm)
    camp_results = analyze_camp_base(CampScenario(total_carriers=24, cluster_size=4), gsm, analyzer)

    report = build_markdown_report(
        mobility=mobility,
        fading_metrics=fading_metrics,
        frequency_planning=camp_results['frequency_planning'],
        logical_channels=camp_results['logical_channels'],
        rbw_noise=camp_results['rbw_noise'],
    )

    assert '600 µs' in report
    assert '577 µs' not in report


def test_build_markdown_report_includes_sections():
    gsm = GSMConfig()
    convoy = ConvoyScenario()
    mobility = analyze_convoy_mobility(convoy, gsm)
    fading_metrics, _ = analyze_convoy_fading(convoy, gsm)
    camp_results = analyze_camp_base(CampScenario(), gsm, AnalyzerConfig())
    rbw_noise = rbw_noise_table(AnalyzerConfig())

    report = build_markdown_report(
        mobility=mobility,
        fading_metrics=fading_metrics,
        frequency_planning=camp_results['frequency_planning'],
        logical_channels=camp_results['logical_channels'],
        rbw_noise=rbw_noise,
    )

    assert '## Escenario A — Convoy de alta velocidad' in report
    assert '## Escenario B — Campamento base' in report
    assert '## Conclusión técnica' in report
    assert 'C/I' in report
    assert 'danl_dbm' in report
