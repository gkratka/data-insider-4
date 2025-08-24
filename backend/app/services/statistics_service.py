import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, classification_report, silhouette_score
from scipy import stats
from scipy.stats import chi2_contingency, pearsonr, spearmanr
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import base64
import json

class StatisticsService:
    """
    Comprehensive statistical analysis service providing descriptive statistics,
    regression models, clustering algorithms, and statistical significance testing.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
    
    async def descriptive_statistics(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Calculate comprehensive descriptive statistics for dataset."""
        try:
            if columns:
                df = df[columns]
            
            # Separate numeric and categorical columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            result = {
                "summary": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "numeric_columns": len(numeric_cols),
                    "categorical_columns": len(categorical_cols),
                    "memory_usage": df.memory_usage(deep=True).sum(),
                    "missing_values": df.isnull().sum().to_dict()
                },
                "numeric_statistics": {},
                "categorical_statistics": {},
                "correlations": {},
                "distributions": {}
            }
            
            # Numeric statistics
            if numeric_cols:
                numeric_df = df[numeric_cols]
                result["numeric_statistics"] = {
                    "basic_stats": numeric_df.describe().to_dict(),
                    "skewness": numeric_df.skew().to_dict(),
                    "kurtosis": numeric_df.kurtosis().to_dict(),
                    "variance": numeric_df.var().to_dict(),
                    "quantiles": {
                        col: numeric_df[col].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).to_dict()
                        for col in numeric_cols
                    }
                }
                
                # Correlation matrix
                if len(numeric_cols) > 1:
                    corr_matrix = numeric_df.corr()
                    result["correlations"]["pearson"] = corr_matrix.to_dict()
                    result["correlations"]["spearman"] = numeric_df.corr(method='spearman').to_dict()
            
            # Categorical statistics
            if categorical_cols:
                result["categorical_statistics"] = {
                    col: {
                        "unique_values": df[col].nunique(),
                        "value_counts": df[col].value_counts().to_dict(),
                        "mode": df[col].mode().tolist()[0] if not df[col].mode().empty else None,
                        "missing_count": df[col].isnull().sum()
                    }
                    for col in categorical_cols
                }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error in descriptive statistics: {str(e)}")
    
    async def linear_regression_analysis(self, df: pd.DataFrame, target_column: str, 
                                       feature_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Perform linear regression analysis."""
        try:
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in dataset")
            
            # Select numeric columns for features if not specified
            if not feature_columns:
                feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                if target_column in feature_columns:
                    feature_columns.remove(target_column)
            
            # Prepare data
            X = df[feature_columns].dropna()
            y = df.loc[X.index, target_column]
            
            if len(X) < 2:
                raise ValueError("Insufficient data for regression analysis")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Fit model
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            # Calculate metrics
            train_r2 = r2_score(y_train, y_train_pred)
            test_r2 = r2_score(y_test, y_test_pred)
            
            result = {
                "model_type": "linear_regression",
                "target_column": target_column,
                "feature_columns": feature_columns,
                "coefficients": dict(zip(feature_columns, model.coef_)),
                "intercept": model.intercept_,
                "performance": {
                    "train_r2": train_r2,
                    "test_r2": test_r2,
                    "train_rmse": np.sqrt(np.mean((y_train - y_train_pred) ** 2)),
                    "test_rmse": np.sqrt(np.mean((y_test - y_test_pred) ** 2))
                },
                "feature_importance": dict(zip(feature_columns, np.abs(model.coef_))),
                "sample_predictions": {
                    "actual": y_test.head(10).tolist(),
                    "predicted": y_test_pred[:10].tolist()
                }
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error in linear regression: {str(e)}")
    
    async def logistic_regression_analysis(self, df: pd.DataFrame, target_column: str,
                                         feature_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Perform logistic regression analysis for classification."""
        try:
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' not found in dataset")
            
            # Select numeric columns for features if not specified
            if not feature_columns:
                feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
                if target_column in feature_columns:
                    feature_columns.remove(target_column)
            
            # Prepare data
            X = df[feature_columns].dropna()
            y = df.loc[X.index, target_column]
            
            # Encode target if categorical
            if y.dtype == 'object':
                y = self.label_encoder.fit_transform(y)
                classes = self.label_encoder.classes_
            else:
                classes = sorted(y.unique())
            
            if len(X) < 10 or len(np.unique(y)) < 2:
                raise ValueError("Insufficient data for logistic regression")
            
            # Split and scale data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Fit model
            model = LogisticRegression(random_state=42, max_iter=1000)
            model.fit(X_train_scaled, y_train)
            
            # Predictions
            train_pred = model.predict(X_train_scaled)
            test_pred = model.predict(X_test_scaled)
            train_proba = model.predict_proba(X_train_scaled)
            test_proba = model.predict_proba(X_test_scaled)
            
            result = {
                "model_type": "logistic_regression",
                "target_column": target_column,
                "feature_columns": feature_columns,
                "classes": classes.tolist() if hasattr(classes, 'tolist') else classes,
                "coefficients": dict(zip(feature_columns, model.coef_[0] if model.coef_.shape[0] == 1 else model.coef_)),
                "intercept": model.intercept_[0] if len(model.intercept_) == 1 else model.intercept_.tolist(),
                "performance": {
                    "train_accuracy": (train_pred == y_train).mean(),
                    "test_accuracy": (test_pred == y_test).mean(),
                    "classification_report": classification_report(y_test, test_pred, output_dict=True)
                },
                "feature_importance": dict(zip(feature_columns, np.abs(model.coef_[0]) if model.coef_.shape[0] == 1 else np.abs(model.coef_).mean(axis=0)))
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error in logistic regression: {str(e)}")
    
    async def clustering_analysis(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                                n_clusters: int = 3, method: str = "kmeans") -> Dict[str, Any]:
        """Perform clustering analysis using K-means or hierarchical clustering."""
        try:
            # Select numeric columns if not specified
            if not columns:
                columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not columns:
                raise ValueError("No numeric columns found for clustering")
            
            # Prepare data
            X = df[columns].dropna()
            if len(X) < n_clusters:
                raise ValueError(f"Insufficient data points ({len(X)}) for {n_clusters} clusters")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Perform clustering
            if method.lower() == "kmeans":
                model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            elif method.lower() == "hierarchical":
                model = AgglomerativeClustering(n_clusters=n_clusters)
            else:
                raise ValueError("Method must be 'kmeans' or 'hierarchical'")
            
            clusters = model.fit_predict(X_scaled)
            
            # Calculate silhouette score
            silhouette = silhouette_score(X_scaled, clusters) if len(np.unique(clusters)) > 1 else 0
            
            # Analyze clusters
            cluster_stats = {}
            for i in range(n_clusters):
                cluster_mask = clusters == i
                cluster_data = X[cluster_mask]
                cluster_stats[f"cluster_{i}"] = {
                    "size": int(cluster_mask.sum()),
                    "percentage": float(cluster_mask.mean() * 100),
                    "centroid": cluster_data.mean().to_dict(),
                    "std": cluster_data.std().to_dict()
                }
            
            result = {
                "method": method,
                "n_clusters": n_clusters,
                "feature_columns": columns,
                "cluster_assignments": clusters.tolist(),
                "silhouette_score": silhouette,
                "cluster_statistics": cluster_stats,
                "inertia": model.inertia_ if hasattr(model, 'inertia_') else None
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Error in clustering analysis: {str(e)}")
    
    async def statistical_tests(self, df: pd.DataFrame, test_type: str, **kwargs) -> Dict[str, Any]:
        """Perform various statistical significance tests."""
        try:
            result = {"test_type": test_type}
            
            if test_type == "correlation":
                col1 = kwargs.get("column1")
                col2 = kwargs.get("column2")
                method = kwargs.get("method", "pearson")
                
                if not col1 or not col2:
                    raise ValueError("Both column1 and column2 required for correlation test")
                
                x = df[col1].dropna()
                y = df[col2].dropna()
                common_idx = x.index.intersection(y.index)
                x, y = x[common_idx], y[common_idx]
                
                if method == "pearson":
                    corr_coef, p_value = pearsonr(x, y)
                elif method == "spearman":
                    corr_coef, p_value = spearmanr(x, y)
                else:
                    raise ValueError("Method must be 'pearson' or 'spearman'")
                
                result.update({
                    "correlation_coefficient": corr_coef,
                    "p_value": p_value,
                    "significant": p_value < 0.05,
                    "method": method,
                    "sample_size": len(x)
                })
            
            elif test_type == "t_test":
                group_col = kwargs.get("group_column")
                value_col = kwargs.get("value_column")
                
                if not group_col or not value_col:
                    raise ValueError("Both group_column and value_column required for t-test")
                
                groups = df.groupby(group_col)[value_col].apply(list).to_dict()
                group_names = list(groups.keys())
                
                if len(group_names) != 2:
                    raise ValueError("T-test requires exactly 2 groups")
                
                group1, group2 = groups[group_names[0]], groups[group_names[1]]
                t_stat, p_value = stats.ttest_ind(group1, group2)
                
                result.update({
                    "t_statistic": t_stat,
                    "p_value": p_value,
                    "significant": p_value < 0.05,
                    "group1": {"name": group_names[0], "mean": np.mean(group1), "size": len(group1)},
                    "group2": {"name": group_names[1], "mean": np.mean(group2), "size": len(group2)}
                })
            
            elif test_type == "chi_square":
                col1 = kwargs.get("column1")
                col2 = kwargs.get("column2")
                
                if not col1 or not col2:
                    raise ValueError("Both column1 and column2 required for chi-square test")
                
                contingency_table = pd.crosstab(df[col1], df[col2])
                chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                
                result.update({
                    "chi2_statistic": chi2,
                    "p_value": p_value,
                    "degrees_of_freedom": dof,
                    "significant": p_value < 0.05,
                    "contingency_table": contingency_table.to_dict(),
                    "expected_frequencies": pd.DataFrame(expected, 
                                                       index=contingency_table.index,
                                                       columns=contingency_table.columns).to_dict()
                })
            
            else:
                raise ValueError("Unsupported test type")
            
            return result
            
        except Exception as e:
            raise Exception(f"Error in statistical test: {str(e)}")
    
    async def generate_visualization(self, df: pd.DataFrame, chart_type: str, **kwargs) -> str:
        """Generate statistical visualizations and return as base64 encoded image."""
        try:
            plt.figure(figsize=(10, 6))
            
            if chart_type == "correlation_heatmap":
                numeric_df = df.select_dtypes(include=[np.number])
                if numeric_df.empty:
                    raise ValueError("No numeric columns found for correlation heatmap")
                
                corr_matrix = numeric_df.corr()
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
                plt.title("Correlation Heatmap")
                
            elif chart_type == "distribution":
                column = kwargs.get("column")
                if not column or column not in df.columns:
                    raise ValueError("Valid column required for distribution plot")
                
                if df[column].dtype in ['object', 'category']:
                    df[column].value_counts().plot(kind='bar')
                    plt.title(f"Distribution of {column}")
                    plt.xticks(rotation=45)
                else:
                    plt.hist(df[column].dropna(), bins=30, alpha=0.7, edgecolor='black')
                    plt.title(f"Distribution of {column}")
                    plt.xlabel(column)
                    plt.ylabel("Frequency")
                
            elif chart_type == "scatter":
                x_col = kwargs.get("x_column")
                y_col = kwargs.get("y_column")
                
                if not x_col or not y_col:
                    raise ValueError("Both x_column and y_column required for scatter plot")
                
                plt.scatter(df[x_col], df[y_col], alpha=0.6)
                plt.xlabel(x_col)
                plt.ylabel(y_col)
                plt.title(f"{y_col} vs {x_col}")
                
            else:
                raise ValueError("Unsupported chart type")
            
            # Save plot to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            plt.close()  # Ensure plot is closed on error
            raise Exception(f"Error generating visualization: {str(e)}")
    
    async def advanced_analysis_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Provide a comprehensive analysis summary with recommendations."""
        try:
            # Basic info
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            summary = {
                "dataset_overview": {
                    "shape": df.shape,
                    "numeric_columns": len(numeric_cols),
                    "categorical_columns": len(categorical_cols),
                    "missing_values_total": df.isnull().sum().sum(),
                    "duplicate_rows": df.duplicated().sum()
                },
                "data_quality": {},
                "statistical_insights": {},
                "recommendations": []
            }
            
            # Data quality assessment
            missing_percentage = (df.isnull().sum() / len(df) * 100)
            summary["data_quality"] = {
                "columns_with_missing": missing_percentage[missing_percentage > 0].to_dict(),
                "high_missing_columns": missing_percentage[missing_percentage > 50].index.tolist(),
                "data_completeness": (100 - missing_percentage.mean())
            }
            
            # Statistical insights
            if numeric_cols:
                numeric_df = df[numeric_cols]
                high_corr_pairs = []
                
                if len(numeric_cols) > 1:
                    corr_matrix = numeric_df.corr()
                    # Find high correlation pairs
                    for i in range(len(corr_matrix.columns)):
                        for j in range(i+1, len(corr_matrix.columns)):
                            corr_val = corr_matrix.iloc[i, j]
                            if abs(corr_val) > 0.7:
                                high_corr_pairs.append({
                                    "column1": corr_matrix.columns[i],
                                    "column2": corr_matrix.columns[j],
                                    "correlation": corr_val
                                })
                
                summary["statistical_insights"] = {
                    "highly_correlated_features": high_corr_pairs,
                    "skewed_distributions": {
                        col: numeric_df[col].skew() for col in numeric_cols 
                        if abs(numeric_df[col].skew()) > 1
                    },
                    "potential_outliers": {
                        col: len(numeric_df[col][
                            (numeric_df[col] < (numeric_df[col].quantile(0.25) - 1.5 * (numeric_df[col].quantile(0.75) - numeric_df[col].quantile(0.25)))) |
                            (numeric_df[col] > (numeric_df[col].quantile(0.75) + 1.5 * (numeric_df[col].quantile(0.75) - numeric_df[col].quantile(0.25))))
                        ]) for col in numeric_cols
                    }
                }
            
            # Generate recommendations
            recommendations = []
            
            if summary["data_quality"]["high_missing_columns"]:
                recommendations.append("Consider removing columns with >50% missing values or imputing missing data")
            
            if summary["dataset_overview"]["duplicate_rows"] > 0:
                recommendations.append(f"Remove {summary['dataset_overview']['duplicate_rows']} duplicate rows")
            
            if len(numeric_cols) >= 2:
                recommendations.append("Consider correlation analysis and regression modeling")
            
            if len(numeric_cols) >= 3:
                recommendations.append("Dataset suitable for clustering analysis")
            
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                recommendations.append("Explore relationships between categorical and numeric variables")
            
            summary["recommendations"] = recommendations
            
            return summary
            
        except Exception as e:
            raise Exception(f"Error in advanced analysis summary: {str(e)}")