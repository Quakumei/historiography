from .fixtures import (
    sample_fixture
)

def test_sample_fixture(sample_fixture):
    assert f'Hello {sample_fixture}!' == 'Hello fixture!'

