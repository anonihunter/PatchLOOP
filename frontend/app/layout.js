import "./globals.css";

export const metadata = {
  title: "PatchLoop",
  description: "Adaptive software maintenance agent"
};

export default function RootLayout({ children }) {
  return <html lang="en"><body>{children}</body></html>;
}
