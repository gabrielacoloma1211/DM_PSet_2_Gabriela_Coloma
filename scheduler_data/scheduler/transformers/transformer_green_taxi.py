import time

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(loader_output, *args, **kwargs):
    required = ["status", "service_type", "source_month", "ingest_ts", "local_file"]
    for k in required:
        if k not in loader_output:
            raise KeyError(f"Falta clave del loader: {k}")
    return loader_output


@test
def test_output(output, *args) -> None:
    assert output is not None and isinstance(output, dict)
    assert "source_month" in output and "service_type" in output