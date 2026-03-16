from src.normalize.normalizers import normalize_component_type, normalize_manufacturer, normalize_model


def test_manufacturer_normalization_variants():
    assert normalize_manufacturer("Allen Bradley") == "Allen-Bradley"
    assert normalize_manufacturer("A-B") == "Allen-Bradley"
    assert normalize_manufacturer("CISCO") == "Cisco"
    assert normalize_manufacturer("Microtik") == "MikroTik"


def test_model_normalization():
    assert normalize_model(" 1756-l83e ") == "1756-L83E"
    assert normalize_model("unknown") is None


def test_component_type_normalization():
    assert normalize_component_type("Managed Switch") == "Network Switch"
    assert normalize_component_type("plc") == "PLC"
