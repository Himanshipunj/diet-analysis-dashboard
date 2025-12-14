"use client";

import { useState, useEffect } from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    PieChart,
    Pie,
    Cell,
    ScatterChart,
    Scatter,
    ResponsiveContainer,
} from "recharts";
import DashboardWrapper from "./components/DashboardWrapper";

const API_BASE =
    "https://diet-processor-func-dnfzf2bvcpbrf4by.westus2-01.azurewebsites.net/api/diet-processor";

// Color palette for charts
const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088fe', '#00c49f'];

interface Recipe {
    recipe_name: string;
    diet_type: string;
    cuisine_type: string;
    protein: number;
    carbs: number;
    fat: number;
}

interface ChartData {
    labels: string[];
    datasets: any[];
}

interface NutritionalInsights {
    summary: {
        total_recipes: number;
        total_diet_types: number;
        total_cuisine_types: number;
        most_common_diet: string;
        most_common_cuisine: string;
    };
    macronutrients: any;
    nutrient_ranges: any;
    diet_distribution: any;
}

export default function Dashboard() {
    const [insights, setInsights] = useState<NutritionalInsights | null>(null);
    const [barChartData, setBarChartData] = useState<ChartData | null>(null);
    const [scatterData, setScatterData] = useState<any>(null);
    const [heatmapData, setHeatmapData] = useState<any>(null);
    const [pieChartData, setPieChartData] = useState<ChartData | null>(null);
    const [recipes, setRecipes] = useState<Recipe[]>([]);
    const [clusters, setClusters] = useState<any>(null);
    const [dietTypes, setDietTypes] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Filter states
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedDietType, setSelectedDietType] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalRecipes, setTotalRecipes] = useState(0);

    // Chart customization
    const [scatterX, setScatterX] = useState("Protein");
    const [scatterY, setScatterY] = useState("Carbs");

    // Utility functions
    const showLoading = (show: boolean) => setLoading(show);
    const showError = (message: string) => {
        setError(message);
        setTimeout(() => setError(null), 5000);
    };

    // API functions
    const apiCall = async (endpoint: string, params: Record<string, any> = {}) => {
        try {
            const url = new URL(API_BASE + endpoint);
            Object.keys(params).forEach(key => {
                if (params[key]) url.searchParams.append(key, params[key]);
            });

            const response = await fetch(url.toString());
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error: any) {
            console.error('API Error:', error);
            showError(`API Error: ${error.message}`);
            throw error;
        }
    };

    // Load functions
    const loadNutritionalInsights = async () => {
        try {
            const data = await apiCall('/nutritional-insights');
            setInsights(data);
        } catch (error) {
            console.error('Failed to load insights:', error);
        }
    };

    const loadBarChart = async () => {
        try {
            const data = await apiCall('/bar-chart');
            setBarChartData(data);
        } catch (error) {
            console.error('Failed to load bar chart:', error);
        }
    };

    const loadScatterPlot = async (xNutrient = scatterX, yNutrient = scatterY) => {
        try {
            const data = await apiCall('/scatter-plot', { x: xNutrient, y: yNutrient });
            setScatterData(data);
        } catch (error) {
            console.error('Failed to load scatter plot:', error);
        }
    };

    const loadHeatmap = async () => {
        try {
            const data = await apiCall('/heatmap');
            setHeatmapData(data);
        } catch (error) {
            console.error('Failed to load heatmap:', error);
        }
    };

    const loadPieChart = async () => {
        try {
            const data = await apiCall('/pie-chart');
            setPieChartData(data);
        } catch (error) {
            console.error('Failed to load pie chart:', error);
        }
    };

    const loadRecipes = async (page = 1) => {
        try {
            const params = {
                page: page,
                page_size: 12,
                diet_type: selectedDietType,
                search: searchTerm
            };

            const data = await apiCall('/recipes', params);
            setRecipes(data.recipes);
            setCurrentPage(data.pagination.current_page);
            setTotalPages(data.pagination.total_pages);
            setTotalRecipes(data.pagination.total_recipes);
        } catch (error) {
            console.error('Failed to load recipes:', error);
        }
    };

    const loadClusters = async () => {
        try {
            const data = await apiCall('/clusters');
            setClusters(data);
        } catch (error) {
            console.error('Failed to load clusters:', error);
        }
    };

    const loadDietTypes = async () => {
        try {
            const data = await apiCall('/diet-types');
            setDietTypes(data.diet_types);
        } catch (error) {
            console.error('Failed to load diet types:', error);
        }
    };

    const loadAllCharts = async () => {
        showLoading(true);
        try {
            await Promise.all([
                loadBarChart(),
                loadScatterPlot(),
                loadHeatmap(),
                loadPieChart()
            ]);
        } catch (error) {
            console.error('Error loading charts:', error);
        } finally {
            showLoading(false);
        }
    };

    // Initialize dashboard
    const initializeDashboard = async () => {
        showLoading(true);
        try {
            await Promise.all([
                loadNutritionalInsights(),
                loadDietTypes(),
                loadAllCharts(),
                loadRecipes()
            ]);
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
        } finally {
            showLoading(false);
        }
    };

    // Event handlers
    const handleApplyFilters = () => {
        loadRecipes(1);
    };

    const handleClearFilters = () => {
        setSearchTerm("");
        setSelectedDietType("");
        setTimeout(() => loadRecipes(1), 100);
    };

    const handleScatterChange = () => {
        loadScatterPlot(scatterX, scatterY);
    };

    // Transform data for charts
    const transformBarChartData = () => {
        if (!barChartData?.datasets) return [];

        const labels = barChartData.labels || [];
        const datasets = barChartData.datasets;

        return labels.map((label, index) => ({
            dietType: label,
            protein: datasets[0]?.data[index] || 0,
            carbs: datasets[1]?.data[index] || 0,
            fat: datasets[2]?.data[index] || 0,
        }));
    };

    const transformScatterData = () => {
        if (!scatterData?.data) return [];
        return scatterData.data.map((point: any) => ({
            x: point.x,
            y: point.y,
            dietType: point.diet_type,
            recipeName: point.recipe_name
        }));
    };

    const transformPieChartData = () => {
        if (!pieChartData?.datasets?.[0]?.data) return [];

        const labels = pieChartData.labels || [];
        const data = pieChartData.datasets[0].data;

        return labels.map((label, index) => ({
            name: label,
            value: data[index] || 0
        }));
    };

    // Effects
    useEffect(() => {
        initializeDashboard();
    }, []);

    useEffect(() => {
        handleScatterChange();
    }, [scatterX, scatterY]);

    return (
        <DashboardWrapper>
            <div className="bg-gray-100 min-h-screen">
                {/* Header */}
                <header className="bg-blue-600 p-4 text-white">
                    <h1 className="text-3xl font-semibold">Nutritional Insights</h1>
                </header>

                <main className="container mx-auto p-6">
                    {/* Loading indicator */}
                    {loading && (
                        <div className="text-center p-4">
                            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            <p className="mt-2">Loading nutritional data...</p>
                        </div>
                    )}

                    {/* Error display */}
                    {error && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                            {error}
                        </div>
                    )}

                    {/* Summary Statistics */}
                    {insights?.summary && (
                        <section className="mb-8">
                            <h2 className="text-2xl font-semibold mb-4">Dashboard Overview</h2>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                                <div className="bg-white p-4 shadow-lg rounded-lg">
                                    <h3 className="font-semibold text-gray-600">Total Recipes</h3>
                                    <p className="text-2xl font-bold text-blue-600">{insights.summary.total_recipes}</p>
                                </div>
                                <div className="bg-white p-4 shadow-lg rounded-lg">
                                    <h3 className="font-semibold text-gray-600">Diet Types</h3>
                                    <p className="text-2xl font-bold text-green-600">{insights.summary.total_diet_types}</p>
                                </div>
                                <div className="bg-white p-4 shadow-lg rounded-lg">
                                    <h3 className="font-semibold text-gray-600">Cuisine Types</h3>
                                    <p className="text-2xl font-bold text-purple-600">{insights.summary.total_cuisine_types}</p>
                                </div>
                                <div className="bg-white p-4 shadow-lg rounded-lg">
                                    <h3 className="font-semibold text-gray-600">Most Common Diet</h3>
                                    <p className="text-xl font-bold text-orange-600">{insights.summary.most_common_diet}</p>
                                </div>
                            </div>
                        </section>
                    )}

                    {/* Charts Section */}
                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">Explore Nutritional Insights</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

                            {/* Bar Chart */}
                            <div className="bg-white p-4 shadow-lg rounded-lg">
                                <h3 className="font-semibold mb-2">Bar Chart</h3>
                                <p className="text-sm text-gray-600 mb-4">Average macronutrient content by diet type.</p>
                                <div className="w-full h-48">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={transformBarChartData()}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="dietType" fontSize={10} />
                                            <YAxis fontSize={10} />
                                            <Tooltip />
                                            <Bar dataKey="protein" fill="#8884d8" name="Protein" />
                                            <Bar dataKey="carbs" fill="#82ca9d" name="Carbs" />
                                            <Bar dataKey="fat" fill="#ffc658" name="Fat" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Scatter Plot */}
                            <div className="bg-white p-4 shadow-lg rounded-lg">
                                <h3 className="font-semibold mb-2">Scatter Plot</h3>
                                <p className="text-sm text-gray-600 mb-2">Nutrient relationships.</p>
                                <div className="mb-2 text-xs">
                                    <select
                                        value={scatterX}
                                        onChange={(e) => setScatterX(e.target.value)}
                                        className="text-xs p-1 border rounded mr-1"
                                    >
                                        <option value="Protein">Protein</option>
                                        <option value="Carbs">Carbs</option>
                                        <option value="Fat">Fat</option>
                                    </select>
                                    vs
                                    <select
                                        value={scatterY}
                                        onChange={(e) => setScatterY(e.target.value)}
                                        className="text-xs p-1 border rounded ml-1"
                                    >
                                        <option value="Carbs">Carbs</option>
                                        <option value="Protein">Protein</option>
                                        <option value="Fat">Fat</option>
                                    </select>
                                </div>
                                <div className="w-full h-32">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <ScatterChart data={transformScatterData()}>
                                            <CartesianGrid />
                                            <XAxis dataKey="x" fontSize={10} />
                                            <YAxis dataKey="y" fontSize={10} />
                                            <Tooltip
                                                formatter={(value: any, name: string) => [value + 'g', name]}
                                            />
                                            <Scatter dataKey="y" fill="#8884d8" />
                                        </ScatterChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Heatmap */}
                            <div className="bg-white p-4 shadow-lg rounded-lg">
                                <h3 className="font-semibold mb-2">Heatmap</h3>
                                <p className="text-sm text-gray-600 mb-4">Nutrient correlations.</p>
                                <div className="w-full h-48 flex items-center justify-center">
                                    {heatmapData?.data ? (
                                        <div
                                            className="grid gap-1 h-full w-full"
                                            style={{
                                                gridTemplateColumns: `repeat(${heatmapData.labels?.length || 3}, 1fr)`
                                            }}
                                        >
                                            {heatmapData.data.map((cell: any, index: number) => {
                                                const intensity = Math.abs(cell.value);
                                                const opacity = intensity * 0.8 + 0.2;
                                                const bgColor = cell.value > 0 ?
                                                    `rgba(54, 162, 235, ${opacity})` :
                                                    `rgba(255, 99, 132, ${opacity})`;

                                                return (
                                                    <div
                                                        key={index}
                                                        className="flex items-center justify-center text-xs font-medium"
                                                        style={{
                                                            backgroundColor: bgColor,
                                                            color: intensity > 0.5 ? 'white' : 'black'
                                                        }}
                                                        title={`${cell.row_label} vs ${cell.col_label}: ${cell.value.toFixed(3)}`}
                                                    >
                                                        {cell.value.toFixed(2)}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    ) : (
                                        <div className="text-gray-400">Loading heatmap...</div>
                                    )}
                                </div>
                            </div>

                            {/* Pie Chart */}
                            <div className="bg-white p-4 shadow-lg rounded-lg">
                                <h3 className="font-semibold mb-2">Pie Chart</h3>
                                <p className="text-sm text-gray-600 mb-4">Recipe distribution by diet type.</p>
                                <div className="w-full h-48">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={transformPieChartData()}
                                                dataKey="value"
                                                nameKey="name"
                                                cx="50%"
                                                cy="50%"
                                                outerRadius={60}
                                                fill="#8884d8"
                                                label={false}
                                            >
                                                {transformPieChartData().map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <Tooltip />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                        </div>
                    </section>

                    {/* Filters and Data Interaction */}
                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">Filters and Data Interaction</h2>
                        <div className="flex flex-wrap gap-4">
                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                placeholder="Search by Diet Type"
                                className="p-2 border rounded w-full sm:w-auto"
                            />
                            <select
                                value={selectedDietType}
                                onChange={(e) => setSelectedDietType(e.target.value)}
                                className="p-2 border rounded w-full sm:w-auto"
                            >
                                <option value="">All Diet Types</option>
                                {dietTypes.map((diet) => (
                                    <option key={diet} value={diet}>{diet}</option>
                                ))}
                            </select>
                            <button
                                onClick={handleApplyFilters}
                                className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
                            >
                                Apply Filters
                            </button>
                            <button
                                onClick={handleClearFilters}
                                className="bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700"
                            >
                                Clear Filters
                            </button>
                        </div>
                    </section>

                    {/* API Data Interaction */}
                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">API Data Interaction</h2>
                        <div className="flex flex-wrap gap-4">
                            <button
                                onClick={loadNutritionalInsights}
                                disabled={loading}
                                className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
                            >
                                Get Nutritional Insights
                            </button>
                            <button
                                onClick={() => loadRecipes(1)}
                                disabled={loading}
                                className="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50"
                            >
                                Get Recipes
                            </button>
                            <button
                                onClick={loadClusters}
                                disabled={loading}
                                className="bg-purple-600 text-white py-2 px-4 rounded hover:bg-purple-700 disabled:opacity-50"
                            >
                                Get Clusters
                            </button>
                            <button
                                onClick={loadAllCharts}
                                disabled={loading}
                                className="bg-orange-600 text-white py-2 px-4 rounded hover:bg-orange-700 disabled:opacity-50"
                            >
                                Refresh Charts
                            </button>
                        </div>
                    </section>

                    {/* Recipes Display */}
                    <section className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4">Recipes</h2>
                        <div className="bg-white rounded-lg shadow-lg p-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {recipes.map((recipe, index) => (
                                    <div key={index} className="bg-gray-50 p-3 rounded border">
                                        <h4 className="font-semibold text-sm">{recipe.recipe_name}</h4>
                                        <p className="text-xs text-gray-600">{recipe.diet_type} | {recipe.cuisine_type}</p>
                                        <div className="mt-2 text-xs space-x-1">
                                            <span className="bg-blue-100 px-2 py-1 rounded">P: {recipe.protein}g</span>
                                            <span className="bg-red-100 px-2 py-1 rounded">C: {recipe.carbs}g</span>
                                            <span className="bg-yellow-100 px-2 py-1 rounded">F: {recipe.fat}g</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>

                    {/* Pagination */}
                    <section>
                        <h2 className="text-2xl font-semibold mb-4">Pagination</h2>
                        <div className="flex justify-center gap-2 mt-4">
                            {currentPage > 1 && (
                                <button
                                    onClick={() => loadRecipes(currentPage - 1)}
                                    className="px-3 py-1 bg-gray-300 rounded hover:bg-gray-400"
                                >
                                    Previous
                                </button>
                            )}

                            {/* Page numbers */}
                            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                const page = Math.max(1, currentPage - 2) + i;
                                if (page > totalPages) return null;

                                return (
                                    <button
                                        key={page}
                                        onClick={() => loadRecipes(page)}
                                        className={`px-3 py-1 rounded ${page === currentPage
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-gray-300 hover:bg-gray-400'
                                            }`}
                                    >
                                        {page}
                                    </button>
                                );
                            })}

                            {currentPage < totalPages && (
                                <button
                                    onClick={() => loadRecipes(currentPage + 1)}
                                    className="px-3 py-1 bg-gray-300 rounded hover:bg-gray-400"
                                >
                                    Next
                                </button>
                            )}

                            <span className="px-3 py-1 text-gray-600">
                                Page {currentPage} of {totalPages} ({totalRecipes} total)
                            </span>
                        </div>
                    </section>

                    {/* Clusters Info */}
                    {clusters && (
                        <section className="mb-8 mt-8">
                            <h2 className="text-2xl font-semibold mb-4">Recipe Clusters</h2>
                            <div className="bg-white rounded-lg shadow-lg p-4">
                                <p className="text-sm text-gray-600 mb-4">
                                    Found {clusters.total_clusters} clusters using {clusters.clustering_method}
                                </p>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {Object.values(clusters.clusters || {}).map((cluster: any, index: number) => (
                                        <div key={index} className="bg-gray-50 p-3 rounded border">
                                            <h4 className="font-semibold text-sm">Cluster {cluster.cluster_id}</h4>
                                            <p className="text-xs text-gray-600">{cluster.size} recipes</p>
                                            <div className="mt-2 text-xs">
                                                <div>Avg Protein: {cluster.avg_protein}g</div>
                                                <div>Avg Carbs: {cluster.avg_carbs}g</div>
                                                <div>Avg Fat: {cluster.avg_fat}g</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </section>
                    )}

                </main>

                <footer className="bg-blue-600 p-4 text-white text-center mt-10">
                    <p>&copy; 2025 Nutritional Insights. All Rights Reserved.</p>
                </footer>
            </div>
        </DashboardWrapper>
    );
}