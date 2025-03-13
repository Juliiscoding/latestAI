import React from "react";

// Simple mock implementation of chart components for the preview
const createChartComponent = (type) => {
  return ({ 
    data = [], 
    categories = [], 
    index, 
    colors = ["blue"], 
    valueFormatter = (val) => val, 
    showLegend = true,
    showGridLines = true,
    showAnimation = true,
    className = "",
    ...props 
  }) => {
    // Create a simple mock chart for preview purposes
    return (
      <div className={`chart-container ${className}`} style={{ width: '100%', height: '100%' }}>
        <div style={{ 
          padding: '20px', 
          border: '1px dashed #ccc', 
          borderRadius: '8px', 
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#f9f9f9'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>{type} Chart</div>
          <div style={{ fontSize: '14px', color: '#666' }}>
            {data.length > 0 ? (
              <>
                <div>Data points: {data.length}</div>
                <div>Categories: {categories.join(', ')}</div>
                <div>Index: {index}</div>
              </>
            ) : (
              "No data available for preview"
            )}
          </div>
          <div style={{ 
            marginTop: '20px', 
            display: 'flex', 
            gap: '10px'
          }}>
            {colors.map((color, i) => (
              <div key={i} style={{ 
                width: '20px', 
                height: '20px', 
                backgroundColor: color === 'blue' ? '#3b82f6' : 
                                  color === 'sky' ? '#0ea5e9' : 
                                  color === 'green' ? '#22c55e' : 
                                  color === 'red' ? '#ef4444' : 
                                  color === 'yellow' ? '#eab308' : 
                                  color === 'purple' ? '#a855f7' : 
                                  color,
                borderRadius: '4px'
              }} />
            ))}
          </div>
        </div>
      </div>
    );
  };
};

// Create all chart components
const AreaChart = createChartComponent('Area');
const BarChart = createChartComponent('Bar');
const LineChart = createChartComponent('Line');
const PieChart = createChartComponent('Pie');
const DonutChart = createChartComponent('Donut');
const RadarChart = createChartComponent('Radar');
const RadialBarChart = createChartComponent('Radial Bar');

export {
  AreaChart,
  BarChart,
  LineChart,
  PieChart,
  DonutChart,
  RadarChart,
  RadialBarChart
};
