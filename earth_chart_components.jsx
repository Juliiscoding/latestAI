/**
 * Earth Module Chart Components
 * 
 * This file contains reusable chart components for the Earth module dashboard.
 * These components use Recharts to visualize data from Snowflake analytics views.
 */

import React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { Box, Text, Flex, useColorModeValue } from '@chakra-ui/react';

// Color palette for charts
const COLORS = [
  '#3182CE', // blue.500
  '#38B2AC', // teal.500
  '#805AD5', // purple.500
  '#DD6B20', // orange.500
  '#E53E3E', // red.500
  '#38A169', // green.500
  '#D69E2E', // yellow.500
  '#00B5D8', // cyan.500
  '#ED64A6', // pink.500
  '#667EEA', // indigo.500
];

/**
 * Custom tooltip component for charts
 */
const CustomTooltip = ({ active, payload, label, formatter }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  if (active && payload && payload.length) {
    return (
      <Box 
        bg={bgColor} 
        p={3} 
        borderRadius="md" 
        boxShadow="md" 
        border="1px solid" 
        borderColor={borderColor}
      >
        <Text fontWeight="bold" mb={2}>{label}</Text>
        {payload.map((entry, index) => (
          <Flex key={`item-${index}`} align="center" mb={1}>
            <Box 
              w={3} 
              h={3} 
              borderRadius="full" 
              bg={entry.color} 
              mr={2} 
            />
            <Text fontSize="sm">
              {entry.name}: {formatter ? formatter(entry.value) : entry.value}
            </Text>
          </Flex>
        ))}
      </Box>
    );
  }
  
  return null;
};

/**
 * Line Chart Component
 * 
 * @param {Object} props - Component props
 * @param {Array} props.data - Chart data
 * @param {String} props.xKey - Key for X-axis values
 * @param {Array} props.yKeys - Keys for Y-axis values
 * @param {Array} props.colors - Colors for lines
 * @param {Function} props.formatter - Value formatter function
 * @param {Boolean} props.showGrid - Whether to show grid lines
 */
export const LineChart = ({ 
  data, 
  xKey, 
  yKeys, 
  colors = COLORS, 
  formatter,
  showGrid = true,
}) => {
  const formatValue = formatter || (value => value);
  
  return (
    <ResponsiveContainer width="100%" height="100%">
      <RechartsLineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={useColorModeValue('gray.200', 'gray.700')} />}
        <XAxis 
          dataKey={xKey} 
          tick={{ fill: useColorModeValue('gray.600', 'gray.400') }}
          axisLine={{ stroke: useColorModeValue('gray.300', 'gray.600') }}
        />
        <YAxis 
          tick={{ fill: useColorModeValue('gray.600', 'gray.400') }}
          axisLine={{ stroke: useColorModeValue('gray.300', 'gray.600') }}
          tickFormatter={formatValue}
        />
        <Tooltip content={<CustomTooltip formatter={formatValue} />} />
        <Legend />
        {yKeys.map((key, index) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            stroke={colors[index % colors.length]}
            activeDot={{ r: 8 }}
            strokeWidth={2}
          />
        ))}
      </RechartsLineChart>
    </ResponsiveContainer>
  );
};

/**
 * Area Chart Component
 * 
 * @param {Object} props - Component props
 * @param {Array} props.data - Chart data
 * @param {String} props.xKey - Key for X-axis values
 * @param {Array} props.yKeys - Keys for Y-axis values
 * @param {Array} props.colors - Colors for areas
 * @param {Function} props.formatter - Value formatter function
 * @param {Boolean} props.showGrid - Whether to show grid lines
 * @param {Boolean} props.stacked - Whether to stack areas
 */
