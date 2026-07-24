from src.preprocessing import clean_and_engineer_features

def test_feature_engineering_outputs(sample_daily_df):
    processed = clean_and_engineer_features(sample_daily_df)
    
    # Assert data is generated without nulls
    assert not processed.empty
    assert "rolling_7_tmax" in processed.columns
    assert "rolling_14_tmax" in processed.columns
    assert not processed.isnull().any().any()