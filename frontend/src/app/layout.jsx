import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata = {
  title: "CA Final Quiz App",
  description: "Quiz and analytics platform for CA Final preparation."
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}

