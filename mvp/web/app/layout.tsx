import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lunetra IA · ¿Lleno hoy o espero?",
  description:
    "Asistente de IA que te dice si conviene cargar gasolina hoy o esperar, con una banda de precio justo de referencia.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0f1b2d",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
