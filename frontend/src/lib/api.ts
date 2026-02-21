const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Types ──
export interface DetectionResult {
    id: number;
    created_at: string;
    num_detections: number;
    result_image_url: string;
    boxes?: Array<{
        x1: number;
        y1: number;
        x2: number;
        y2: number;
        conf: number;
        label: string;
    }>;
}

export interface HistoryParams {
    page?: number;
    page_size?: number;
    search?: string;
    date_from?: string;
    date_to?: string;
    min_detections?: number;
    max_detections?: number;
}

export interface HistoryResponse {
    items: DetectionResult[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

// ── API Functions ──

/** Upload ảnh và detect người */
export async function detectPeople(file: File): Promise<DetectionResult> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/api/detect`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        const error = await res.text();
        throw new Error(`Detection failed: ${error}`);
    }
    return res.json();
}

/** Lấy lịch sử detection */
export async function getHistory(
    params: HistoryParams = {}
): Promise<HistoryResponse> {
    const searchParams = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
            searchParams.set(key, String(value));
        }
    });

    const res = await fetch(`${API_BASE}/api/history?${searchParams}`);
    if (!res.ok) throw new Error(`History fetch failed: ${res.statusText}`);
    return res.json();
}

/** Build full URL cho result image */
export function getResultImageUrl(path: string): string {
    return `${API_BASE}${path}`;
}
