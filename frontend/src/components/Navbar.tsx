"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./Navbar.module.css";

export default function Navbar() {
    const pathname = usePathname();

    return (
        <nav className={styles.navbar}>
            <div className={styles.brand}>
                <span className={styles.icon}>🎯</span>
                <span className={styles.title}>Person Counter</span>
            </div>
            <div className={styles.links}>
                <Link
                    href="/"
                    className={`${styles.link} ${pathname === "/" ? styles.active : ""}`}
                >
                    Upload
                </Link>
                <Link
                    href="/history"
                    className={`${styles.link} ${pathname === "/history" ? styles.active : ""}`}
                >
                    History
                </Link>
            </div>
        </nav>
    );
}
