# Nutritional Insights API Documentation

This document provides comprehensive documentation for the Enhanced Diet Data Processor Azure Function API, designed specifically to support the Nutritional Insights dashboard frontend.

## Base URL

```
https://<your-function-app>.azurewebsites.net/api/diet-processor
```

## Authentication

All endpoints use `authLevel: "anonymous"` and include CORS headers for web browser compatibility.

---

## Main Dashboard APIs

### 1. Get Nutritional Insights

**Endpoint:** `GET /nutritional-insights`

**Description:** Returns comprehensive nutritional data for the main dashboard overview.

**Response:**

```json
{
  "summary": {
    "total_recipes": 1000,
    "total_diet_types": 8,
    "total_cuisine_types": 15,
    "diet_types": ["Vegan", "Keto", "Mediterranean", ...],
    "most_common_diet": "Mediterranean",
    "most_common_cuisine": "Italian"
  },
  "macronutrients": {
    "Vegan": {"Protein": 12.5, "Carbs": 45.2, "Fat": 8.1},
    "Keto": {"Protein": 25.3, "Carbs": 5.8, "Fat": 35.7}
  },
  "nutrient_ranges": {
    "Protein": {"min": 0.5, "max": 85.2, "average": 18.7, "median": 16.3},
    "Carbs": {"min": 1.2, "max": 95.4, "average": 32.1, "median": 28.9}
  },
  "diet_distribution": {...},
  "top_protein_recipes": [...],
  "correlations": {...},
  "timestamp": "2025-01-01T12:00:00"
}
```

### 2. Get Paginated Recipes

**Endpoint:** `GET /recipes`

**Query Parameters:**

- `page` (optional, default: 1): Page number
- `page_size` (optional, default: 20): Number of recipes per page
- `diet_type` (optional): Filter by diet type
- `search` (optional): Search term for recipe names

**Example:** `GET /recipes?page=1&page_size=20&diet_type=Vegan&search=pasta`

**Response:**

```json
{
  "recipes": [
    {
      "recipe_name": "Vegan Pasta Primavera",
      "diet_type": "Vegan",
      "cuisine_type": "Italian",
      "protein": 12.5,
      "carbs": 45.2,
      "fat": 8.1
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 25,
    "total_recipes": 500,
    "page_size": 20,
    "has_next": true,
    "has_previous": false
  },
  "filters": {
    "diet_type": "Vegan",
    "search_term": "pasta"
  }
}
```

### 3. Get Recipe Clusters

**Endpoint:** `GET /clusters`

**Description:** Returns recipe clusters based on nutritional similarity using K-means clustering.

**Response:**

```json
{
  "clusters": {
    "cluster_0": {
      "cluster_id": 0,
      "size": 150,
      "avg_protein": 25.3,
      "avg_carbs": 8.2,
      "avg_fat": 18.7,
      "common_diet_types": {"Keto": 80, "Low-carb": 45, "Atkins": 25},
      "sample_recipes": ["Keto Chicken Salad", "Low-carb Beef Stir-fry", ...]
    }
  },
  "total_clusters": 5,
  "features_used": ["Protein(g)", "Carbs(g)", "Fat(g)"],
  "clustering_method": "K-Means"
}
```

---

## Chart-Specific APIs

### 1. Bar Chart Data

**Endpoint:** `GET /bar-chart`

**Description:** Returns data formatted for Chart.js bar chart showing average macronutrient content by diet type.

**Response:**

```json
{
  "chart_type": "bar",
  "title": "Average Macronutrient Content by Diet Type",
  "labels": ["Vegan", "Keto", "Mediterranean", "Paleo"],
  "datasets": [
    {
      "label": "Protein (g)",
      "data": [12.5, 25.3, 18.7, 22.1],
      "backgroundColor": "rgba(54, 162, 235, 0.8)",
      "borderColor": "rgba(54, 162, 235, 1)",
      "borderWidth": 1
    },
    {
      "label": "Carbs (g)",
      "data": [45.2, 5.8, 32.1, 15.4],
      "backgroundColor": "rgba(255, 99, 132, 0.8)",
      "borderColor": "rgba(255, 99, 132, 1)",
      "borderWidth": 1
    },
    {
      "label": "Fat (g)",
      "data": [8.1, 35.7, 12.3, 18.9],
      "backgroundColor": "rgba(255, 206, 86, 0.8)",
      "borderColor": "rgba(255, 206, 86, 1)",
      "borderWidth": 1
    }
  ]
}
```

### 2. Scatter Plot Data

**Endpoint:** `GET /scatter-plot`

**Query Parameters:**

- `x` (optional, default: "Protein"): X-axis nutrient
- `y` (optional, default: "Carbs"): Y-axis nutrient

**Example:** `GET /scatter-plot?x=Protein&y=Fat`

**Response:**

