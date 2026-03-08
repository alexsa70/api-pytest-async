from pathlib import Path

import pytest
import schemathesis

from config.settings import Settings

OPENAPI_PATH = Path(__file__).resolve().parents[2] / "openapi" / "openapi.json"
schema = schemathesis.openapi.from_path(str(OPENAPI_PATH))


@pytest.mark.fuzz
@pytest.mark.skipif(not Settings().run_fuzz, reason="Set RUN_FUZZ=true to execute fuzz tests")
@schema.parametrize()
def test_openapi_fuzz(case: schemathesis.Case, settings: Settings) -> None:
    response = case.call(base_url=settings.api_base_url)
    case.validate_response(response)
