import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { 
  BarChart3, 
  LineChart as LineChartIcon, 
  PieChart as PieChartIcon,
  Scatter as ScatterIcon,
  Download,
  TrendingUp,
  Activity
} from "lucide-react";
import { toast } from "sonner";

interface Column {
  key: string;
  label: string;
  type: 'string' | 'number' | 'date' | 'boolean';
}

interface ChartData {
  [key: string]: any;
}

interface DataVisualizationProps {
  data: any[][];
  columns: Column[];
  title?: string;
  className?: string;
}

type ChartType = 'bar' | 'line' | 'area' | 'scatter' | 'pie';

const COLORS = [
  '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00',
  '#0088fe', '#00c49f', '#ffbb28', '#ff8042', '#8dd1e1'
];

const DataVisualization = ({ data, columns, title, className }: DataVisualizationProps) => {
  const [chartType, setChartType] = useState<ChartType>('bar');
  const [xAxis, setXAxis] = useState<string>('');
  const [yAxis, setYAxis] = useState<string>('');

  // Convert array data to object format for charts
  const chartData: ChartData[] = data.map((row, index) => {
    const rowData: ChartData = { _index: index };
    columns.forEach((col, colIndex) => {
      rowData[col.key] = row[colIndex];
    });
    return rowData;
  });

  // Get numeric columns for Y-axis
  const numericColumns = columns.filter(col => col.type === 'number');
  const stringColumns = columns.filter(col => col.type === 'string');
  const dateColumns = columns.filter(col => col.type === 'date');

  // Auto-select default axes
  const defaultXAxis = stringColumns[0]?.key || dateColumns[0]?.key || columns[0]?.key || '';
  const defaultYAxis = numericColumns[0]?.key || columns[1]?.key || '';

  const currentXAxis = xAxis || defaultXAxis;
  const currentYAxis = yAxis || defaultYAxis;

  const handleExportChart = (format: 'png' | 'svg' | 'pdf') => {
    toast.info(`Export to ${format.toUpperCase()} functionality would be implemented here`);
  };

  const getChartIcon = (type: ChartType) => {
    switch (type) {
      case 'bar': return <BarChart3 className="w-4 h-4" />;
      case 'line': return <LineChartIcon className="w-4 h-4" />;
      case 'area': return <Activity className="w-4 h-4" />;
      case 'scatter': return <ScatterIcon className="w-4 h-4" />;
      case 'pie': return <PieChartIcon className="w-4 h-4" />;
      default: return <BarChart3 className="w-4 h-4" />;
    }
  };

  const renderChart = () => {
    if (!currentXAxis || !currentYAxis || chartData.length === 0) {
      return (
        <div className="flex items-center justify-center h-64 text-muted-foreground">
          <div className="text-center">
            <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Select X and Y axes to display chart</p>
          </div>
        </div>
      );
    }

    const commonProps = {
      data: chartData.slice(0, 100), // Limit data points for performance
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    };

    switch (chartType) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey={currentXAxis} 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar 
                dataKey={currentYAxis} 
                fill={COLORS[0]} 
                name={columns.find(c => c.key === currentYAxis)?.label || currentYAxis}
              />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey={currentXAxis} 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey={currentYAxis} 
                stroke={COLORS[0]} 
                strokeWidth={2}
                name={columns.find(c => c.key === currentYAxis)?.label || currentYAxis}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'area':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey={currentXAxis} 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Area 
                type="monotone" 
                dataKey={currentYAxis} 
                stroke={COLORS[0]} 
                fill={COLORS[0]}
                fillOpacity={0.3}
                name={columns.find(c => c.key === currentYAxis)?.label || currentYAxis}
              />
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                type="number"
                dataKey={currentXAxis} 
                tick={{ fontSize: 12 }}
                name={columns.find(c => c.key === currentXAxis)?.label || currentXAxis}
              />
              <YAxis 
                type="number"
                dataKey={currentYAxis} 
                tick={{ fontSize: 12 }}
                name={columns.find(c => c.key === currentYAxis)?.label || currentYAxis}
              />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Scatter 
                dataKey={currentYAxis} 
                fill={COLORS[0]}
                name={`${columns.find(c => c.key === currentXAxis)?.label || currentXAxis} vs ${columns.find(c => c.key === currentYAxis)?.label || currentYAxis}`}
              />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'pie':
        // Aggregate data for pie chart
        const pieData = chartData.reduce((acc: any[], item) => {
          const key = item[currentXAxis];
          const value = Number(item[currentYAxis]) || 0;
          const existing = acc.find(d => d.name === key);
          
          if (existing) {
            existing.value += value;
          } else {
            acc.push({ name: key, value });
          }
          
          return acc;
        }, []).slice(0, 10); // Limit to top 10 categories

        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return <div>Unsupported chart type</div>;
    }
  };

  const getQuickInsights = () => {
    if (!currentYAxis || numericColumns.length === 0) return null;

    const yAxisData = chartData.map(d => Number(d[currentYAxis])).filter(v => !isNaN(v));
    if (yAxisData.length === 0) return null;

    const sum = yAxisData.reduce((a, b) => a + b, 0);
    const avg = sum / yAxisData.length;
    const min = Math.min(...yAxisData);
    const max = Math.max(...yAxisData);

    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-sm font-medium text-muted-foreground">Total</div>
            <div className="text-2xl font-bold">{sum.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-sm font-medium text-muted-foreground">Average</div>
            <div className="text-2xl font-bold">{avg.toFixed(2)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-sm font-medium text-muted-foreground">Min</div>
            <div className="text-2xl font-bold">{min.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-sm font-medium text-muted-foreground">Max</div>
            <div className="text-2xl font-bold">{max.toLocaleString()}</div>
          </CardContent>
        </Card>
      </div>
    );
  };

  if (data.length === 0 || columns.length === 0) {
    return (
      <Card className={className}>
        <CardContent className="py-12">
          <div className="text-center">
            <TrendingUp className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No Data to Visualize</h3>
            <p className="text-muted-foreground">
              Upload and process data to see visualizations here.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{title || "Data Visualization"}</CardTitle>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => handleExportChart('png')}
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
        
        {/* Chart Controls */}
        <div className="flex flex-col sm:flex-row gap-4 mt-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Chart Type:</span>
            <Tabs value={chartType} onValueChange={(value) => setChartType(value as ChartType)}>
              <TabsList className="grid grid-cols-5 w-fit">
                <TabsTrigger value="bar" className="px-2">
                  <BarChart3 className="w-4 h-4" />
                </TabsTrigger>
                <TabsTrigger value="line" className="px-2">
                  <LineChartIcon className="w-4 h-4" />
                </TabsTrigger>
                <TabsTrigger value="area" className="px-2">
                  <Activity className="w-4 h-4" />
                </TabsTrigger>
                <TabsTrigger value="scatter" className="px-2">
                  <ScatterIcon className="w-4 h-4" />
                </TabsTrigger>
                <TabsTrigger value="pie" className="px-2">
                  <PieChartIcon className="w-4 h-4" />
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">X-Axis:</span>
              <Select value={currentXAxis} onValueChange={setXAxis}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Select column" />
                </SelectTrigger>
                <SelectContent>
                  {columns.map(col => (
                    <SelectItem key={col.key} value={col.key}>
                      {col.label}
                      <Badge variant="outline" className="ml-2 text-xs">
                        {col.type}
                      </Badge>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Y-Axis:</span>
              <Select value={currentYAxis} onValueChange={setYAxis}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Select column" />
                </SelectTrigger>
                <SelectContent>
                  {columns.map(col => (
                    <SelectItem key={col.key} value={col.key}>
                      {col.label}
                      <Badge variant="outline" className="ml-2 text-xs">
                        {col.type}
                      </Badge>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Chart */}
        <div className="mb-6">
          {renderChart()}
        </div>
        
        {/* Quick Insights */}
        {getQuickInsights()}
        
        {/* Chart Info */}
        <div className="mt-4 text-xs text-muted-foreground">
          Showing {Math.min(chartData.length, 100)} of {chartData.length} data points
          {chartData.length > 100 && " (limited for performance)"}
        </div>
      </CardContent>
    </Card>
  );
};

export default DataVisualization;