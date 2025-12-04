import { z } from "zod"

export const plasticSchema = z.object({
  name: z.string().min(1, "Название пластика обязательно"),
  purchaseLink: z.url("Введите корректную ссылку").or(z.literal("")),
  purchaseDate: z.date(),
  weight: z.number().positive("Вес должен быть положительным числом"),
  plasticType: z.string().min(1, "Выберите тип пластика"),
  color: z.string().min(1, "Выберите цвет"),
  price: z.number().nonnegative("Цена не может быть отрицательной"),
  brand: z.string().min(1, "Выберите бренд"),
})

export type PlasticFormData = z.infer<typeof plasticSchema>
