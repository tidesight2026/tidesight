import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface StatsChartProps {
  data: Array<{ name: string; value: number }>
  type?: 'line' | 'bar'
  color?: string
  label?: string
}

export default function StatsChart({ data, type = 'line', color = '#3b82f6', label = 'القيمة' }: StatsChartProps) {
  const chartData = data.map((item) => ({
    name: item.name,
    [label]: item.value,
  }))

  if (type === 'bar') {
    return (
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey={label} fill={color} />
        </BarChart>
      </ResponsiveContainer>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey={label} stroke={color} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  )
}

