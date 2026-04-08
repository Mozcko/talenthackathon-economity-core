import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useMemo, useState, useEffect } from 'react';

interface ChartDataProps {
  data: {
    id: number;
    entidad: string;
    tipo: string;
    monto: number;
    tasa: number;
  }[];
}

const THEME_VARIABLES = [
  '--color-primary-container',
  '--color-secondary',
  '--color-secondary-fixed-dim',
  '--color-tertiary-container',
  '--color-on-tertiary-fixed'
];

export default function AssetDistributionChart({ data }: ChartDataProps) {
  const [isReady, setIsReady] = useState(false);
  const [chartColors, setChartColors] = useState<string[]>([]);

  useEffect(() => {
    // Resolve CSS variables to actual computed values (hex/rgb) for Recharts animations
    const rootStyles = getComputedStyle(document.documentElement);
    const resolvedColors = THEME_VARIABLES.map((variable) => 
      rootStyles.getPropertyValue(variable).trim()
    );
    setChartColors(resolvedColors);

    // This small delay prevents the "flying from top-left" Recharts bug
    // by allowing the parent container to fully calculate its layout 
    // dimensions (0x0 initial size) before rendering the chart.
    const timer = setTimeout(() => setIsReady(true), 150);
    return () => clearTimeout(timer);
  }, []);

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
    <div className="w-full h-[300px]">
      {isReady && (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={90}
              paddingAngle={4}
              dataKey="value"
              isAnimationActive={true}
              animationDuration={1200}
              animationEasing="ease-out"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value: number) => formatCurrency(value)}
              contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', fontWeight: 'bold' }}
            />
            <Legend verticalAlign="bottom" height={36} iconType="circle" />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}