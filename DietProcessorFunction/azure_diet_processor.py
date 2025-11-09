import pandas as pd
import numpy as np
import os
import io
import logging
from typing import Dict, List, Optional, Union
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError


class AzureDietDataProcessor:
    """
    Azure-compatible version of DietDataProcessor that reads data from Azure Blob Storage
    """

    def __init__(
        self, connection_string: Optional[str] = None, container_name: str = "diet-data"
    ):
        """
        Initialize the Azure Diet Data Processor

        Args:
            connection_string: Azure Storage connection string (if None, uses environment variable)
            container_name: Name of the blob container containing the data
        """
        self.data = None
        self.container_name = container_name
        self.blob_name = "All_Diets.csv"

        # Get connection string from parameter or environment variable
        self.connection_string = connection_string or os.getenv("AzureWebJobsStorage")

        if not self.connection_string:
            raise ValueError(
                "Azure Storage connection string must be provided either as parameter or AzureWebJobsStorage environment variable"
            )

        # Initialize blob service client
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
        except Exception as e:
            logging.error(f"Failed to initialize blob service client: {e}")
            raise

    def load_data_from_blob(self, blob_name: Optional[str] = None) -> bool:
        """
        Load diet data from Azure Blob Storage

        Args:
            blob_name: Name of the blob file (defaults to All_Diets.csv)

        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            blob_name = blob_name or self.blob_name

            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            # Download blob content
            logging.info(
                f"Downloading blob: {blob_name} from container: {self.container_name}"
            )
            blob_data = blob_client.download_blob().readall()

            # Load into pandas DataFrame
            self.data = pd.read_csv(io.BytesIO(blob_data))
            logging.info(
                f"Successfully loaded {len(self.data)} records from blob storage"
            )

            # Clean the data
            self._clean_data()
            return True

        except ResourceNotFoundError:
            logging.error(
                f"Blob {blob_name} not found in container {self.container_name}"
            )
            return False
        except Exception as e:
            logging.error(f"Error loading data from blob storage: {e}")
            return False

    def load_data_from_content(self, content: bytes) -> bool:
        """
        Load diet data from blob content (useful for blob triggers)

        Args:
            content: Raw blob content as bytes

        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            self.data = pd.read_csv(io.BytesIO(content))
            logging.info(
                f"Successfully loaded {len(self.data)} records from blob content"
            )

            # Clean the data
            self._clean_data()
            return True

        except Exception as e:
            logging.error(f"Error loading data from blob content: {e}")
            return False

    def upload_results_to_blob(
        self, data: Union[Dict, List], blob_name: str, format_type: str = "json"
    ) -> bool:
        """
        Upload processed results back to blob storage

        Args:
            data: Data to upload
            blob_name: Name for the result blob
            format_type: Format to save data in ('json' or 'csv')

        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            if format_type.lower() == "json":
                import json

                content = json.dumps(data, indent=2)
                content_type = "application/json"
            elif format_type.lower() == "csv" and isinstance(data, list):
                df = pd.DataFrame(data)
                content = df.to_csv(index=False)
                content_type = "text/csv"
            else:
                raise ValueError("Unsupported format type or data structure")

            blob_client.upload_blob(content, overwrite=True, content_type=content_type)
            logging.info(f"Successfully uploaded results to blob: {blob_name}")
            return True

        except Exception as e:
            logging.error(f"Error uploading results to blob storage: {e}")
            return False

    def _clean_data(self):
        """Clean and prepare the dataset"""
        if self.data is None:
            return

        logging.info("Cleaning data...")

        # Fill missing numeric values with mean
        numeric_cols = ["Protein(g)", "Carbs(g)", "Fat(g)"]
        for col in numeric_cols:
            if col in self.data.columns:
                mean_val = self.data[col].mean()
                self.data[col] = self.data[col].fillna(mean_val)

        # Fill missing categorical values
        categorical_cols = ["Diet_type", "Cuisine_type"]
        for col in categorical_cols:
            if col in self.data.columns:
                mode_value = self.data[col].mode()
                fill_value = mode_value[0] if len(mode_value) > 0 else "Unknown"
                self.data[col] = self.data[col].fillna(fill_value)

        logging.info("Data cleaning completed")

    def get_macronutrient_averages(self) -> Dict[str, Dict[str, float]]:
        """Get average macronutrient content by diet type"""
        if self.data is None:
            logging.warning("No data loaded")
            return {}

        macro_cols = ["Protein(g)", "Carbs(g)", "Fat(g)"]
        available_cols = [col for col in macro_cols if col in self.data.columns]

        if "Diet_type" not in self.data.columns or not available_cols:
            logging.warning("Required columns not found in data")
            return {}

        result = {}
        for diet_type in self.data["Diet_type"].unique():
            diet_data = self.data[self.data["Diet_type"] == diet_type]
            averages = {}
            for col in available_cols:
                averages[col.replace("(g)", "")] = round(diet_data[col].mean(), 2)
            result[diet_type] = averages

        return result

    def get_diet_comparison_data(self) -> List[Dict]:
        """Get comparison data between different diet types"""
        averages = self.get_macronutrient_averages()
        comparison_data = []

        for diet_type, macros in averages.items():
            diet_info = {
                "diet_type": diet_type,
                "protein": macros.get("Protein", 0),
                "carbs": macros.get("Carbs", 0),
                "fat": macros.get("Fat", 0),
                "total_recipes": len(self.data[self.data["Diet_type"] == diet_type]),
            }
            comparison_data.append(diet_info)

        return comparison_data

    def get_top_recipes_by_nutrient(
        self, nutrient: str = "Protein", n: int = 10
    ) -> List[Dict]:
        """Get top N recipes by specified nutrient content"""
        if self.data is None:
            return []

        nutrient_col = f"{nutrient}(g)"
        if nutrient_col not in self.data.columns:
            logging.warning(f"Nutrient column {nutrient_col} not found")
            return []

        top_recipes = self.data.nlargest(n, nutrient_col)

        result = []
        for _, recipe in top_recipes.iterrows():
            recipe_info = {
                "recipe_name": recipe.get("Recipe_name", "Unknown"),
                "diet_type": recipe.get("Diet_type", "Unknown"),
                "cuisine_type": recipe.get("Cuisine_type", "Unknown"),
                "nutrient_value": round(recipe[nutrient_col], 2),
                "nutrient_type": nutrient,
            }
            result.append(recipe_info)

        return result

    def get_cuisine_distribution(self) -> Dict[str, Dict[str, int]]:
        """Get cuisine distribution by diet type"""
        if (
            self.data is None
            or "Diet_type" not in self.data.columns
            or "Cuisine_type" not in self.data.columns
        ):
            return {}

        result = {}
        for diet_type in self.data["Diet_type"].unique():
            diet_data = self.data[self.data["Diet_type"] == diet_type]
            cuisine_counts = diet_data["Cuisine_type"].value_counts().to_dict()
            result[diet_type] = cuisine_counts

        return result

    def get_nutrient_ranges(self) -> Dict[str, Dict[str, float]]:
        """Get min, max, and average values for each nutrient"""
        if self.data is None:
            return {}

        nutrient_cols = ["Protein(g)", "Carbs(g)", "Fat(g)"]
        result = {}

        for col in nutrient_cols:
            if col in self.data.columns:
                nutrient_name = col.replace("(g)", "")
                result[nutrient_name] = {
                    "min": round(self.data[col].min(), 2),
                    "max": round(self.data[col].max(), 2),
                    "average": round(self.data[col].mean(), 2),
                    "median": round(self.data[col].median(), 2),
                }

        return result

    def get_diet_summary(self) -> Dict:
        """Get overall summary statistics"""
        if self.data is None:
            return {}

        return {
            "total_recipes": len(self.data),
            "total_diet_types": (
                self.data["Diet_type"].nunique()
                if "Diet_type" in self.data.columns
                else 0
            ),
            "total_cuisine_types": (
                self.data["Cuisine_type"].nunique()
                if "Cuisine_type" in self.data.columns
                else 0
            ),
            "diet_types": (
                self.data["Diet_type"].unique().tolist()
                if "Diet_type" in self.data.columns
                else []
            ),
            "most_common_diet": (
                self.data["Diet_type"].mode()[0]
                if "Diet_type" in self.data.columns
                and len(self.data["Diet_type"].mode()) > 0
                else "Unknown"
            ),
            "most_common_cuisine": (
                self.data["Cuisine_type"].mode()[0]
                if "Cuisine_type" in self.data.columns
                and len(self.data["Cuisine_type"].mode()) > 0
                else "Unknown"
            ),
        }

    def get_recipes_by_diet_type(self, diet_type: str) -> List[Dict]:
        """Get all recipes for a specific diet type"""
        if self.data is None or "Diet_type" not in self.data.columns:
            return []

        diet_recipes = self.data[self.data["Diet_type"] == diet_type]

        result = []
        for _, recipe in diet_recipes.iterrows():
            recipe_info = {
                "recipe_name": recipe.get("Recipe_name", "Unknown"),
                "cuisine_type": recipe.get("Cuisine_type", "Unknown"),
                "protein": round(recipe.get("Protein(g)", 0), 2),
                "carbs": round(recipe.get("Carbs(g)", 0), 2),
                "fat": round(recipe.get("Fat(g)", 0), 2),
            }
            result.append(recipe_info)

        return result

    def search_recipes(
        self, search_term: str, search_field: str = "Recipe_name"
    ) -> List[Dict]:
        """Search for recipes by name or other fields"""
        if self.data is None or search_field not in self.data.columns:
            return []

        # Case-insensitive search
        matching_recipes = self.data[
            self.data[search_field].str.contains(search_term, case=False, na=False)
        ]

        result = []
        for _, recipe in matching_recipes.iterrows():
            recipe_info = {
                "recipe_name": recipe.get("Recipe_name", "Unknown"),
                "diet_type": recipe.get("Diet_type", "Unknown"),
                "cuisine_type": recipe.get("Cuisine_type", "Unknown"),
                "protein": round(recipe.get("Protein(g)", 0), 2),
                "carbs": round(recipe.get("Carbs(g)", 0), 2),
                "fat": round(recipe.get("Fat(g)", 0), 2),
            }
            result.append(recipe_info)

        return result

    # ===== NEW ENHANCED METHODS FOR FRONTEND DASHBOARD =====

    def get_nutritional_insights(self) -> Dict:
        """Get comprehensive nutritional insights for the main dashboard API"""
        if self.data is None:
            return {"error": "No data available"}

        return {
            "summary": self.get_diet_summary(),
            "macronutrients": self.get_macronutrient_averages(),
            "nutrient_ranges": self.get_nutrient_ranges(),
            "diet_distribution": self.get_pie_chart_data(),
            "top_protein_recipes": self.get_top_recipes_by_nutrient("Protein", 5),
            "correlations": self.get_nutrient_correlations(),
            "timestamp": pd.Timestamp.now().isoformat(),
        }

    def get_chart_data(self, chart_type: str) -> Dict:
        """Get data formatted for specific chart types"""
        if self.data is None:
            return {"error": "No data available"}

        chart_type = chart_type.lower()

        if chart_type == "bar":
            return self.get_bar_chart_data()
        elif chart_type == "scatter":
            return self.get_scatter_plot_data("Protein", "Carbs")
        elif chart_type == "heatmap":
            return self.get_heatmap_data()
        elif chart_type == "pie":
            return self.get_pie_chart_data()
        else:
            return {"error": f"Unsupported chart type: {chart_type}"}

    def get_recipes_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        diet_type: str = "",
        search_term: str = "",
    ) -> Dict:
        """Get paginated recipes with filtering"""
        if self.data is None:
            return {"error": "No data available"}

        # Start with all data
        filtered_data = self.data.copy()

        # Apply diet type filter
        if diet_type and "Diet_type" in filtered_data.columns:
            filtered_data = filtered_data[
                filtered_data["Diet_type"].str.contains(diet_type, case=False, na=False)
            ]

        # Apply search filter
        if search_term and "Recipe_name" in filtered_data.columns:
            filtered_data = filtered_data[
                filtered_data["Recipe_name"].str.contains(
                    search_term, case=False, na=False
                )
            ]

        # Calculate pagination
        total_recipes = len(filtered_data)
        total_pages = (total_recipes + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        # Get page data
        page_data = filtered_data.iloc[start_idx:end_idx]

        recipes = []
        for _, recipe in page_data.iterrows():
            recipe_info = {
                "recipe_name": recipe.get("Recipe_name", "Unknown"),
                "diet_type": recipe.get("Diet_type", "Unknown"),
                "cuisine_type": recipe.get("Cuisine_type", "Unknown"),
                "protein": round(recipe.get("Protein(g)", 0), 2),
                "carbs": round(recipe.get("Carbs(g)", 0), 2),
                "fat": round(recipe.get("Fat(g)", 0), 2),
            }
            recipes.append(recipe_info)

        return {
            "recipes": recipes,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_recipes": total_recipes,
                "page_size": page_size,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            },
            "filters": {"diet_type": diet_type, "search_term": search_term},
        }

    def get_recipe_clusters(self) -> Dict:
        """Get recipe clusters based on nutritional similarity"""
        if self.data is None:
            return {"error": "No data available"}

        try:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler

            # Prepare data for clustering
            features = ["Protein(g)", "Carbs(g)", "Fat(g)"]
            available_features = [f for f in features if f in self.data.columns]

            if len(available_features) < 2:
                return {"error": "Insufficient nutrition data for clustering"}

            cluster_data = self.data[available_features].dropna()

            # Normalize the data
            scaler = StandardScaler()
            normalized_data = scaler.fit_transform(cluster_data)

            # Perform clustering
            n_clusters = min(
                5, len(cluster_data) // 10
            )  # Reasonable number of clusters
            if n_clusters < 2:
                n_clusters = 2

            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(normalized_data)

            # Analyze clusters
            clusters = {}
            for i in range(n_clusters):
                cluster_indices = cluster_data.index[cluster_labels == i]
                cluster_recipes = self.data.loc[cluster_indices]

                cluster_info = {
                    "cluster_id": i,
                    "size": len(cluster_recipes),
                    "avg_protein": (
                        round(cluster_recipes["Protein(g)"].mean(), 2)
                        if "Protein(g)" in cluster_recipes.columns
                        else 0
                    ),
                    "avg_carbs": (
                        round(cluster_recipes["Carbs(g)"].mean(), 2)
                        if "Carbs(g)" in cluster_recipes.columns
                        else 0
                    ),
                    "avg_fat": (
                        round(cluster_recipes["Fat(g)"].mean(), 2)
                        if "Fat(g)" in cluster_recipes.columns
                        else 0
                    ),
                    "common_diet_types": (
                        cluster_recipes["Diet_type"].value_counts().head(3).to_dict()
                        if "Diet_type" in cluster_recipes.columns
                        else {}
                    ),
                    "sample_recipes": (
                        cluster_recipes["Recipe_name"].head(5).tolist()
                        if "Recipe_name" in cluster_recipes.columns
                        else []
                    ),
                }
                clusters[f"cluster_{i}"] = cluster_info

            return {
                "clusters": clusters,
                "total_clusters": n_clusters,
                "features_used": available_features,
                "clustering_method": "K-Means",
            }

        except ImportError:
            # Fallback if sklearn is not available
            return self._simple_recipe_grouping()

    def _simple_recipe_grouping(self) -> Dict:
        """Simple recipe grouping by diet type when sklearn is unavailable"""
        if "Diet_type" not in self.data.columns:
            return {"error": "No diet type data available for grouping"}

        groups = {}
        for diet_type in self.data["Diet_type"].unique():
            diet_data = self.data[self.data["Diet_type"] == diet_type]

            group_info = {
                "group_name": diet_type,
                "size": len(diet_data),
                "avg_protein": (
                    round(diet_data["Protein(g)"].mean(), 2)
                    if "Protein(g)" in diet_data.columns
                    else 0
                ),
                "avg_carbs": (
                    round(diet_data["Carbs(g)"].mean(), 2)
                    if "Carbs(g)" in diet_data.columns
                    else 0
                ),
                "avg_fat": (
                    round(diet_data["Fat(g)"].mean(), 2)
                    if "Fat(g)" in diet_data.columns
                    else 0
                ),
                "sample_recipes": (
                    diet_data["Recipe_name"].head(5).tolist()
                    if "Recipe_name" in diet_data.columns
                    else []
                ),
            }
            groups[diet_type.replace(" ", "_")] = group_info

        return {
            "groups": groups,
            "grouping_method": "By Diet Type",
            "note": "Using simple diet type grouping",
        }

    def get_diet_types(self) -> Dict:
        """Get available diet types for filter dropdown"""
        if self.data is None or "Diet_type" not in self.data.columns:
            return {"diet_types": []}

        diet_types = self.data["Diet_type"].dropna().unique().tolist()
        diet_counts = self.data["Diet_type"].value_counts().to_dict()

        return {
            "diet_types": sorted(diet_types),
            "diet_counts": diet_counts,
            "total_types": len(diet_types),
        }

    def get_bar_chart_data(self) -> Dict:
        """Get data formatted for bar chart: Average macronutrient content by diet type"""
        macros = self.get_macronutrient_averages()

        if not macros:
            return {"error": "No macronutrient data available"}

        # Format for Chart.js bar chart
        labels = list(macros.keys())
        protein_data = [macros[diet].get("Protein", 0) for diet in labels]
        carbs_data = [macros[diet].get("Carbs", 0) for diet in labels]
        fat_data = [macros[diet].get("Fat", 0) for diet in labels]

        return {
            "chart_type": "bar",
            "title": "Average Macronutrient Content by Diet Type",
            "labels": labels,
            "datasets": [
                {
                    "label": "Protein (g)",
                    "data": protein_data,
                    "backgroundColor": "rgba(54, 162, 235, 0.8)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1,
                },
                {
                    "label": "Carbs (g)",
                    "data": carbs_data,
                    "backgroundColor": "rgba(255, 99, 132, 0.8)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1,
                },
                {
                    "label": "Fat (g)",
                    "data": fat_data,
                    "backgroundColor": "rgba(255, 206, 86, 0.8)",
                    "borderColor": "rgba(255, 206, 86, 1)",
                    "borderWidth": 1,
                },
            ],
        }

    def get_scatter_plot_data(
        self, x_nutrient: str = "Protein", y_nutrient: str = "Carbs"
    ) -> Dict:
        """Get data formatted for scatter plot: Nutrient relationships"""
        if self.data is None:
            return {"error": "No data available"}

        x_col = f"{x_nutrient}(g)"
        y_col = f"{y_nutrient}(g)"

        if x_col not in self.data.columns or y_col not in self.data.columns:
            return {"error": f"Nutrient columns {x_col} or {y_col} not found"}

        # Sample data for performance (max 500 points)
        sample_size = min(500, len(self.data))
        sample_data = self.data.sample(n=sample_size)

        scatter_data = []
        colors = {}
        diet_types = (
            sample_data["Diet_type"].unique()
            if "Diet_type" in sample_data.columns
            else ["Unknown"]
        )

        # Assign colors to diet types
        color_palette = [
            "#FF6384",
            "#36A2EB",
            "#FFCE56",
            "#4BC0C0",
            "#9966FF",
            "#FF9F40",
        ]
        for i, diet in enumerate(diet_types):
            colors[diet] = color_palette[i % len(color_palette)]

        for _, recipe in sample_data.iterrows():
            diet_type = recipe.get("Diet_type", "Unknown")
            point = {
                "x": round(recipe[x_col], 2),
                "y": round(recipe[y_col], 2),
                "diet_type": diet_type,
                "recipe_name": recipe.get("Recipe_name", "Unknown"),
                "color": colors.get(diet_type, "#999999"),
            }
            scatter_data.append(point)

        return {
            "chart_type": "scatter",
            "title": f"{x_nutrient} vs {y_nutrient} Relationship",
            "x_axis": f"{x_nutrient} (g)",
            "y_axis": f"{y_nutrient} (g)",
            "data": scatter_data,
            "diet_types": list(colors.keys()),
            "colors": colors,
        }

    def get_heatmap_data(self) -> Dict:
        """Get data formatted for heatmap: Nutrient correlations"""
        if self.data is None:
            return {"error": "No data available"}

        nutrient_cols = ["Protein(g)", "Carbs(g)", "Fat(g)"]
        available_cols = [col for col in nutrient_cols if col in self.data.columns]

        if len(available_cols) < 2:
            return {"error": "Insufficient nutrient data for correlation analysis"}

        # Calculate correlation matrix
        correlation_matrix = self.data[available_cols].corr()

        # Format for heatmap
        labels = [col.replace("(g)", "") for col in available_cols]
        data = []

        for i, row_label in enumerate(labels):
            for j, col_label in enumerate(labels):
                correlation_value = round(correlation_matrix.iloc[i, j], 3)
                data.append(
                    {
                        "x": j,
                        "y": i,
                        "value": correlation_value,
                        "row_label": row_label,
                        "col_label": col_label,
                    }
                )

        return {
            "chart_type": "heatmap",
            "title": "Nutrient Correlations",
            "labels": labels,
            "data": data,
            "min_value": -1,
            "max_value": 1,
        }

    def get_pie_chart_data(self) -> Dict:
        """Get data formatted for pie chart: Recipe distribution by diet type"""
        if self.data is None or "Diet_type" not in self.data.columns:
            return {"error": "No diet type data available"}

        diet_counts = self.data["Diet_type"].value_counts()

        # Format for Chart.js pie chart
        labels = diet_counts.index.tolist()
        data_values = diet_counts.values.tolist()

        # Generate colors
        colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]
        background_colors = [colors[i % len(colors)] for i in range(len(labels))]

        return {
            "chart_type": "pie",
            "title": "Recipe Distribution by Diet Type",
            "labels": labels,
            "datasets": [
                {
                    "data": data_values,
                    "backgroundColor": background_colors,
                    "borderWidth": 2,
                }
            ],
            "total_recipes": sum(data_values),
        }

    def get_nutrient_correlations(self) -> Dict:
        """Get detailed nutrient correlation analysis"""
        if self.data is None:
            return {"error": "No data available"}

        nutrient_cols = ["Protein(g)", "Carbs(g)", "Fat(g)"]
        available_cols = [col for col in nutrient_cols if col in self.data.columns]

        if len(available_cols) < 2:
            return {"correlations": {}}

        correlations = {}
        correlation_matrix = self.data[available_cols].corr()

        for i in range(len(available_cols)):
            for j in range(i + 1, len(available_cols)):
                nutrient1 = available_cols[i].replace("(g)", "")
                nutrient2 = available_cols[j].replace("(g)", "")
                correlation_value = round(correlation_matrix.iloc[i, j], 3)

                correlations[f"{nutrient1}_vs_{nutrient2}"] = {
                    "correlation": correlation_value,
                    "strength": self._interpret_correlation(correlation_value),
                    "nutrients": [nutrient1, nutrient2],
                }

        return {
            "correlations": correlations,
            "interpretation": "Correlation values range from -1 to 1, where values closer to -1 or 1 indicate stronger relationships",
        }

    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation strength"""
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            return "Very Strong"
        elif abs_corr >= 0.6:
            return "Strong"
        elif abs_corr >= 0.4:
            return "Moderate"
        elif abs_corr >= 0.2:
            return "Weak"
        else:
            return "Very Weak"


# Example usage for local testing
def main():
    """Test the AzureDietDataProcessor functionality locally"""
    # For local development, you can use Azurite (Azure Storage Emulator)
    connection_string = (
        "DefaultEndpointsProtocol=http;"
        "AccountName=devstoreaccount1;"
        "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
        "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    )

    try:
        processor = AzureDietDataProcessor(connection_string=connection_string)

        # Load data from blob storage
        if processor.load_data_from_blob():
            print("Data loaded successfully from Azure Blob Storage!")

            # Test all functions
            print("\n1. Diet Summary:")
            summary = processor.get_diet_summary()
            print(summary)

            print("\n2. Macronutrient Averages:")
            averages = processor.get_macronutrient_averages()
            for diet, macros in averages.items():
                print(f"  {diet}: {macros}")

            # Upload results back to blob storage
            processor.upload_results_to_blob(summary, "diet_summary.json")
            processor.upload_results_to_blob(averages, "macronutrient_averages.json")

        else:
            print("Failed to load data from blob storage")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
