import { DetectionResult as Result } from "@/lib/api";
import { getResultImageUrl } from "@/lib/api";
import styles from "./DetectionResult.module.css";

interface Props {
    result: Result;
}

export default function DetectionResult({ result }: Props) {
    return (
        <div className={styles.container}>
            <div className={styles.imageWrapper}>
                <img
                    src={getResultImageUrl(result.result_image_url)}
                    alt="Detection result"
                    className={styles.resultImage}
                />
            </div>

            <div className={styles.stats}>
                <div className={styles.countCard}>
                    <span className={styles.countNumber}>{result.num_detections}</span>
                    <span className={styles.countLabel}>People Detected</span>
                </div>

                <div className={styles.timestamp}>
                    {new Date(result.created_at).toLocaleString("vi-VN")}
                </div>

                {result.boxes && result.boxes.length > 0 && (
                    <div className={styles.boxList}>
                        <h4 className={styles.boxListTitle}>Confidence Scores</h4>
                        <ul>
                            {result.boxes.map((box, i) => (
                                <li key={i} className={styles.boxItem}>
                                    <span className={styles.personLabel}>Person {i + 1}</span>
                                    <div className={styles.confidenceBar}>
                                        <div
                                            className={styles.confidenceFill}
                                            style={{ width: `${box.conf * 100}%` }}
                                        />
                                    </div>
                                    <span className={styles.confidenceValue}>
                                        {(box.conf * 100).toFixed(1)}%
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
