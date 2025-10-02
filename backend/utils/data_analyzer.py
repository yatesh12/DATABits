import pandas as pd
import numpy as np
from scipy import stats

class DataAnalyzer:
    @staticmethod
    def analyze_data_quality(df):
        """Analyze overall data quality"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        
        # Calculate quality score
        missing_penalty = min(50, (missing_cells / total_cells) * 100)
        
        # Check for duplicates
        duplicate_rows = df.duplicated().sum()
        duplicate_penalty = min(20, (duplicate_rows / len(df)) * 100)
        
        # Check for constant columns
        constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
        constant_penalty = min(10, len(constant_cols) / len(df.columns) * 100)
        
        quality_score = max(0, 100 - missing_penalty - duplicate_penalty - constant_penalty)
        
        return {
            'score': round(quality_score),
            'total_cells': total_cells,
            'missing_cells': missing_cells,
            'missing_percentage': round((missing_cells / total_cells) * 100, 2),
            'duplicate_rows': duplicate_rows,
            'constant_columns': constant_cols,
            'issues': DataAnalyzer._identify_issues(df)
        }
    
    @staticmethod
    def _identify_issues(df):
        """Identify specific data quality issues"""
        issues = []
        
        # Missing values
        missing_counts = df.isnull().sum()
        high_missing = missing_counts[missing_counts > len(df) * 0.3]
        for col, count in high_missing.items():
            pct = (count / len(df)) * 100
            severity = 'high' if pct > 70 else 'medium'
            issues.append({
                'type': f'High missing values in {col}',
                'count': count,
                'severity': severity,
                'description': f'{pct:.1f}% missing values'
            })
        
        # Duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            severity = 'high' if duplicates > len(df) * 0.1 else 'medium'
            issues.append({
                'type': 'Duplicate rows',
                'count': duplicates,
                'severity': severity,
                'description': f'{(duplicates/len(df)*100):.1f}% of rows are duplicates'
            })
        
        # Constant columns
        for col in df.columns:
            if df[col].nunique() <= 1:
                issues.append({
                    'type': f'Constant column: {col}',
                    'count': 1,
                    'severity': 'low',
                    'description': 'Column has only one unique value'
                })
        
        # Outliers in numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if df[col].notna().sum() > 0:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)][col].count()
                
                if outliers > len(df) * 0.05:  # More than 5% outliers
                    issues.append({
                        'type': f'Outliers in {col}',
                        'count': outliers,
                        'severity': 'medium',
                        'description': f'{(outliers/len(df)*100):.1f}% potential outliers'
                    })
        
        return issues
    
    @staticmethod
    def generate_column_insights(df):
        """Generate insights for each column"""
        insights = []
        
        for col in df.columns:
            col_data = df[col]
            insight = {
                'name': col,
                'dtype': str(col_data.dtype),
                'non_null_count': col_data.notna().sum(),
                'null_count': col_data.isnull().sum(),
                'null_percentage': (col_data.isnull().sum() / len(df)) * 100,
                'unique_count': col_data.nunique(),
                'memory_usage': col_data.memory_usage(deep=True)
            }
            
            # Type-specific insights
            if col_data.dtype in [np.number, 'int64', 'float64']:
                # Numerical column
                insight['type'] = 'numerical'
                if col_data.notna().sum() > 0:
                    insight['stats'] = {
                        'mean': float(col_data.mean()),
                        'median': float(col_data.median()),
                        'std': float(col_data.std()),
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                        'skewness': float(stats.skew(col_data.dropna())),
                        'kurtosis': float(stats.kurtosis(col_data.dropna()))
                    }
                    
                    # Check for outliers
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = col_data[(col_data < Q1 - 1.5 * IQR) | (col_data > Q3 + 1.5 * IQR)].count()
                    insight['outliers'] = outliers
                    
            elif col_data.dtype in ['object', 'category']:
                # Categorical column
                insight['type'] = 'categorical'
                if col_data.notna().sum() > 0:
                    value_counts = col_data.value_counts()
                    insight['top_values'] = value_counts.head(10).to_dict()
                    insight['cardinality'] = len(value_counts)
                    
                    # Check if it might be a date
                    sample_values = col_data.dropna().head(100)
                    date_like = 0
                    for val in sample_values:
                        try:
                            pd.to_datetime(val)
                            date_like += 1
                        except:
                            pass
                    
                    if date_like > len(sample_values) * 0.8:
                        insight['potential_date'] = True
            
            insights.append(insight)
        
        return insights
    
    @staticmethod
    def suggest_preprocessing_steps(df):
        """Suggest preprocessing steps based on data analysis"""
        suggestions = []
        
        # Check missing values
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            suggestions.append({
                'step': 'handle_missing_values',
                'priority': 'high',
                'description': f'Handle {missing_counts.sum()} missing values across {(missing_counts > 0).sum()} columns',
                'recommended_strategy': 'mean for numerical, mode for categorical'
            })
        
        # Check duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            suggestions.append({
                'step': 'remove_duplicates',
                'priority': 'high',
                'description': f'Remove {duplicates} duplicate rows',
                'recommended_strategy': 'drop_duplicates'
            })
        
        # Check for normalization needs
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 1:
            # Check if scales are very different
            ranges = {}
            for col in numerical_cols:
                if df[col].notna().sum() > 0:
                    ranges[col] = df[col].max() - df[col].min()
            
            if len(ranges) > 1:
                max_range = max(ranges.values())
                min_range = min(ranges.values())
                if max_range / min_range > 100:  # Very different scales
                    suggestions.append({
                        'step': 'normalize_data',
                        'priority': 'medium',
                        'description': 'Numerical features have very different scales',
                        'recommended_strategy': 'standard or minmax scaling'
                    })
        
        # Check for categorical encoding needs
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            suggestions.append({
                'step': 'encode_categorical',
                'priority': 'medium',
                'description': f'Encode {len(categorical_cols)} categorical columns for ML compatibility',
                'recommended_strategy': 'label encoding for ordinal, one-hot for nominal'
            })
        
        # Check for outliers
        for col in numerical_cols:
            if df[col].notna().sum() > 0:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)][col].count()
                
                if outliers > len(df) * 0.05:  # More than 5% outliers
                    suggestions.append({
                        'step': 'remove_outliers',
                        'priority': 'low',
                        'description': f'Column {col} has {outliers} potential outliers',
                        'recommended_strategy': 'IQR method or Z-score'
                    })
                    break  # Only suggest once
        
        return suggestions