export const AreaChart = ({ 
  data, 
  xKey, 
  yKeys, 
  colors = COLORS, 
  formatter,
  showGrid = true,
  stacked = false,
}) => {
  const formatValue = formatter || (value => value);
  
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={useColorModeValue('gray.200', 'gray.700')} />}
        <XAxis 
          dataKey={xKey} 
          tick={{ fill: useColorModeValue('gray.600', 'gray.400') }}
          axisLine={{ stroke: useColorModeValue('gray.300', 'gray.600') }}
        />
        <YAxis 
          tick={{ fill: useColorModeValue('gray.600', 'gray.400') }}
          axisLine={{ stroke: useColorModeValue('gray.300', 'gray.600') }}
          tickFormatter={formatValue}
        />
        <Tooltip content={<CustomTooltip formatter={formatValue} />} />
        <Legend />
        {yKeys.map((key, index) => (
          <Area
            key={key}
            type="monotone"
            dataKey={key}
            stackId={stacked ? "1" : index}
            stroke={colors[index % colors.length]}
            fill={colors[index % colors.length]}
            fillOpacity={0.6}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );
};

/**
 * Bar Chart Component
 * 
 * @param {Object} props - Component props
 * @param {Array} props.data - Chart data
 * @param {String} props.xKey - Key for X-axis values
 * @param {Array} props.yKeys - Keys for Y-axis values
 * @param {Array} props.colors - Colors for bars
 * @param {Function} props.formatter - Value formatter function
 * @param {Boolean} props.showGrid - Whether to show grid lines
 * @param {Boolean} props.stacked - Whether to stack bars
 * @param {String} props.layout - Layout orientation ('vertical' or 'horizontal')
 */
export const BarChart = ({ 
  data, 
  xKey, 
  yKeys, 
  colors = COLORS, 
  formatter,
  showGrid = true,
  stacked = false,
  layout = 'vertical',
}) => {
  const formatValue = formatter || (value => value);
  const isVertical = layout === 'vertical';
  
  return (
    <ResponsiveContainer width="100%" height="100%">
      <RechartsBarChart
        data={data}
        layout={layout}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke={useColorModeValue('gray.200', 'gray.700')} />}
        <XAxis 
          dataKey={isVertical ? xKey : null}
          type={isVertical ? 'category' : 'number'}
          tick={{ fill: useColorModeValue('gray.600', 'gray.400') }}
          axisLine={{ stroke: useColorModeValue('gray.300', 'gray.600') }}
          tickFormatter={!isVertical ? formatValue : undefined}
        />
        <YAxis 
          dataKey={!isVertical ? xKey : null}
          type={!isVertical ? 'category' : 'number'}
          tick={{ fill: useColorModeValue('gray.600', 'gray.400') }}
          axisLine={{ stroke: useColorModeValue('gray.300', 'gray.600') }}
          tickFormatter={isVertical ? formatValue : undefined}
        />
        <Tooltip content={<CustomTooltip formatter={formatValue} />} />
        <Legend />
        {yKeys.map((key, index) => (
          <Bar
            key={key}
            dataKey={key}
            stackId={stacked ? "a" : index}
            fill={colors[index % colors.length]}
            radius={[4, 4, 0, 0]}
          />
        ))}
      </RechartsBarChart>
    </ResponsiveContainer>
  );
};

/**
 * Pie Chart Component
 * 
 * @param {Object} props - Component props
 * @param {Array} props.data - Chart data
 * @param {String} props.nameKey - Key for segment names
 * @param {String} props.valueKey - Key for segment values
 * @param {Array} props.colors - Colors for segments
 * @param {Function} props.formatter - Value formatter function
 * @param {Boolean} props.showLegend - Whether to show legend
 * @param {Number} props.innerRadius - Inner radius for donut chart (0 for pie)
 */
export const PieChart = ({ 
  data, 
  nameKey, 
  valueKey, 
  colors = COLORS, 
  formatter,
  showLegend = true,
  innerRadius = 0,
}) => {
  const formatValue = formatter || (value => value);
  
  return (
    <ResponsiveContainer width="100%" height="100%">
      <RechartsPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          outerRadius="80%"
          innerRadius={innerRadius}
          fill="#8884d8"
          dataKey={valueKey}
          nameKey={nameKey}
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip formatter={formatValue} />} />
        {showLegend && <Legend />}
      </RechartsPieChart>
    </ResponsiveContainer>
  );
};

/**
 * Gauge Chart Component (specialized donut chart)
 * 
 * @param {Object} props - Component props
 * @param {Number} props.value - Current value
 * @param {Number} props.max - Maximum value
 * @param {String} props.label - Chart label
 * @param {String} props.color - Primary color
 */
export const GaugeChart = ({ 
  value, 
  max = 100, 
  label = '', 
  color = COLORS[0],
}) => {
  // Calculate percentage
  const percentage = (value / max) * 100;
  
  // Prepare data for the donut chart
  const data = [
    { name: 'Value', value: percentage },
    { name: 'Remaining', value: 100 - percentage },
  ];
  
  return (
    <Box position="relative" height="100%">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            startAngle={180}
            endAngle={0}
            innerRadius="70%"
            outerRadius="90%"
            dataKey="value"
            cornerRadius={5}
          >
            <Cell fill={color} />
            <Cell fill={useColorModeValue('gray.100', 'gray.700')} />
          </Pie>
        </RechartsPieChart>
      </ResponsiveContainer>
      
      <Flex
        position="absolute"
        top="50%"
        left="0"
        right="0"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        transform="translateY(-40%)"
      >
        <Text fontSize="3xl" fontWeight="bold">
          {value}
        </Text>
        <Text fontSize="sm" color="gray.500">
          {label}
        </Text>
      </Flex>
    </Box>
  );
};
