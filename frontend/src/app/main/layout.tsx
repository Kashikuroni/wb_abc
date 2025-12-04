import { AuthProvider } from "@/context/auth";

export default function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <AuthProvider>
      <div className="flex-1 min-h-0 max-h-full overflow-hidden p-4">
        {children}
      </div>
    </AuthProvider>
  );
}