```json
{
  "chart_type": "scatter",
  "title": "Protein vs Fat Relationship",
  "x_axis": "Protein (g)",
  "y_axis": "Fat (g)",
  "data": [
    {
      "x": 25.3,
      "y": 18.7,
      "diet_type": "Keto",
      "recipe_name": "Keto Chicken Salad",
      "color": "#FF6384"
    }
  ],
  "diet_types": ["Vegan", "Keto", "Mediterranean"],
  "colors": {
    "Vegan": "#FF6384",
    "Keto": "#36A2EB",
    "Mediterranean": "#FFCE56"
  }
}
```

### 3. Heatmap Data

**Endpoint:** `GET /heatmap`

**Description:** Returns nutrient correlation data for heatmap visualization.

**Response:**

```json
{
  "chart_type": "heatmap",
  "title": "Nutrient Correlations",
  "labels": ["Protein", "Carbs", "Fat"],
  "data": [
    {
      "x": 0,
      "y": 1,
      "value": -0.245,
      "row_label": "Protein",
      "col_label": "Carbs"
    }
  ],
  "min_value": -1,
  "max_value": 1
}
```

### 4. Pie Chart Data

**Endpoint:** `GET /pie-chart`

**Description:** Returns recipe distribution by diet type for pie chart.

**Response:**

```json
{
  "chart_type": "pie",
  "title": "Recipe Distribution by Diet Type",
  "labels": ["Mediterranean", "Vegan", "Keto", "Paleo"],
  "datasets": [
    {
      "data": [350, 250, 180, 120],
      "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"],
      "borderWidth": 2
    }
  ],
  "total_recipes": 900
}
```

### 5. Generic Chart Data

**Endpoint:** `GET /chart-data?type={chart_type}`

**Query Parameters:**

- `type`: Chart type (bar, scatter, heatmap, pie)

**Description:** Generic endpoint that routes to specific chart data based on type parameter.

---

## Utility APIs

### 1. Get Diet Types

**Endpoint:** `GET /diet-types`

**Description:** Returns available diet types for filter dropdowns.

**Response:**

```json
{
  "diet_types": ["Keto", "Mediterranean", "Paleo", "Vegan"],
  "diet_counts": {
    "Mediterranean": 350,
    "Vegan": 250,
    "Keto": 180,
    "Paleo": 120
  },
  "total_types": 4
}
```

### 2. Health Check

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "message": "Function is running"
}
```

---

## Legacy APIs (Maintained for Backward Compatibility)

### 1. Diet Summary

**Endpoint:** `GET /summary`

### 2. Macronutrients

**Endpoint:** `GET /macronutrients`

### 3. Diet Comparison

**Endpoint:** `GET /comparison`

### 4. Top Recipes

**Endpoint:** `GET /top-recipes?nutrient={nutrient}&n={count}`

### 5. Cuisine Distribution

**Endpoint:** `GET /cuisine-distribution`

### 6. Nutrient Ranges

**Endpoint:** `GET /nutrient-ranges`

### 7. Recipes by Diet Type

**Endpoint:** `GET /recipes/{diet_type}`

### 8. Search Recipes

**Endpoint:** `GET /search?term={search_term}&field={field_name}`

---

## Frontend Integration Examples

### JavaScript Fetch Examples

```javascript
// Get nutritional insights for dashboard
const insights = await fetch("/api/diet-processor/nutritional-insights").then(
  (response) => response.json()
);

// Get bar chart data
const barData = await fetch("/api/diet-processor/bar-chart").then((response) =>
  response.json()
);

// Get paginated recipes with filters
const recipes = await fetch(
  "/api/diet-processor/recipes?page=1&diet_type=Vegan&search=pasta"
).then((response) => response.json());

// Get scatter plot data
const scatterData = await fetch(
  "/api/diet-processor/scatter-plot?x=Protein&y=Carbs"
).then((response) => response.json());
```

### Chart.js Integration

```javascript
// Bar Chart
const barChart = new Chart(ctx, {
  type: "bar",
  data: {
    labels: barData.labels,
    datasets: barData.datasets,
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: barData.title,
      },
    },
  },
});

// Pie Chart
const pieChart = new Chart(ctx, {
  type: "pie",
  data: {
    labels: pieData.labels,
    datasets: pieData.datasets,
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: pieData.title,
      },
    },
  },
});
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **500**: Internal Server Error

Error responses follow this format:

```json
{
  "error": "Description of the error"
}
```

---

## Performance Notes

1. **Scatter Plot Data**: Limited to 500 random samples for performance
2. **Pagination**: Recommended page size is 20-50 recipes
3. **Caching**: Consider implementing client-side caching for chart data
4. **CORS**: All endpoints include appropriate CORS headers for browser requests

---

## Data Schema

The API expects Azure Blob Storage data with these columns:

- `Recipe_name`: Recipe name
- `Diet_type`: Diet category (Vegan, Keto, etc.)
- `Cuisine_type`: Cuisine category (Italian, Mexican, etc.)
- `Protein(g)`: Protein content in grams
- `Carbs(g)`: Carbohydrate content in grams
- `Fat(g)`: Fat content in grams
