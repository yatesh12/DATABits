from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import io
import json
import uuid
import os
import threading
import time
from datetime import datetime
from functools import wraps
import logging
from werkzeug.exceptions import RequestEntityTooLarge
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer, KNNImputer
import warnings
warnings.filterwarnings('ignore')

# Configure logging to reduce verbosity
logging.basicConfig(
    level=logging.WARNING,  # Changed from INFO to WARNING
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Disable werkzeug logging for requests
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Thread-safe storage
datasets = {}
processing_status = {}
dataset_lock = threading.Lock()
# Add cache for random samples to prevent regeneration
random_sample_cache = {}

class ProcessingStatus:
    def __init__(self):
        self.status = "idle"  # idle, processing, completed, error
        self.progress = 0
        self.message = ""
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None

def standardize_response(success=True, data=None, message="", error=None, status_code=200):
    """Standardize all API responses"""
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        response["data"] = data
    else:
        response["error"] = error or message
        
    return jsonify(response), status_code

def handle_errors(f):
    """Decorator for consistent error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error in {f.__name__}: {str(e)}")
            return standardize_response(False, error=f"Validation error: {str(e)}", status_code=400)
        except FileNotFoundError as e:
            logger.error(f"File not found in {f.__name__}: {str(e)}")
            return standardize_response(False, error="Dataset not found", status_code=404)
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return standardize_response(False, error="Internal server error", status_code=500)
    return decorated_function

def validate_dataset_exists(dataset_id):
    """Validate that dataset exists"""
    if dataset_id not in datasets:
        raise FileNotFoundError(f"Dataset {dataset_id} not found")
    return datasets[dataset_id]

def safe_convert_to_json(obj):
    """Safely convert numpy/pandas objects to JSON serializable format"""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: safe_convert_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_convert_to_json(item) for item in obj]
    else:
        return obj

class EnhancedDataPreprocessor:
    def __init__(self, df, dataset_id):
        self.df = df.copy()
        self.original_df = df.copy()
        self.dataset_id = dataset_id
        self.operations_log = []
        self.processing_status = ProcessingStatus()
        # Cache for random samples
        self.cached_random_sample = None
        self.random_sample_timestamp = None
        
    def get_random_sample(self, n=5, force_refresh=False):
        """Get cached random sample or generate new one"""
        current_time = datetime.now()
        
        # Check if we need to refresh the cache (force refresh or cache is older than 30 seconds)
        if (force_refresh or 
            self.cached_random_sample is None or 
            self.random_sample_timestamp is None or
            (current_time - self.random_sample_timestamp).seconds > 30):
            
            # Generate new random sample
            sample_size = min(n, len(self.df))
            if sample_size > 0:
                # Use timestamp as seed for different results each time cache refreshes
                random_seed = int(current_time.timestamp() * 1000000) % 2**32
                self.cached_random_sample = self.df.sample(n=sample_size, random_state=random_seed)
                self.random_sample_timestamp = current_time
                logger.info(f"Generated new random sample for dataset {self.dataset_id}")
            else:
                self.cached_random_sample = self.df.head(0)
        
        return self.cached_random_sample
        
    def update_status(self, status, progress=None, message=""):
        """Update processing status"""
        with dataset_lock:
            self.processing_status.status = status
            if progress is not None:
                self.processing_status.progress = progress
            self.processing_status.message = message
            processing_status[self.dataset_id] = {
                "status": status,
                "progress": progress or self.processing_status.progress,
                "message": message
            }
    
    def validate_columns(self, columns, required_type=None):
        """Validate column names and types"""
        if columns is None:
            return list(self.df.columns)
        
        invalid_columns = [col for col in columns if col not in self.df.columns]
        if invalid_columns:
            raise ValueError(f"Invalid columns: {invalid_columns}")
        
        if required_type:
            if required_type == 'numeric':
                invalid_types = [col for col in columns 
                               if not pd.api.types.is_numeric_dtype(self.df[col])]
            elif required_type == 'categorical':
                invalid_types = [col for col in columns 
                               if pd.api.types.is_numeric_dtype(self.df[col])]
            else:
                invalid_types = []
                
            if invalid_types:
                raise ValueError(f"Columns {invalid_types} are not {required_type}")
        
        return columns
    
    def handle_missing_values(self, strategy='mean', columns=None):
        """Handle missing values with progress tracking"""
        self.update_status("processing", 0, "Starting missing value imputation...")
        
        columns = self.validate_columns(columns)
        results = {}
        total_columns = len(columns)
        
        for i, col in enumerate(columns):
            progress = int((i / total_columns) * 100)
            self.update_status("processing", progress, f"Processing column: {col}")
            
            missing_count_before = self.df[col].isnull().sum()
            
            if missing_count_before == 0:
                results[col] = {'status': 'no_missing', 'filled': 0}
                continue
            
            try:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    # Numerical data
                    if strategy == 'mean':
                        fill_value = self.df[col].mean()
                    elif strategy == 'median':
                        fill_value = self.df[col].median()
                    elif strategy == 'mode':
                        mode_series = self.df[col].mode()
                        fill_value = mode_series.iloc[0] if not mode_series.empty else 0
                    elif strategy == 'constant':
                        fill_value = 0
                    elif strategy == 'knn':
                        # KNN imputation
                        imputer = KNNImputer(n_neighbors=min(5, len(self.df) - 1))
                        self.df[col] = imputer.fit_transform(self.df[[col]]).flatten()
                        fill_value = None
                    else:
                        fill_value = self.df[col].mean()
                    
                    if fill_value is not None:
                        self.df[col].fillna(fill_value, inplace=True)
                else:
                    # Categorical data
                    if strategy == 'mode':
                        mode_series = self.df[col].mode()
                        fill_value = mode_series.iloc[0] if not mode_series.empty else 'Unknown'
                    elif strategy == 'constant':
                        fill_value = 'Unknown'
                    else:
                        # Forward fill for categorical
                        self.df[col].fillna(method='ffill', inplace=True)
                        fill_value = 'Unknown'
                    
                    if fill_value is not None:
                        self.df[col].fillna(fill_value, inplace=True)
                
                missing_count_after = self.df[col].isnull().sum()
                filled_count = missing_count_before - missing_count_after
                
                results[col] = {
                    'status': 'filled',
                    'filled': int(filled_count),
                    'strategy': strategy,
                    'fill_value': safe_convert_to_json(fill_value) if fill_value is not None else None
                }
                
            except Exception as e:
                logger.error(f"Error processing column {col}: {str(e)}")
                results[col] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Clear random sample cache when data changes
        self.cached_random_sample = None
        self.random_sample_timestamp = None
        
        self.update_status("completed", 100, "Missing value imputation completed")
        
        # Log operation
        operation_log = {
            'operation': 'handle_missing_values',
            'strategy': strategy,
            'columns': columns,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        self.operations_log.append(operation_log)
        
        return results
    
    def encode_categorical(self, method='label', columns=None):
        """Encode categorical variables with progress tracking"""
        self.update_status("processing", 0, "Starting categorical encoding...")
        
        if columns is None:
            columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        else:
            columns = self.validate_columns(columns, 'categorical')
        
        results = {}
        total_columns = len(columns)
        
        for i, col in enumerate(columns):
            progress = int((i / total_columns) * 100)
            self.update_status("processing", progress, f"Encoding column: {col}")
            
            try:
                unique_values = self.df[col].nunique()
                
                if method == 'label':
                    le = LabelEncoder()
                    # Handle NaN values
                    mask = self.df[col].notna()
                    if mask.sum() > 0:
                        self.df.loc[mask, col] = le.fit_transform(self.df.loc[mask, col])
                        results[col] = {
                            'status': 'success',
                            'method': 'label',
                            'unique_values': unique_values,
                            'classes': le.classes_.tolist()
                        }
                    else:
                        results[col] = {
                            'status': 'skipped',
                            'reason': 'all_null'
                        }
                        
                elif method == 'onehot':
                    # One-hot encoding
                    if unique_values <= 20:  # Reasonable limit for one-hot
                        dummies = pd.get_dummies(self.df[col], prefix=col, dummy_na=True)
                        self.df = pd.concat([self.df.drop(col, axis=1), dummies], axis=1)
                        results[col] = {
                            'status': 'success',
                            'method': 'onehot',
                            'unique_values': unique_values,
                            'new_columns': dummies.columns.tolist()
                        }
                    else:
                        results[col] = {
                            'status': 'skipped',
                            'reason': 'too_many_categories',
                            'unique_values': unique_values,
                            'recommendation': 'Use label encoding or reduce categories'
                        }
                        
            except Exception as e:
                logger.error(f"Error encoding column {col}: {str(e)}")
                results[col] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Clear random sample cache when data changes
        self.cached_random_sample = None
        self.random_sample_timestamp = None
        
        self.update_status("completed", 100, "Categorical encoding completed")
        
        # Log operation
        operation_log = {
            'operation': 'encode_categorical',
            'method': method,
            'columns': columns,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        self.operations_log.append(operation_log)
        
        return results
    
    def remove_outliers(self, method='iqr', columns=None, threshold=1.5):
        """Remove outliers with progress tracking"""
        self.update_status("processing", 0, "Starting outlier removal...")
        
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        else:
            columns = self.validate_columns(columns, 'numeric')
        
        results = {}
        initial_rows = len(self.df)
        total_columns = len(columns)
        
        for i, col in enumerate(columns):
            progress = int((i / total_columns) * 100)
            self.update_status("processing", progress, f"Processing column: {col}")
            
            try:
                if method == 'iqr':
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    
                    outliers_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                    outliers_count = outliers_mask.sum()
                    
                    self.df = self.df[~outliers_mask]
                    
                elif method == 'zscore':
                    z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                    outliers_mask = z_scores > threshold
                    outliers_count = outliers_mask.sum()
                    
                    self.df = self.df[~outliers_mask]
                
                results[col] = {
                    'status': 'success',
                    'method': method,
                    'outliers_removed': int(outliers_count),
                    'threshold': threshold
                }
                
            except Exception as e:
                logger.error(f"Error removing outliers from column {col}: {str(e)}")
                results[col] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        final_rows = len(self.df)
        total_removed = initial_rows - final_rows
        
        # Clear random sample cache when data changes
        self.cached_random_sample = None
        self.random_sample_timestamp = None
        
        self.update_status("completed", 100, f"Outlier removal completed. Removed {total_removed} rows")
        
        # Log operation
        operation_log = {
            'operation': 'remove_outliers',
            'method': method,
            'columns': columns,
            'threshold': threshold,
            'total_rows_removed': total_removed,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        self.operations_log.append(operation_log)
        
        return {'total_removed': total_removed, 'column_results': results}
    
    def remove_duplicates(self):
        """Remove duplicate rows with progress tracking"""
        self.update_status("processing", 50, "Removing duplicate rows...")
        
        initial_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        final_rows = len(self.df)
        removed_count = initial_rows - final_rows
        
        # Clear random sample cache when data changes
        self.cached_random_sample = None
        self.random_sample_timestamp = None
        
        result = {
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_count': removed_count
        }
        
        self.update_status("completed", 100, f"Removed {removed_count} duplicate rows")
        
        # Log operation
        operation_log = {
            'operation': 'remove_duplicates',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        self.operations_log.append(operation_log)
        
        return result

@app.route('/api/dataset/<dataset_id>/outliers', methods=['POST'])
@handle_errors
def remove_outliers(dataset_id):
    """Remove outliers from dataset"""
    preprocessor = validate_dataset_exists(dataset_id)
    
    data = request.get_json() or {}
    method = data.get('method', 'iqr')
    columns = data.get('columns', None)
    threshold = float(data.get('threshold', 1.5))
    async_processing = data.get('async', False)
    
    # Validate method
    valid_methods = ['iqr', 'zscore']
    if method not in valid_methods:
        return standardize_response(False, error=f'Invalid method. Must be one of: {valid_methods}', status_code=400)
    
    # Validate threshold
    if threshold <= 0:
        return standardize_response(False, error='Threshold must be positive', status_code=400)
    
    if async_processing:
        run_async_operation(
            lambda p: p.remove_outliers(method, columns, threshold),
            dataset_id
        )
        return standardize_response(True, {
            'processing': True,
            'message': 'Processing started. Check status endpoint for progress.'
        }, 'Outlier removal started')
    else:
        results = preprocessor.remove_outliers(method, columns, threshold)
        summary = preprocessor.get_comprehensive_summary()
        
        return standardize_response(True, {
            'results': results,
            'summary': summary
        }, f'Outliers removed using {method} method')

@app.route('/api/dataset/<dataset_id>/duplicates', methods=['DELETE'])
@handle_errors
def remove_duplicates(dataset_id):
    """Remove duplicate rows"""
    preprocessor = validate_dataset_exists(dataset_id)
    
    results = preprocessor.remove_duplicates()
    summary = preprocessor.get_comprehensive_summary()
    
    return standardize_response(True, {
        'results': results,
        'summary': summary
    }, f'Removed {results["removed_count"]} duplicate rows')

@app.route('/api/dataset/<dataset_id>/correlation', methods=['GET'])
@handle_errors
def get_correlation_analysis(dataset_id):
    """Get correlation analysis for numerical columns"""
    preprocessor = validate_dataset_exists(dataset_id)
    df = preprocessor.df
    
    # Get numerical columns
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numerical_cols) < 2:
        return standardize_response(True, {
            'numericalColumns': numerical_cols,
            'correlationMatrix': [],
            'strongCorrelations': [],
            'insights': ['Not enough numerical columns for correlation analysis. Need at least 2 numerical columns.']
        }, 'Insufficient numerical columns for correlation analysis')
    
    # Calculate correlation matrix
    corr_matrix = df[numerical_cols].corr()
    
    # Convert to the format expected by frontend
    correlation_matrix = []
    for i, col1 in enumerate(numerical_cols):
        row = []
        for j, col2 in enumerate(numerical_cols):
            corr_value = corr_matrix.iloc[i, j]
            if pd.isna(corr_value):
                corr_value = 0
            
            abs_corr = abs(corr_value)
            if abs_corr >= 0.7:
                strength = "strong"
            elif abs_corr >= 0.5:
                strength = "moderate"
            else:
                strength = "weak"
            
            row.append({
                'value': safe_convert_to_json(corr_value),
                'strength': strength,
                'col1': col1,
                'col2': col2
            })
        correlation_matrix.append(row)
    
    # Find strong correlations
    strong_correlations = []
    for i in range(len(numerical_cols)):
        for j in range(i + 1, len(numerical_cols)):
            corr_value = correlation_matrix[i][j]['value']
            if abs(corr_value) >= 0.5:
                strong_correlations.append({
                    'col1': numerical_cols[i],
                    'col2': numerical_cols[j],
                    'correlation': corr_value,
                    'strength': correlation_matrix[i][j]['strength'],
                    'direction': 'positive' if corr_value > 0 else 'negative'
                })
    
    # Generate insights
    insights = []
    if len(strong_correlations) == 0:
        insights.append("No strong correlations found between variables.")
    else:
        insights.append(f"Found {len(strong_correlations)} strong correlation(s).")
        for corr in strong_correlations[:3]:
            insights.append(
                f"{corr['col1']} and {corr['col2']} have a {corr['strength']} {corr['direction']} correlation ({corr['correlation']:.3f})."
            )
    
    return standardize_response(True, {
        'numericalColumns': numerical_cols,
        'correlationMatrix': correlation_matrix,
        'strongCorrelations': strong_correlations,
        'insights': insights
    }, 'Correlation analysis completed successfully')

@app.route('/api/dataset/<dataset_id>/export', methods=['GET'])
@handle_errors
def export_dataset(dataset_id):
    """Export processed dataset as CSV"""
    preprocessor = validate_dataset_exists(dataset_id)
    df = preprocessor.df
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    # Convert to bytes
    csv_data = io.BytesIO()
    csv_data.write(output.getvalue().encode('utf-8'))
    csv_data.seek(0)
    
    return send_file(
        csv_data,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'processed_data_{dataset_id[:8]}.csv'
    )

@app.route('/api/dataset/<dataset_id>/reset', methods=['POST'])
@handle_errors
def reset_dataset(dataset_id):
    """Reset dataset to original state"""
    preprocessor = validate_dataset_exists(dataset_id)
    
    with dataset_lock:
        preprocessor.df = preprocessor.original_df.copy()
        preprocessor.operations_log = []
        # Clear random sample cache when resetting
        preprocessor.cached_random_sample = None
        preprocessor.random_sample_timestamp = None
        preprocessor.update_status("idle", 0, "Dataset reset to original state")
    
    summary = preprocessor.get_comprehensive_summary()
    
    return standardize_response(True, {
        'summary': summary
    }, 'Dataset reset to original state')

@app.route('/api/dataset/<dataset_id>/history', methods=['GET'])
@handle_errors
def get_processing_history(dataset_id):
    """Get processing history for dataset"""
    preprocessor = validate_dataset_exists(dataset_id)
    
    return standardize_response(True, {
        'operations': preprocessor.operations_log,
        'total_operations': len(preprocessor.operations_log)
    }, 'Processing history retrieved successfully')

# Error handlers
@app.errorhandler(413)
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return standardize_response(False, error='File too large. Maximum size is 50MB.', status_code=413)

@app.errorhandler(404)
def handle_not_found(e):
    return standardize_response(False, error='Endpoint not found', status_code=404)

@app.errorhandler(500)
def handle_internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return standardize_response(False, error='Internal server error', status_code=500)

if __name__ == '__main__':
    print("Starting Data Preprocessing API Server...")
    print("Server running on http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    print("Random sample caching enabled - samples refresh every 30 seconds")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
