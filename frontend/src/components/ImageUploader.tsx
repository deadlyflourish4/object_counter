"use client";
import { useState, useRef, DragEvent, ChangeEvent } from "react";
import styles from "./ImageUploader.module.css";

interface Props {
    onFileSelected: (file: File) => void;
    isLoading: boolean;
}

export default function ImageUploader({ onFileSelected, isLoading }: Props) {
    const [preview, setPreview] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [fileName, setFileName] = useState<string>("");
    const inputRef = useRef<HTMLInputElement>(null);

    const handleFile = (file: File) => {
        const allowed = ["image/jpeg", "image/png", "image/webp"];
        if (!allowed.includes(file.type)) {
            alert("Chỉ chấp nhận JPEG, PNG, WebP");
            return;
        }

        setFileName(file.name);
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target?.result as string);
        reader.readAsDataURL(file);
        onFileSelected(file);
    };

    const onDrop = (e: DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    };

    const onChange = (e: ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) handleFile(file);
    };

    return (
        <div className={styles.wrapper}>
            <div
                className={`${styles.dropzone} ${isDragging ? styles.dragging : ""} ${preview ? styles.hasPreview : ""}`}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={onDrop}
                onClick={() => inputRef.current?.click()}
            >
                <input
                    ref={inputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    hidden
                    onChange={onChange}
                />

                {preview ? (
                    <div className={styles.previewContainer}>
                        <img src={preview} alt="Preview" className={styles.previewImage} />
                        <div className={styles.previewOverlay}>
                            <span>Click to change</span>
                        </div>
                    </div>
                ) : (
                    <div className={styles.placeholder}>
                        <div className={styles.uploadIcon}>📁</div>
                        <p className={styles.mainText}>Drag & drop image here</p>
                        <p className={styles.subText}>or click to browse</p>
                        <p className={styles.formats}>JPEG, PNG, WebP • Max 10MB</p>
                    </div>
                )}

                {isLoading && (
                    <div className={styles.loadingOverlay}>
                        <div className={styles.spinner}></div>
                        <p>Detecting...</p>
                    </div>
                )}
            </div>
            {fileName && <p className={styles.fileName}>{fileName}</p>}
        </div>
    );
}
