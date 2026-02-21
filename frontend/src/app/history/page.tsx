"use client";
import { useState, useEffect, useCallback } from "react";
import { getHistory, HistoryResponse, HistoryParams, getResultImageUrl } from "@/lib/api";
import styles from "./page.module.css";

export default function HistoryPage() {
    const [data, setData] = useState<HistoryResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [viewImage, setViewImage] = useState<string | null>(null);

    // Filters
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState("");
    const [dateFrom, setDateFrom] = useState("");
    const [dateTo, setDateTo] = useState("");
    const [minDetections, setMinDetections] = useState("");
    const [maxDetections, setMaxDetections] = useState("");

    const fetchHistory = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const params: HistoryParams = {
                page,
                page_size: 10,
            };
            if (search) params.search = search;
            if (dateFrom) params.date_from = dateFrom;
            if (dateTo) params.date_to = dateTo;
            if (minDetections) params.min_detections = parseInt(minDetections);
            if (maxDetections) params.max_detections = parseInt(maxDetections);

            const result = await getHistory(params);
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load history");
        } finally {
            setIsLoading(false);
        }
    }, [page, search, dateFrom, dateTo, minDetections, maxDetections]);

    useEffect(() => {
        fetchHistory();
    }, [fetchHistory]);

    const handleFilter = () => {
        setPage(1);
        fetchHistory();
    };

    const handleClear = () => {
        setSearch("");
        setDateFrom("");
        setDateTo("");
        setMinDetections("");
        setMaxDetections("");
        setPage(1);
    };

    return (
        <div className={styles.page}>
            <div className={styles.header}>
                <h1 className={styles.title}>Detection History</h1>
                <p className={styles.subtitle}>
                    Browse and filter past detection results
                </p>
            </div>

            {/* Filters */}
            <div className={styles.filterPanel}>
                <div className={styles.filterRow}>
                    <input
                        type="text"
                        placeholder="🔍 Search filename..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className={styles.searchInput}
                        onKeyDown={(e) => e.key === "Enter" && handleFilter()}
                    />
                    <input
                        type="date"
                        value={dateFrom}
                        onChange={(e) => setDateFrom(e.target.value)}
                        className={styles.dateInput}
                        placeholder="From"
                    />
                    <input
                        type="date"
                        value={dateTo}
                        onChange={(e) => setDateTo(e.target.value)}
                        className={styles.dateInput}
                        placeholder="To"
                    />
                </div>
                <div className={styles.filterRow}>
                    <input
                        type="number"
                        placeholder="Min people"
                        value={minDetections}
                        onChange={(e) => setMinDetections(e.target.value)}
                        className={styles.numberInput}
                        min="0"
                    />
                    <input
                        type="number"
                        placeholder="Max people"
                        value={maxDetections}
                        onChange={(e) => setMaxDetections(e.target.value)}
                        className={styles.numberInput}
                        min="0"
                    />
                    <button className={styles.filterButton} onClick={handleFilter}>
                        Filter
                    </button>
                    <button className={styles.clearButton} onClick={handleClear}>
                        Clear
                    </button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className={styles.error}>⚠️ {error}</div>
            )}

            {/* Loading */}
            {isLoading && (
                <div className={styles.loading}>
                    <div className={styles.spinner}></div>
                    <p>Loading...</p>
                </div>
            )}

            {/* Table */}
            {!isLoading && data && (
                <>
                    <div className={styles.tableWrapper}>
                        <table className={styles.table}>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Time</th>
                                    <th>People</th>
                                    <th>Result</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.items.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className={styles.emptyRow}>
                                            No records found
                                        </td>
                                    </tr>
                                ) : (
                                    data.items.map((item) => (
                                        <tr key={item.id}>
                                            <td className={styles.idCell}>{item.id}</td>
                                            <td className={styles.timeCell}>
                                                {new Date(item.created_at).toLocaleString("vi-VN")}
                                            </td>
                                            <td>
                                                <span className={styles.badge}>
                                                    {item.num_detections}
                                                </span>
                                            </td>
                                            <td>
                                                <img
                                                    src={getResultImageUrl(item.result_image_url)}
                                                    alt={`Result ${item.id}`}
                                                    className={styles.thumbnail}
                                                    onClick={() => setViewImage(getResultImageUrl(item.result_image_url))}
                                                />
                                            </td>
                                            <td>
                                                <button
                                                    className={styles.viewButton}
                                                    onClick={() => setViewImage(getResultImageUrl(item.result_image_url))}
                                                >
                                                    View
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    <div className={styles.pagination}>
                        <button
                            className={styles.pageButton}
                            disabled={page <= 1}
                            onClick={() => setPage(page - 1)}
                        >
                            ← Prev
                        </button>
                        <span className={styles.pageInfo}>
                            Page {data.page} of {data.total_pages}
                            <span className={styles.totalCount}> ({data.total} records)</span>
                        </span>
                        <button
                            className={styles.pageButton}
                            disabled={page >= data.total_pages}
                            onClick={() => setPage(page + 1)}
                        >
                            Next →
                        </button>
                    </div>
                </>
            )}

            {/* Image Modal */}
            {viewImage && (
                <div className={styles.modal} onClick={() => setViewImage(null)}>
                    <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                        <button className={styles.modalClose} onClick={() => setViewImage(null)}>
                            ✕
                        </button>
                        <img src={viewImage} alt="Full result" className={styles.modalImage} />
                    </div>
                </div>
            )}
        </div>
    );
}
