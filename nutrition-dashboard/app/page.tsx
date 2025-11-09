"use client";

import { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Stack,
  TextField,
  MenuItem,
} from "@mui/material";
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
} from "recharts";

const API_BASE =
  "https://diet-processor-func-dnfzf2bvcpbrf4by.westus2-01.azurewebsites.net/api/diet-processor";

export default function Dashboard() {
  const [macronutrients, setMacronutrients] = useState<any[]>([]);
  const [cuisineDistribution, setCuisineDistribution] = useState<any[]>([]);
  const [comparisonData, setComparisonData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [dietType, setDietType] = useState("All");

  // Fetch functions
  const getMacronutrients = async () => {
    setLoading(true);
    const res = await fetch(`${API_BASE}/macronutrients`);
    const data = await res.json();
    setMacronutrients(data);
    setLoading(false);
  };

  const getCuisineDistribution = async () => {
    setLoading(true);
    const res = await fetch(`${API_BASE}/cuisine-distribution`);
    const data = await res.json();
    setCuisineDistribution(data);
    setLoading(false);
  };

  const getComparison = async () => {
    setLoading(true);
    const res = await fetch(`${API_BASE}/comparison`);
    const data = await res.json();
    setComparisonData(data);
    setLoading(false);
  };

  useEffect(() => {
    getMacronutrients();
    getCuisineDistribution();
    getComparison();
  }, []);

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Nutritional Insights
      </Typography>

      <Typography variant="h6" sx={{ mt: 3 }}>
        Explore Nutritional Insights
      </Typography>

      <Stack direction="row" spacing={3} sx={{ mt: 2, flexWrap: "wrap" }}>
        {/* Macronutrient Bar Chart */}
        <Card sx={{ p: 2, width: 300 }}>
          <Typography variant="subtitle1" fontWeight="bold">
            Bar Chart
          </Typography>
          <Typography variant="body2">Average macronutrient content</Typography>
          <BarChart width={250} height={200} data={macronutrients}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="diet" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="protein" fill="#1976d2" />
          </BarChart>
        </Card>

        {/* Comparison Scatter Plot */}
        <Card sx={{ p: 2, width: 300 }}>
          <Typography variant="subtitle1" fontWeight="bold">
            Scatter Plot
          </Typography>
          <Typography variant="body2">
            Nutrient relationships (protein vs carbs)
          </Typography>
          <ScatterChart width={250} height={200}>
            <CartesianGrid />
            <XAxis dataKey="protein" />
            <YAxis dataKey="carbs" />
            <Tooltip />
            <Scatter data={comparisonData} fill="#2e7d32" />
          </ScatterChart>
        </Card>

        {/* Cuisine Distribution Pie Chart */}
        <Card sx={{ p: 2, width: 300 }}>
          <Typography variant="subtitle1" fontWeight="bold">
            Pie Chart
          </Typography>
          <Typography variant="body2">
            Recipe distribution by cuisine
          </Typography>
          <PieChart width={250} height={200}>
            <Pie
              data={cuisineDistribution}
              dataKey="count"
              nameKey="cuisine"
              cx="50%"
              cy="50%"
              outerRadius={70}
              fill="#8884d8"
              label
            >
              {cuisineDistribution.map((_, i) => (
                <Cell
                  key={i}
                  fill={["#8884d8", "#82ca9d", "#ffc658", "#ff8042"][i % 4]}
                />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </Card>
      </Stack>

      {/* Filters and Buttons */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6">Filters and Data Interaction</Typography>
        <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
          <TextField
            size="small"
            placeholder="Search by Diet Type"
            value={dietType}
            onChange={(e) => setDietType(e.target.value)}
          />
          <TextField size="small" select label="All Diet Types" value={dietType}>
            <MenuItem value="All">All Diet Types</MenuItem>
            <MenuItem value="Vegan">Vegan</MenuItem>
            <MenuItem value="Keto">Keto</MenuItem>
            <MenuItem value="Paleo">Paleo</MenuItem>
          </TextField>
        </Stack>
      </Box>

      {/* API Buttons */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6">API Data Interaction</Typography>
        <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
          <Button variant="contained" onClick={getMacronutrients}>
            Get Nutritional Insights
          </Button>
          <Button variant="contained" color="success" onClick={getComparison}>
            Get Recipes
          </Button>
          <Button variant="contained" color="secondary" onClick={getCuisineDistribution}>
            Get Clusters
          </Button>
        </Stack>
      </Box>

      {/* Pagination */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6">Pagination</Typography>
        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
          <Button variant="outlined">Previous</Button>
          <Button variant="contained">1</Button>
          <Button variant="outlined">2</Button>
          <Button variant="outlined">Next</Button>
        </Stack>
      </Box>

      <Typography variant="body2" textAlign="center" sx={{ mt: 6, color: "gray" }}>
        © 2025 Nutritional Insights. All Rights Reserved.
      </Typography>
    </Box>
  );
}
