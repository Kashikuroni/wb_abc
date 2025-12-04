"use client";
import * as React from "react";
import { format, differenceInDays, isAfter, startOfDay } from "date-fns";
import { ru } from "date-fns/locale";
import { CalendarIcon, Loader2 } from "lucide-react";
import type { DateRange } from "react-day-picker";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { ABCTable } from "@/components/abc-table";
import type { ABCItem } from "@/types/abc";
import WbOrdersApi from "@/services/wb/api";

export function ABCAnalysis() {
  const [date, setDate] = React.useState<DateRange | undefined>(undefined);
  const [data, setData] = React.useState<ABCItem[] | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const isDateTooOld = React.useMemo(() => {
    if (!date?.from) return false;

    const today = new Date();
    const daysDiff = differenceInDays(today, date.from);

    return daysDiff > 90;
  }, [date?.from]);

  const isDateInFuture = React.useMemo(() => {
    if (!date?.from) return false;

    const today = startOfDay(new Date());
    const dateFrom = startOfDay(date.from);

    if (isAfter(dateFrom, today)) {
      return true;
    }

    if (date?.to) {
      const dateTo = startOfDay(date.to);
      if (isAfter(dateTo, today)) {
        return true;
      }
    }

    return false;
  }, [date?.from, date?.to]);

  React.useEffect(() => {
    if (isDateInFuture) {
      setError("Нельзя выгрузить отчет из будущего");
      setData(null);
    } else if (isDateTooOld) {
      setError("Нельзя выгрузить отчет старше чем за 90 дней");
      setData(null);
    } else {
      setError(null);
    }
  }, [isDateTooOld, isDateInFuture]);

  const handleFetch = async () => {
    // Дополнительная проверка перед отправкой
    if (isDateInFuture) {
      setError("Нельзя выгрузить отчет из будущего");
      return;
    }

    if (isDateTooOld) {
      setError("Нельзя выгрузить отчет старше чем за 90 дней");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const dateRange = {
        date_from: date?.from
          ? { date: format(date.from, "yyyy-MM-dd") }
          : { date: format(new Date(), "yyyy-MM-dd") },
        date_to: date?.to ? { date: format(date.to, "yyyy-MM-dd") } : null,
      };

      const api = new WbOrdersApi();
      const result = await api.getAbcAnalytics(dateRange);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Произошла ошибка");
    } finally {
      setLoading(false);
    }
  };

  const isButtonDisabled = loading || isDateTooOld || isDateInFuture;

  return (
    <div className="container py-8 px-4 mx-auto">
      <h1 className="mb-6 text-3xl font-bold">ABC анализ</h1>
      <div className="flex flex-col gap-4 mb-8 sm:flex-row">
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={cn(
                "w-full sm:w-[300px] justify-start text-left font-normal",
                !date && "text-muted-foreground",
              )}
            >
              <CalendarIcon className="mr-2 w-4 h-4" />
              {date?.from ? (
                date.to ? (
                  <>
                    {format(date.from, "dd.MM.yyyy", { locale: ru })} -{" "}
                    {format(date.to, "dd.MM.yyyy", { locale: ru })}
                  </>
                ) : (
                  format(date.from, "dd.MM.yyyy", { locale: ru })
                )
              ) : (
                <span>Выберите диапазон дат</span>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="p-0 w-auto" align="start">
            <Calendar
              mode="range"
              defaultMonth={date?.from}
              selected={date}
              onSelect={setDate}
              numberOfMonths={2}
            />
          </PopoverContent>
        </Popover>
        <Button
          onClick={handleFetch}
          disabled={isButtonDisabled}
          className="sm:w-auto"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 w-4 h-4 animate-spin" />
              Загрузка...
            </>
          ) : (
            "Получить"
          )}
        </Button>
      </div>

      {error && (
        <div className="py-3 px-4 mb-6 rounded-md bg-destructive/10 text-destructive">
          {error}
        </div>
      )}

      {data && <ABCTable data={data} />}

      {!data && !loading && !error && (
        <div className="py-12 text-center text-muted-foreground">
          Выберите диапазон дат и нажмите &quot;Получить&quot; для загрузки
          данных
        </div>
      )}
    </div>
  );
}
