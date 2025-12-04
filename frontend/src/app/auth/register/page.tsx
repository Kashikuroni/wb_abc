"use client"
import { RegisterForm } from "@/components/auth/register-form";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md space-y-8">
        <RegisterForm />
      </div>
    </div>
  );
}
