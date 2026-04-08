import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useMemo } from 'react';

interface ChartDataProps {
  data: {
    id: number;
    entidad: string;
    tipo: string;
    monto: number;
    tasa: number;
  }[];
}

const COLORS = ['#4f46e5', '#0ea5e9', '#10b981', '#f59e0b', '#8b5cf6'];

export default function AssetDistributionChart({ data }: ChartDataProps) {
  // Agrupar los montos por "tipo" (Tomamos la primera parte antes del guion si lo hay)
  const chartData = useMemo(() => {
    const grouped = data.reduce((acc, curr) => {
      const type = curr.tipo.split('-')[0].trim();
      if (!acc[type]) acc[type] = 0;
      acc[type] += curr.monto;
      return acc;
    }, {} as Record<string, number>);

    return Object.keys(grouped).map((key) => ({
      name: key,
      value: grouped[key],
    }));
  }, [data]);

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(value);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={70}
          outerRadius={90}
          paddingAngle={4}
          dataKey="value"
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip 
          formatter={(value: number) => formatCurrency(value)}
          contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', fontWeight: 'bold' }}
        />
        <Legend verticalAlign="bottom" height={36} iconType="circle" />
      </PieChart>
    </ResponsiveContainer>
  );
}