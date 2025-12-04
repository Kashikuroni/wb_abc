"use client"

import { useEffect, useState } from "react"

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
  photo_url?: string
  allows_write_to_pm?: boolean
}

export function useTelegramWebApp() {
  const [user, setUser] = useState<TelegramUser | null>(null)
  const [initData, setInitData] = useState<string>("")
  const [isReady, setIsReady] = useState(false)
  const [webApp, setWebApp] = useState<any>(null)
  const [telegramData, setTelegramData] = useState({
    chatInstance: "",
    chatType: "",
    startParam: "",
    authDate: "",
    hash: "",
  })

  useEffect(() => {
    if (typeof window === "undefined") return

    // Dynamically import WebApp only on client side
    import("@twa-dev/sdk").then(({ default: WebApp }) => {
      if (!WebApp?.initDataUnsafe) return

      try {
        WebApp.ready()

        const userData = WebApp.initDataUnsafe.user
        const initDataString = WebApp.initData

        if (userData) setUser(userData)
        setInitData(initDataString)
        setWebApp(WebApp)
        setTelegramData({
          chatInstance: WebApp.initDataUnsafe.chat_instance || "",
          chatType: WebApp.initDataUnsafe.chat_type || "",
          startParam: WebApp.initDataUnsafe.start_param || "",
          authDate: String(WebApp.initDataUnsafe.auth_date || ""),
          hash: WebApp.initDataUnsafe.hash || "",
        })
        setIsReady(true)

        WebApp.expand()
        WebApp.enableClosingConfirmation()
      } catch (err) {
        console.error("Telegram WebApp init error:", err)
      }
    })
  }, [])

  return {
    user,
    initData,
    webApp,
    isReady,
    ...telegramData,
  }
}
