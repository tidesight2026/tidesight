import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface MortalityTrendChartProps {
  data: Array<{ date: string; rate: number }>
}

export default function MortalityTrendChart({ data }: MortalityTrendChartProps) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="rate" stroke="#ef4444" strokeWidth={2} name="معدل النفوق (%)" />
      </LineChart>
    </ResponsiveContainer>
  )
}

