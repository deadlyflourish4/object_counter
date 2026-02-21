"use client";
import { useState } from "react";
import ImageUploader from "@/components/ImageUploader";
import DetectionResult from "@/components/DetectionResult";
import { detectPeople, DetectionResult as DetectionResultType } from "@/lib/api";
import styles from "./page.module.css";

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<DetectionResultType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelected = (file: File) => {
    setSelectedFile(file);
    setResult(null);
    setError(null);
  };

  const handleDetect = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await detectPeople(selectedFile);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Detection failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Upload & Detect</h1>
        <p className={styles.subtitle}>
          Upload an image to detect and count people
        </p>
      </div>

      <div className={styles.uploadSection}>
        <ImageUploader
          onFileSelected={handleFileSelected}
          isLoading={isLoading}
        />

        <button
          className={styles.detectButton}
          onClick={handleDetect}
          disabled={!selectedFile || isLoading}
        >
          {isLoading ? "Detecting..." : "🔍 Detect People"}
        </button>
      </div>

      {error && (
        <div className={styles.error}>
          <span>⚠️</span> {error}
        </div>
      )}

      {result && (
        <div className={styles.resultSection}>
          <h2 className={styles.resultTitle}>Detection Result</h2>
          <DetectionResult result={result} />
        </div>
      )}
    </div>
  );
}
