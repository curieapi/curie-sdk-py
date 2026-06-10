# tests/test_client.py
import pytest
import respx
import httpx
from curie import Client, AuthenticationError, ModelNotFoundError


BASE_URL = "https://api.curie.sh"


@pytest.fixture
def client():
    return Client(api_key="sk-test-key", base_url=BASE_URL)


@respx.mock
def test_fold_success(client):
    respx.post(f"{BASE_URL}/v1/run").mock(return_value=httpx.Response(200, json={
        "job_id": "test-job-id",
        "model": "esm/esmfold-v1",
        "pdb": "ATOM 1 N MET A 1...",
        "plddt": 0.87,
        "length": 16,
        "latency_ms": 500,
        "cost_usd": 0.005,
    }))
    result = client.fold("MKTIIALSYIFCLVFA")
    assert result.pdb == "ATOM 1 N MET A 1..."
    assert result.plddt == 0.87
    assert result.confidence == pytest.approx(87.0)
    assert result.is_high_confidence is True


@respx.mock
def test_invalid_api_key(client):
    respx.post(f"{BASE_URL}/v1/run").mock(return_value=httpx.Response(401, json={
        "error": "Invalid or missing API key",
        "code": "UNAUTHORIZED",
    }))
    with pytest.raises(AuthenticationError):
        client.fold("MKTIIALSYIFCLVFA")


@respx.mock
def test_model_not_found(client):
    respx.post(f"{BASE_URL}/v1/run").mock(return_value=httpx.Response(404, json={
        "error": "Model 'unknown/model' not found",
        "code": "MODEL_NOT_FOUND",
        "available_models": ["esm/esmfold-v1", "meta/esm2-650m"],
    }))
    with pytest.raises(ModelNotFoundError) as exc_info:
        client.run("unknown/model", sequence="MKTII")
    assert "esm/esmfold-v1" in exc_info.value.available_models


def test_missing_api_key():
    with pytest.raises(AuthenticationError):
        Client(api_key=None)


@respx.mock
def test_embed_returns_numpy(client):
    embedding = [0.1] * 1280
    respx.post(f"{BASE_URL}/v1/run").mock(return_value=httpx.Response(200, json={
        "job_id": "test-job-id",
        "model": "meta/esm2-650m",
        "embedding": embedding,
        "per_residue": None,
        "length": 16,
        "latency_ms": 100,
        "cost_usd": 0.002,
    }))
    result = client.embed("MKTIIALSYIFCLVFA")
    assert result.dim == 1280

    # Test that to_numpy() raises ImportError when numpy not installed
    try:
        import numpy
        arr = result.to_numpy()
        assert arr.shape == (1280,)
    except ImportError:
        # If numpy not installed, verify the method raises the right error
        with pytest.raises(ImportError, match="numpy is required"):
            result.to_numpy()
