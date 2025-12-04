"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import type { ABCItem } from "@/types/abc"
import { cn } from "@/lib/utils"

interface ABCTableProps {
  data: ABCItem[]
}

export function ABCTable({ data }: ABCTableProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("ru-RU", {
      style: "currency",
      currency: "RUB",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${value.toFixed(2)}%`
  }

  const getCategoryBadge = (category: "A" | "B" | "C") => {
    const styles = {
      A: "bg-emerald-500/15 text-emerald-700 hover:bg-emerald-500/20",
      B: "bg-amber-500/15 text-amber-700 hover:bg-amber-500/20",
      C: "bg-rose-500/15 text-rose-700 hover:bg-rose-500/20",
    }

    return (
      <Badge variant="secondary" className={cn("font-semibold", styles[category])}>
        {category}
      </Badge>
    )
  }

  const totals = data.reduce(
    (acc, item) => {
      acc[item.category].count++
      acc[item.category].revenue += item.revenue
      acc[item.category].orders += item.orders_count
      acc.total.revenue += item.revenue
      acc.total.orders += item.orders_count
      return acc
    },
    {
      A: { count: 0, revenue: 0, orders: 0 },
      B: { count: 0, revenue: 0, orders: 0 },
      C: { count: 0, revenue: 0, orders: 0 },
      total: { revenue: 0, orders: 0 },
    },
  )

  return (
    <div className="space-y-6">
      {/* Сводка по категориям */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {(["A", "B", "C"] as const).map((cat) => (
          <div
            key={cat}
            className={cn(
              "rounded-lg border p-4",
              cat === "A" && "border-emerald-200 bg-emerald-50/50",
              cat === "B" && "border-amber-200 bg-amber-50/50",
              cat === "C" && "border-rose-200 bg-rose-50/50",
            )}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-muted-foreground">Категория {cat}</span>
              {getCategoryBadge(cat)}
            </div>
            <div className="space-y-1">
              <p className="text-2xl font-bold">{totals[cat].count} товаров</p>
              <p className="text-sm text-muted-foreground">
                Выручка: {formatCurrency(totals[cat].revenue)} (
                {totals.total.revenue > 0 ? formatPercent((totals[cat].revenue / totals.total.revenue) * 100) : "0%"})
              </p>
              <p className="text-sm text-muted-foreground">Заказов: {totals[cat].orders.toLocaleString("ru-RU")}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Таблица с данными */}
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[80px]">Категория</TableHead>
              <TableHead>Артикул</TableHead>
              <TableHead>nm_id</TableHead>
              <TableHead>Наименование</TableHead>
              <TableHead>Бренд</TableHead>
              <TableHead className="text-right">Заказов</TableHead>
              <TableHead className="text-right">Выручка</TableHead>
              <TableHead className="text-right">Доля</TableHead>
              <TableHead className="text-right">Накопл. доля</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((item, index) => (
              <TableRow key={`${item.nm_id}-${index}`}>
                <TableCell>{getCategoryBadge(item.category)}</TableCell>
                <TableCell className="font-mono text-sm">{item.supplier_article}</TableCell>
                <TableCell className="font-mono text-sm">{item.nm_id}</TableCell>
                <TableCell className="max-w-[200px] truncate" title={item.subject}>
                  {item.subject}
                </TableCell>
                <TableCell>{item.brand}</TableCell>
                <TableCell className="text-right">{item.orders_count.toLocaleString("ru-RU")}</TableCell>
                <TableCell className="text-right font-medium">{formatCurrency(item.revenue)}</TableCell>
                <TableCell className="text-right text-muted-foreground">{formatPercent(item.revenue_share)}</TableCell>
                <TableCell className="text-right text-muted-foreground">
                  {formatPercent(item.cumulative_share)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
