import pytest
import pandas as pd
import tempfile
import os
from app.services.data_processing_service import DataProcessingService

@pytest.fixture
def data_processor():
    return DataProcessingService()

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
        'age': [30, 25, 35, 28, 32],
        'department': ['Engineering', 'Marketing', 'Engineering', 'Sales', 'Engineering'],
        'salary': [75000, 60000, 80000, 55000, 70000]
    })

class TestDataProcessingService:
    
    def test_load_csv_file(self, data_processor):
        """Test CSV file loading"""
        csv_content = "id,name,age\n1,John,30\n2,Jane,25\n"
        
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as tmp:
            tmp.write(csv_content)
            tmp_path = tmp.name
            
        try:
            df = data_processor.load_file(tmp_path, 'csv')
            assert len(df) == 2
            assert list(df.columns) == ['id', 'name', 'age']
            assert df.iloc[0]['name'] == 'John'
        finally:
            os.unlink(tmp_path)
            
    def test_detect_data_types(self, data_processor, sample_dataframe):
        """Test automatic data type detection"""
        types = data_processor.detect_data_types(sample_dataframe)
        
        assert types['id'] == 'integer'
        assert types['name'] == 'string'
        assert types['age'] == 'integer'
        assert types['salary'] == 'integer'
        
    def test_clean_data(self, data_processor):
        """Test data cleaning operations"""
        dirty_data = pd.DataFrame({
            'name': ['John', '', 'Jane', None, 'Bob'],
            'age': [30, 25, None, 28, 32],
            'salary': [75000, None, 60000, 55000, 70000]
        })
        
        cleaned = data_processor.clean_data(dirty_data)
        
        # Should handle missing values
        assert not cleaned.isnull().any().any()
        
        # Should not have empty strings
        assert not (cleaned == '').any().any()
        
    def test_filter_data(self, data_processor, sample_dataframe):
        """Test data filtering"""
        # Filter by single condition
        filtered = data_processor.filter_data(sample_dataframe, {'age': {'gt': 28}})
        assert len(filtered) == 3
        
        # Filter by multiple conditions
        filtered = data_processor.filter_data(
            sample_dataframe, 
            {'age': {'gt': 25}, 'department': {'eq': 'Engineering'}}
        )
        assert len(filtered) == 2
        
    def test_aggregate_data(self, data_processor, sample_dataframe):
        """Test data aggregation"""
        # Group by department and calculate mean salary
        aggregated = data_processor.aggregate_data(
            sample_dataframe,
            group_by=['department'],
            aggregations={'salary': 'mean', 'age': 'max'}
        )
        
        assert 'department' in aggregated.columns
        assert 'salary' in aggregated.columns
        assert 'age' in aggregated.columns
        assert len(aggregated) == 3  # 3 unique departments
        
    def test_sort_data(self, data_processor, sample_dataframe):
        """Test data sorting"""
        # Sort by age ascending
        sorted_data = data_processor.sort_data(sample_dataframe, [{'column': 'age', 'direction': 'asc'}])
        ages = sorted_data['age'].tolist()
        assert ages == sorted(ages)
        
        # Sort by salary descending
        sorted_data = data_processor.sort_data(sample_dataframe, [{'column': 'salary', 'direction': 'desc'}])
        salaries = sorted_data['salary'].tolist()
        assert salaries == sorted(salaries, reverse=True)
        
    def test_get_summary_statistics(self, data_processor, sample_dataframe):
        """Test summary statistics generation"""
        stats = data_processor.get_summary_statistics(sample_dataframe)
        
        assert 'id' in stats
        assert 'age' in stats
        assert 'salary' in stats
        
        # Check that basic stats are included
        assert 'mean' in stats['age']
        assert 'median' in stats['age']
        assert 'std' in stats['age']
        assert 'min' in stats['age']
        assert 'max' in stats['age']
        
    def test_detect_outliers(self, data_processor):
        """Test outlier detection"""
        data_with_outliers = pd.DataFrame({
            'values': [1, 2, 3, 4, 5, 100]  # 100 is an outlier
        })
        
        outliers = data_processor.detect_outliers(data_with_outliers, 'values')
        assert 100 in outliers['values'].values
        
    def test_memory_efficient_processing(self, data_processor):
        """Test memory-efficient processing of large datasets"""
        # Create a larger dataset
        large_data = pd.DataFrame({
            'id': range(10000),
            'value': range(10000)
        })
        
        # Process in chunks
        result = data_processor.process_in_chunks(
            large_data, 
            chunk_size=1000,
            operation='sum'
        )
        
        assert result is not None
        assert isinstance(result, dict)
        
    def test_data_validation(self, data_processor, sample_dataframe):
        """Test data validation"""
        validation_results = data_processor.validate_data(sample_dataframe)
        
        assert 'row_count' in validation_results
        assert 'column_count' in validation_results
        assert 'missing_values' in validation_results
        assert 'data_types' in validation_results
        
        assert validation_results['row_count'] == 5
        assert validation_results['column_count'] == 5