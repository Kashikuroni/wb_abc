"use client";
import React, { createContext, useContext, type ReactNode } from "react";
import useSWR from "swr";
import { AuthApi } from "@/services";
import type { AuthContextType, User, Workspace } from "@/context/types";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const userFetcher = async (): Promise<User | null> => {
  try {
    return await AuthApi.getUser();
  } catch (error: any) {
    console.log("error")

    // if (typeof window !== "undefined") {
    //   window.location.href = "/auth/login";
    // }
    throw error;
  }
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data, isLoading, mutate } = useSWR<User | null>(
    "/auth/users/",
    userFetcher,
  );

  const user: User | null = data ?? null;
  const isAuthenticated = !!user;

  const refreshUser = async (): Promise<void> => {
    await mutate();
  };

  const clearAuth = async (): Promise<void> => {
    await mutate(null, false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading: isLoading,
        refreshUser,
        clearAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
};
