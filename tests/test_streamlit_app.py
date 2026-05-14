import importlib
import sys
import types


class _FakeStreamlitModule:
    def __init__(self):
        self.errors = []

    def set_page_config(self, **kwargs):
        self.page_config = kwargs

    def error(self, message):
        self.errors.append(message)


def _load_streamlit_app(monkeypatch):
    fake_streamlit = _FakeStreamlitModule()
    monkeypatch.setitem(sys.modules, 'streamlit', fake_streamlit)
    sys.modules.pop('protocolo_titan.streamlit_app', None)
    module = importlib.import_module('protocolo_titan.streamlit_app')
    return module, fake_streamlit


def test_main_reports_validation_errors(monkeypatch):
    module, fake_streamlit = _load_streamlit_app(monkeypatch)
    calls = []

    monkeypatch.setattr(module, 'inject_css', lambda: calls.append('inject_css'))
    monkeypatch.setattr(module, 'header', lambda: calls.append('header'))
    monkeypatch.setattr(
        module,
        'sidebar_controls',
        lambda: ('Escenario A · Physics & Spectrum', 900.0, 577.0, 60.0, 60.0, 25, 4, 1.5, 6.0),
    )
    monkeypatch.setattr(module, 'render_scenario_a', lambda *args: calls.append('render_a'))
    monkeypatch.setattr(module, 'render_scenario_b', lambda *args: calls.append('render_b'))

    module.main()

    assert calls == ['inject_css', 'header']
    assert len(fake_streamlit.errors) == 2
    assert any('deben ser distintas' in error for error in fake_streamlit.errors)
    assert any('divisible' in error for error in fake_streamlit.errors)


def test_main_dispatches_scenario_a(monkeypatch):
    module, fake_streamlit = _load_streamlit_app(monkeypatch)
    captured = {}

    monkeypatch.setattr(module, 'inject_css', lambda: None)
    monkeypatch.setattr(module, 'header', lambda: None)
    monkeypatch.setattr(
        module,
        'sidebar_controls',
        lambda: ('Escenario A · Physics & Spectrum', 1800.0, 600.0, 60.0, 180.0, 24, 4, 1.7, 7.5),
    )
    monkeypatch.setattr(
        module,
        'render_scenario_a',
        lambda gsm, convoy, camp, analyzer: captured.update(
            {
                'carrier_frequency_hz': gsm.carrier_frequency_hz,
                'timeslot_duration_s': gsm.timeslot_duration_s,
                'speeds_kmh': convoy.speeds_kmh,
                'total_carriers': camp.total_carriers,
                'cluster_size': camp.cluster_size,
                'noise_figure_db': analyzer.noise_figure_db,
            }
        ),
    )
    monkeypatch.setattr(module, 'render_scenario_b', lambda *args: captured.update({'wrong_branch': True}))

    module.main()

    assert fake_streamlit.errors == []
    assert captured['carrier_frequency_hz'] == 1800.0 * 1e6
    assert captured['timeslot_duration_s'] == 600.0 * 1e-6
    assert captured['speeds_kmh'] == (60.0, 180.0)
    assert captured['total_carriers'] == 24
    assert captured['cluster_size'] == 4
    assert captured['noise_figure_db'] == 7.5
    assert 'wrong_branch' not in captured


def test_main_dispatches_scenario_b(monkeypatch):
    module, fake_streamlit = _load_streamlit_app(monkeypatch)
    captured = {}

    monkeypatch.setattr(module, 'inject_css', lambda: None)
    monkeypatch.setattr(module, 'header', lambda: None)
    monkeypatch.setattr(
        module,
        'sidebar_controls',
        lambda: ('Escenario B · Base Camp', 900.0, 577.0, 50.0, 250.0, 24, 6, 2.0, 5.0),
    )
    monkeypatch.setattr(module, 'render_scenario_a', lambda *args: captured.update({'wrong_branch': True}))
    monkeypatch.setattr(
        module,
        'render_scenario_b',
        lambda gsm, camp, analyzer: captured.update(
            {
                'carrier_frequency_hz': gsm.carrier_frequency_hz,
                'cluster_size': camp.cluster_size,
                'cell_radius_km': camp.cell_radius_km,
                'noise_figure_db': analyzer.noise_figure_db,
            }
        ),
    )

    module.main()

    assert fake_streamlit.errors == []
    assert captured['carrier_frequency_hz'] == 900.0 * 1e6
    assert captured['cluster_size'] == 6
    assert captured['cell_radius_km'] == 2.0
    assert captured['noise_figure_db'] == 5.0
    assert 'wrong_branch' not in captured
