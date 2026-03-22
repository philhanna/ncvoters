from ncvoters.domain.models import Column, Configuration, Layout


def test_configuration():
    config = Configuration(selected_columns=["a", "b"], sanitize_columns=["a"])
    assert config.selected_columns == ["a", "b"]
    assert config.sanitize_columns == ["a"]
    assert config.db_dir is None


def test_configuration_db_dir():
    config = Configuration(selected_columns=[], sanitize_columns=[], db_dir="~/Desktop")
    assert config.db_dir == "~/Desktop"


def test_layout_defaults():
    layout = Layout()
    assert layout.all_columns == []
    assert layout.status_codes == {}
    assert layout.county_codes == {}


def test_column():
    col = Column(name="last_name", data_type="varchar2(25)", description="Voter last name")
    assert col.name == "last_name"
