import json
import logging
import azure.functions as func

from .azure_diet_processor import AzureDietDataProcessor


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for diet data processing operations.
    Enhanced to support frontend dashboard requirements with chart data,
    filtering, pagination, and comprehensive analytics.
    """

    logging.info("Diet data processor HTTP trigger function processed a request.")

    # CORS headers for all responses
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "86400",
    }

    # Handle preflight OPTIONS request
    if req.method.upper() == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=cors_headers)

    try:
        # Get operation from route
        operation = (req.route_params.get("operation") or "").lower()

        # Handle health check first
        if operation == "health":
            return func.HttpResponse(
                json.dumps({"status": "healthy", "message": "Function is running"}),
                status_code=200,
                mimetype="application/json",
                headers=cors_headers,
            )

        # Initialize the processor
        processor = AzureDietDataProcessor()

        # Load data from Azure Blob Storage
        if not processor.load_data_from_blob():
            return func.HttpResponse(
                json.dumps({"error": "Failed to load data from blob storage"}),
                status_code=500,
                mimetype="application/json",
                headers=cors_headers,
            )

        # Route to appropriate function based on operation
        if operation == "nutritional-insights":
            # Main API for dashboard - returns comprehensive nutritional insights
            result = processor.get_nutritional_insights()

        elif operation == "chart-data":
            # Get data formatted for specific chart types
            chart_type = req.params.get("type", "bar")
            result = processor.get_chart_data(chart_type)

        elif operation == "recipes":
            # Enhanced recipes endpoint with pagination and filtering
            page = int(req.params.get("page", 1))
            page_size = int(req.params.get("page_size", 20))
            diet_type = req.params.get("diet_type", "")
            search_term = req.params.get("search", "")
            result = processor.get_recipes_paginated(
                page, page_size, diet_type, search_term
            )

        elif operation == "clusters":
            # Clustering analysis for recipe grouping
            result = processor.get_recipe_clusters()

        elif operation == "diet-types":
            # Get available diet types for filter dropdown
            result = processor.get_diet_types()

        elif operation == "bar-chart":
            # Bar chart data: Average macronutrient content by diet type
            result = processor.get_bar_chart_data()

        elif operation == "scatter-plot":
            # Scatter plot data: Nutrient relationships
            x_nutrient = req.params.get("x", "Protein")
            y_nutrient = req.params.get("y", "Carbs")
            result = processor.get_scatter_plot_data(x_nutrient, y_nutrient)

        elif operation == "heatmap":
            # Heatmap data: Nutrient correlations
            result = processor.get_heatmap_data()

        elif operation == "pie-chart":
            # Pie chart data: Recipe distribution by diet type
            result = processor.get_pie_chart_data()

        elif operation == "summary":
            result = processor.get_diet_summary()

        elif operation == "macronutrients":
            result = processor.get_macronutrient_averages()

        elif operation == "comparison":
            result = processor.get_diet_comparison_data()

        elif operation == "top-recipes":
            nutrient = req.params.get("nutrient", "Protein")
            try:
                n = int(req.params.get("n", 10))
            except (TypeError, ValueError):
                n = 10
            n = max(1, min(n, 100))
            result = processor.get_top_recipes_by_nutrient(nutrient, n)

        elif operation == "cuisine-distribution":
            result = processor.get_cuisine_distribution()

        elif operation == "nutrient-ranges":
            result = processor.get_nutrient_ranges()

        elif operation.startswith("recipes/"):
            diet_type = operation.replace("recipes/", "")
            result = processor.get_recipes_by_diet_type(diet_type)

        elif operation == "search":
            search_term = req.params.get("term", "")
            search_field = req.params.get("field", "Recipe_name")
            if not search_term:
                return func.HttpResponse(
                    json.dumps({"error": "Search term is required"}),
                    status_code=400,
                    mimetype="application/json",
                    headers=cors_headers,
                )
            result = processor.search_recipes(search_term, search_field)

        else:
            # Default: return available operations
            result = {
                "message": "Welcome to Enhanced Diet Data Processor API",
                "status": "running",
                "version": "2.0",
                "description": "APIs designed for nutritional insights dashboard",
                "available_operations": {
                    "health": "/diet-processor/health",
                    "main_apis": {
                        "nutritional_insights": "/diet-processor/nutritional-insights",
                        "recipes": "/diet-processor/recipes?page=1&page_size=20&diet_type={diet}&search={term}",
                        "clusters": "/diet-processor/clusters",
                    },
                    "chart_apis": {
                        "bar_chart": "/diet-processor/bar-chart",
                        "scatter_plot": "/diet-processor/scatter-plot?x=Protein&y=Carbs",
                        "heatmap": "/diet-processor/heatmap",
                        "pie_chart": "/diet-processor/pie-chart",
                        "chart_data": "/diet-processor/chart-data?type={bar|scatter|heatmap|pie}",
                    },
                    "utility_apis": {
                        "diet_types": "/diet-processor/diet-types",
                        "summary": "/diet-processor/summary",
                        "macronutrients": "/diet-processor/macronutrients",
                        "nutrient_ranges": "/diet-processor/nutrient-ranges",
                    },
                    "legacy_apis": {
                        "comparison": "/diet-processor/comparison",
                        "top_recipes": "/diet-processor/top-recipes?nutrient=Protein&n=10",
                        "cuisine_distribution": "/diet-processor/cuisine-distribution",
                        "recipes_by_diet": "/diet-processor/recipes/{diet_type}",
                        "search": "/diet-processor/search?term={search_term}&field=Recipe_name",
                    },
                },
            }

        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json",
            headers=cors_headers,
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json",
            headers=cors_headers,
        )
