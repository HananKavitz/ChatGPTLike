import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

// Chart colors for dark theme
const CHART_COLORS = [
  '#10a37f', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444',
  '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'
]

const ChartView = ({ visualization }) => {
  if (!visualization) return null

  const { chart_type, chart_config } = visualization

  let chartData
  try {
    chartData = typeof chart_config === 'string' ? JSON.parse(chart_config) : chart_config
  } catch (e) {
    console.error('Failed to parse chart config:', e)
    return null
  }

  if (!chartData || !chartData.data || chartData.data.length === 0) {
    return null
  }

  const renderChart = () => {
    switch (chart_type.toLowerCase()) {
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData.data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey={chartData.valueKey || 'value'}
              >
                {chartData.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#2F2F2F',
                  border: '1px solid #424242',
                  borderRadius: '8px',
                }}
                itemStyle={{ color: '#ECECF1' }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#424242" />
              <XAxis
                dataKey={chartData.xKey || 'name'}
                stroke="#C5C5D2"
                tick={{ fill: '#C5C5D2' }}
              />
              <YAxis
                stroke="#C5C5D2"
                tick={{ fill: '#C5C5D2' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#2F2F2F',
                  border: '1px solid #424242',
                  borderRadius: '8px',
                }}
                itemStyle={{ color: '#ECECF1' }}
              />
              <Legend />
              <Bar
                dataKey={chartData.yKey || 'value'}
                fill={CHART_COLORS[0]}
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#424242" />
              <XAxis
                dataKey={chartData.xKey || 'name'}
                stroke="#C5C5D2"
                tick={{ fill: '#C5C5D2' }}
              />
              <YAxis
                stroke="#C5C5D2"
                tick={{ fill: '#C5C5D2' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#2F2F2F',
                  border: '1px solid #424242',
                  borderRadius: '8px',
                }}
                itemStyle={{ color: '#ECECF1' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey={chartData.yKey || 'value'}
                stroke={CHART_COLORS[0]}
                strokeWidth={2}
                dot={{ fill: CHART_COLORS[0], r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart data={chartData.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#424242" />
              <XAxis
                type="number"
                dataKey={chartData.xKey || 'x'}
                name={chartData.xLabel || 'X'}
                stroke="#C5C5D2"
                tick={{ fill: '#C5C5D2' }}
              />
              <YAxis
                type="number"
                dataKey={chartData.yKey || 'y'}
                name={chartData.yLabel || 'Y'}
                stroke="#C5C5D2"
                tick={{ fill: '#C5C5D2' }}
              />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                contentStyle={{
                  backgroundColor: '#2F2F2F',
                  border: '1px solid #424242',
                  borderRadius: '8px',
                }}
                itemStyle={{ color: '#ECECF1' }}
              />
              <Scatter name={chartData.name || 'Data'} fill={CHART_COLORS[0]} />
            </ScatterChart>
          </ResponsiveContainer>
        )

      default:
        return (
          <div className="p-4 bg-bg-secondary rounded-lg text-text-secondary">
            <p>Unknown chart type: {chart_type}</p>
          </div>
        )
    }
  }

  return (
    <div className="my-4 p-4 bg-bg-secondary rounded-lg border border-border">
      {chartData.title && (
        <h3 className="text-lg font-semibold mb-4 text-text-primary">{chartData.title}</h3>
      )}
      {renderChart()}
    </div>
  )
}

export default ChartView
