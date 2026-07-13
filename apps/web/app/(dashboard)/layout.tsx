import Link from "next/link";
import type { ReactNode } from "react";

const navItems = [
  { href: "/knowledge-bases", label: "Knowledge Bases" },
  { href: "/agents", label: "Agents" },
  { href: "/runtime-logs", label: "Runtime Logs" },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-title">Fusion Agent Studio</span>
          <span className="brand-caption">Knowledge-grounded agents</span>
        </div>
        <nav className="nav-list" aria-label="Main navigation">
          {navItems.map((item) => (
            <Link className="nav-link" href={item.href} key={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
