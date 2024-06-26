import pandas as pd

from ..historiography.dataset.make_dataset import make_historiography_dataset
from ..historiography.settings import HistoriographyDatasetConfig

def test_make_historiography_dataset(driver, sample_valid_dataset_config: HistoriographyDatasetConfig):
    config = sample_valid_dataset_config
    assert not sample_valid_dataset_config.output_file_path.is_file()
    dataset = make_historiography_dataset(
        driver=driver,
        config=config
    )
    assert isinstance(dataset, pd.DataFrame)
    assert len(dataset) > 0
    assert config.output_file_path.is_file()
    loaded_dataset = pd.read_csv(str(config.output_file_path))
    pd.testing.assert_frame_equal(dataset, loaded_dataset)

    