import { useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";

export type ScannerResultState =
  | "idle"
  | "initializing"
  | "ready"
  | "detected"
  | "processing"
  | "accepted"
  | "declined"
  | "camera_permission_denied"
  | "camera_error"
  | "network_error";

export interface StudentInfo {
  name: string;
  rollNo: string;
  department: string;
  year: string;
  registration: string;
}

export interface ScannerResult {
  state: ScannerResultState;
  reason?: string;
  student?: StudentInfo;
}

interface QRScannerProps {
  result: ScannerResult;
  lastQrPayload: string | null;
  onScan: (decodedText: string) => void;
  onReset: () => void;
  onCameraReady: () => void;
  onCameraError: (err: unknown) => void;
}

// File-level serialization queue and instance tracking to prevent concurrent camera clashes (especially in React 18 StrictMode dev)
let globalScannerPromise: Promise<unknown> = Promise.resolve();
let currentScannerInstance: Html5Qrcode | null = null;

const REASON_DESCRIPTIONS: Record<string, string> = {
  "ALREADY SCANNED": "This ticket has already been used for entry.",
  "TICKET EXPIRED": "This ticket is no longer valid for entry.",
  "INVALID QR CODE": "The scanned QR code could not be verified.",
  "TICKET NOT FOUND": "No matching ticket was found.",
  "TICKET REVOKED": "This ticket has been revoked and cannot be used.",
  "REGISTRATION NOT FOUND": "No valid registration was found for this attendee.",
  "EVENT ACCESS NOT PERMITTED": "This ticket is not authorized for this event.",
};

export default function QRScanner({
  result,
  lastQrPayload,
  onScan,
  onReset,
  onCameraReady,
  onCameraError,
}: QRScannerProps) {
  const [retryCount, setRetryCount] = useState(0);
  const scannerInstanceRef = useRef<Html5Qrcode | null>(null);

  // Keep references to callback props stable to prevent useEffect re-executions on state updates
  const onScanRef = useRef(onScan);
  const onCameraReadyRef = useRef(onCameraReady);
  const onCameraErrorRef = useRef(onCameraError);

  useEffect(() => {
    onScanRef.current = onScan;
    onCameraReadyRef.current = onCameraReady;
    onCameraErrorRef.current = onCameraError;
  });

  const shouldScan = result.state === "initializing" || result.state === "ready";

  // Camera initialization and cleanup lifecycle
  useEffect(() => {
    let isCancelled = false;
    let localScanner: Html5Qrcode | null = null;

    globalScannerPromise = globalScannerPromise
      .then(async () => {
        if (isCancelled) return;

        // Instantiate on the current DOM element
        const html5QrCode = new Html5Qrcode("qr-reader");
        localScanner = html5QrCode;
        currentScannerInstance = html5QrCode;
        scannerInstanceRef.current = html5QrCode;

        const qrboxFn = (width: number, height: number) => {
          const size = Math.min(width, height) * 0.7;
          return { width: size, height: size };
        };

        const onDecoded = (decodedText: string) => {
          if (!isCancelled) {
            // Instantly pause scan parsing to prevent duplicate scans
            try {
              html5QrCode.pause(true);
            } catch (e) {
              console.warn("Failed to pause scanner on detection:", e);
            }
            onScanRef.current(decodedText);
          }
        };

        const onFrameError = () => {};

        // Try environment/rear camera first
        try {
          await html5QrCode.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: qrboxFn },
            onDecoded,
            onFrameError
          );
        } catch {
          if (isCancelled) return;
          // Fallback: try front camera / webcam (e.g. desktop dev)
          try {
            await html5QrCode.start(
              { facingMode: "user" },
              { fps: 10, qrbox: qrboxFn },
              onDecoded,
              onFrameError
            );
          } catch (fallbackErr) {
            if (isCancelled) return;
            throw fallbackErr;
          }
        }

        if (isCancelled) {
          await html5QrCode.stop().catch(() => {});
          return;
        }

        onCameraReadyRef.current();
      })
      .catch((err) => {
        if (!isCancelled) {
          onCameraErrorRef.current(err);
        }
      });

    return () => {
      isCancelled = true;
      scannerInstanceRef.current = null;
      globalScannerPromise = globalScannerPromise.then(async () => {
        if (localScanner) {
          try {
            await localScanner.stop();
          } catch {
            // Ignore expected stop failures during clean unmounts
          }
          if (currentScannerInstance === localScanner) {
            currentScannerInstance = null;
          }
        }
      });
    };
  }, [retryCount]); // Only re-runs if operator clicks RETRY CAMERA explicitly

  // Sync pause/resume lifecycle with outcome screen transitions
  useEffect(() => {
    const html5QrCode = scannerInstanceRef.current;
    if (!html5QrCode) {
      return;
    }

    const isCameraActive = result.state === "ready" || result.state === "initializing";

    try {
      if (isCameraActive) {
        html5QrCode.resume();
        // If transitioning back to initializing (e.g. on reset/NEXT SCAN) and camera is already running,
        // trigger onCameraReady immediately to dismiss the loading overlay.
        if (result.state === "initializing") {
          onCameraReadyRef.current();
        }
      } else if (result.state !== "detected" && result.state !== "processing") {
        // Stop CPU parsing and freeze viewport feed on overlays (ACCEPTED, DECLINED, etc.)
        html5QrCode.pause(true);
      }
    } catch {
      // Safe guard against premature state synchronization checks
    }
  }, [result.state]);

  const handleRetry = () => {
    onReset();
    setRetryCount((c) => c + 1);
  };

  return (
    <div style={{ width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
      {/* Primary Camera Viewport Area (visible only when actively scanning) */}
      <div
        className="scanner-viewport-container"
        style={{
          width: "100%",
          aspectRatio: "1 / 1",
          position: "relative",
          display: shouldScan ? "flex" : "none",
          alignItems: "center",
          justifyContent: "center",
          overflow: "hidden",
          backgroundColor: "#0c0c0e",
          boxSizing: "border-box",
        }}
      >
        <div
          id="qr-reader"
          style={{
            width: "100%",
            height: "100%",
            display: "block",
          }}
        />

        {result.state === "initializing" && (
          <div className="camera-preview-sim" style={{ zIndex: 2 }}>
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ color: "var(--fg-white)", opacity: 0.8, marginBottom: "16px" }}
            >
              <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
              <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
              <path d="M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
              <line x1="2" y1="2" x2="22" y2="22" />
            </svg>
            <span style={{ fontSize: "9px", fontFamily: "var(--font-mono)", letterSpacing: "0.15em" }}>
              INITIALIZING CAMERA...
            </span>
          </div>
        )}

        {/* Subtle horizontal scan-line sweep */}
        <div className="scan-line" style={{ zIndex: 4 }} />
      </div>

      {/* Operational scanning instruction & status indicator */}
      {shouldScan && (
        <div style={{ marginTop: "24px", textAlign: "center", width: "100%" }}>
          <div className="scanner-instruction">
            ALIGN QR CODE INSIDE THE FRAME
          </div>
          <div style={{ marginTop: "12px" }}>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "8px", color: "var(--muted-gray)", letterSpacing: "0.2em", textTransform: "uppercase" }}>
              STATUS
            </span>
            <div className="scanner-status" style={{ marginTop: "2px" }}>
              {result.state === "ready" ? "READY" : "INITIALIZING CAMERA..."}
            </div>
          </div>
        </div>
      )}

      {/* Hidden DOM hook so html5-qrcode doesn't break when viewport container is hidden */}
      {!shouldScan && (
        <div id="qr-reader" style={{ display: "none" }} />
      )}

      {/* DETECTED — show raw QR payload for verification */}
      {result.state === "detected" && (
        <div className="result-card-overlay" style={{ zIndex: 5 }}>
          <div>
            <span className="outcome-badge success" style={{ borderColor: "var(--fg-white)", color: "var(--fg-white)" }}>
              QR DETECTED
            </span>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                color: "var(--muted-gray)",
                marginTop: "8px",
                letterSpacing: "0.05em",
              }}
            >
              RAW PAYLOAD
            </div>
            <div style={{ marginTop: "16px" }} />
            <div className="verification-card">
              <div className="verification-row" style={{ borderBottom: "none" }}>
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "11px",
                    color: "var(--fg-white)",
                    wordBreak: "break-all",
                    lineHeight: "1.6",
                  }}
                >
                  {lastQrPayload ?? "—"}
                </span>
              </div>
            </div>
          </div>
          <button className="scanner-btn" onClick={onReset}>
            NEXT SCAN
          </button>
        </div>
      )}

      {/* CAMERA ERRORS Views */}
      {(result.state === "camera_permission_denied" || result.state === "camera_error") && (
        <div className="result-card-overlay" style={{ zIndex: 6, background: "var(--bg-black)" }}>
          <div style={{ textAlign: "center", marginTop: "auto", marginBottom: "auto" }}>
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#ef4444"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ color: "#ef4444", opacity: 0.8, display: "block", margin: "0 auto 16px" }}
            >
              <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
              <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
              <path d="M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
              <line x1="2" y1="2" x2="22" y2="22" />
            </svg>
            <span className="outcome-badge error-scan">
              {result.state === "camera_permission_denied" ? "CAMERA ACCESS REQUIRED" : "CAMERA UNAVAILABLE"}
            </span>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                color: "var(--muted-gray)",
                marginTop: "16px",
                lineHeight: "1.6",
                padding: "0 16px",
              }}
            >
              {result.state === "camera_permission_denied"
                ? "Allow camera access in your browser settings and try again."
                : "Please verify your camera connection or try reloading the application."}
            </div>
          </div>
          <button className="scanner-btn" onClick={handleRetry}>
            RETRY CAMERA
          </button>
        </div>
      )}

      {/* ACCEPTED Scan Result View (Redesigned from scratch) */}
      {result.state === "accepted" && (
        <div className="animate-fade-in" style={{ width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
          {/* Centered Checkmark Box */}
          <div className="animate-slide-up" style={{ position: "relative", width: "80px", height: "80px", margin: "12px 0" }}>
            <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
              <div style={{ position: "absolute", top: 0, left: 0, width: "10px", height: "10px", borderTop: "2px solid #fff", borderLeft: "2px solid #fff" }} />
              <div style={{ position: "absolute", top: 0, right: 0, width: "10px", height: "10px", borderTop: "2px solid #fff", borderRight: "2px solid #fff" }} />
              <div style={{ position: "absolute", bottom: 0, left: 0, width: "10px", height: "10px", borderBottom: "2px solid #fff", borderLeft: "2px solid #fff" }} />
              <div style={{ position: "absolute", bottom: 0, right: 0, width: "10px", height: "10px", borderBottom: "2px solid #fff", borderRight: "2px solid #fff" }} />
            </div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "100%", height: "100%" }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
          </div>

          {/* Access Granted Header */}
          <div className="animate-slide-up delay-100" style={{ textAlign: "center", width: "100%", marginBottom: "16px" }}>
            <h1
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "24px",
                fontWeight: 700,
                color: "#ffffff",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                margin: "0 0 8px 0",
                lineHeight: "1.2",
              }}
            >
              ACCESS
              <br />
              GRANTED
            </h1>
            
            {/* Custom Separator Line */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", margin: "16px 0" }}>
              <div style={{ flex: 1, height: "1px", backgroundColor: "#18181b" }} />
              <div style={{ width: "6px", height: "6px", backgroundColor: "#3f3f46", margin: "0 10px" }} />
              <div style={{ flex: 1, height: "1px", backgroundColor: "#18181b" }} />
            </div>

            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                color: "var(--muted-gray)",
                letterSpacing: "0.2em",
                textTransform: "uppercase",
              }}
            >
              ENTRY RECORDED
            </span>
          </div>

          {/* Student Verification Identity Block */}
          {result.student && (
            <div className="animate-slide-up delay-200" style={{ textAlign: "center", width: "100%", marginBottom: "20px" }}>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "9px",
                  color: "var(--muted-gray)",
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                  marginBottom: "16px",
                }}
              >
                IDENTITY VERIFIED
              </div>
              
              <h2
                style={{
                  fontFamily: "var(--font-sans)",
                  fontSize: "22px",
                  fontWeight: 700,
                  color: "#ffffff",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  margin: "0 0 4px 0",
                }}
              >
                {result.student.name}
              </h2>
              
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  color: "var(--muted-gray)",
                  letterSpacing: "0.1em",
                  marginBottom: "12px",
                }}
              >
                {result.student.rollNo}
              </div>

              {/* Separator line */}
              <div style={{ width: "100%", height: "1px", backgroundColor: "#18181b", marginBottom: "16px" }} />

              {/* Three-column split table metadata */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
                <div style={{ flex: 1, textAlign: "center" }}>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "8px", color: "var(--muted-gray)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "4px" }}>DEPARTMENT</div>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "#ffffff", fontWeight: 600 }}>{result.student.department}</div>
                </div>
                
                <div style={{ width: "1px", height: "24px", backgroundColor: "#27272a" }} />
                
                <div style={{ flex: 1, textAlign: "center" }}>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "8px", color: "var(--muted-gray)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "4px" }}>YEAR</div>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "#ffffff", fontWeight: 600 }}>{result.student.year}</div>
                </div>
                
                <div style={{ width: "1px", height: "24px", backgroundColor: "#27272a" }} />
                
                <div style={{ flex: 1, textAlign: "center" }}>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "8px", color: "var(--muted-gray)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "4px" }}>STATUS</div>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "#10b981", fontWeight: 600 }}>{result.student.registration}</div>
                </div>
              </div>

              {/* Separator line */}
              <div style={{ width: "100%", height: "1px", backgroundColor: "#18181b", marginTop: "16px" }} />
            </div>
          )}

          {/* Redesigned Next Scan Button */}
          <div className="animate-slide-up delay-200" style={{ width: "100%" }}>
            <button
              onClick={onReset}
              className="scanner-action-btn"
              style={{
                position: "relative",
                width: "100%",
                height: "56px",
                backgroundColor: "transparent",
                border: "none",
                padding: "0 24px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
                boxSizing: "border-box",
                transition: "opacity 150ms ease",
              }}
            >
              {/* Left brackets */}
              <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: "6px" }}>
                <div style={{ position: "absolute", top: 0, left: 0, width: "6px", height: "6px", borderTop: "2px solid #fff", borderLeft: "2px solid #fff" }} />
                <div style={{ position: "absolute", bottom: 0, left: 0, width: "6px", height: "6px", borderBottom: "2px solid #fff", borderLeft: "2px solid #fff" }} />
              </div>
              
              <span
                style={{
                  fontFamily: "var(--font-sans)",
                  fontSize: "12px",
                  fontWeight: 600,
                  color: "#ffffff",
                  letterSpacing: "0.2em",
                  textTransform: "uppercase",
                }}
              >
                NEXT SCAN
              </span>
              
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
              
              {/* Right brackets */}
              <div style={{ position: "absolute", right: 0, top: 0, bottom: 0, width: "6px" }}>
                <div style={{ position: "absolute", top: 0, right: 0, width: "6px", height: "6px", borderTop: "2px solid #fff", borderRight: "2px solid #fff" }} />
                <div style={{ position: "absolute", bottom: 0, right: 0, width: "6px", height: "6px", borderBottom: "2px solid #fff", borderRight: "2px solid #fff" }} />
              </div>
            </button>
          </div>
        </div>
      )}

      {/* DECLINED Scan Result View (Redesigned from scratch) */}
      {result.state === "declined" && (
        <div className="animate-fade-in" style={{ width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
          {/* Centered Red Cross Box */}
          <div className="animate-slide-up" style={{ position: "relative", width: "80px", height: "80px", margin: "12px 0" }}>
            <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
              <div style={{ position: "absolute", top: 0, left: 0, width: "10px", height: "10px", borderTop: "2px solid #ef4444", borderLeft: "2px solid #ef4444" }} />
              <div style={{ position: "absolute", top: 0, right: 0, width: "10px", height: "10px", borderTop: "2px solid #ef4444", borderRight: "2px solid #ef4444" }} />
              <div style={{ position: "absolute", bottom: 0, left: 0, width: "10px", height: "10px", borderBottom: "2px solid #ef4444", borderLeft: "2px solid #ef4444" }} />
              <div style={{ position: "absolute", bottom: 0, right: 0, width: "10px", height: "10px", borderBottom: "2px solid #ef4444", borderRight: "2px solid #ef4444" }} />
            </div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "100%", height: "100%" }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </div>
          </div>

          {/* Access Denied Header */}
          <div className="animate-slide-up delay-100" style={{ textAlign: "center", width: "100%", marginBottom: "16px" }}>
            <h1
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "24px",
                fontWeight: 700,
                color: "#ef4444",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                margin: "0 0 8px 0",
                lineHeight: "1.2",
              }}
            >
              ACCESS
              <br />
              DENIED
            </h1>
            
            {/* Separator line */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", margin: "16px 0" }}>
              <div style={{ flex: 1, height: "1px", backgroundColor: "#ef444433" }} />
              <div style={{ width: "6px", height: "6px", backgroundColor: "#ef444488", margin: "0 10px" }} />
              <div style={{ flex: 1, height: "1px", backgroundColor: "#ef444433" }} />
            </div>

            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                color: "#ef4444",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
              }}
            >
              ENTRY COULD NOT BE VERIFIED
            </span>
          </div>

          {/* Reason Info Block */}
          <div className="animate-slide-up delay-200" style={{ textAlign: "center", width: "100%", marginBottom: "20px" }}>
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "9px",
                color: "var(--muted-gray)",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                marginBottom: "16px",
              }}
            >
              REASON
            </div>
            
            <h2
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "22px",
                fontWeight: 700,
                color: "#ef4444",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                margin: "0 0 12px 0",
              }}
            >
              {result.reason}
            </h2>
            
            <div
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "12px",
                color: "var(--muted-gray)",
                lineHeight: "1.6",
                maxWidth: "280px",
                margin: "0 auto",
              }}
            >
              {result.reason ? REASON_DESCRIPTIONS[result.reason] || "Verification failed." : "Verification failed."}
            </div>
          </div>

          {/* Redesigned Next Scan Button (Red themed) */}
          <div className="animate-slide-up delay-200" style={{ width: "100%" }}>
            <button
              onClick={onReset}
              className="scanner-action-btn"
              style={{
                position: "relative",
                width: "100%",
                height: "56px",
                backgroundColor: "transparent",
                border: "none",
                padding: "0 24px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
                boxSizing: "border-box",
                transition: "opacity 150ms ease",
              }}
            >
              {/* Left brackets */}
              <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: "6px" }}>
                <div style={{ position: "absolute", top: 0, left: 0, width: "6px", height: "6px", borderTop: "2px solid #ef4444", borderLeft: "2px solid #ef4444" }} />
                <div style={{ position: "absolute", bottom: 0, left: 0, width: "6px", height: "6px", borderBottom: "2px solid #ef4444", borderLeft: "2px solid #ef4444" }} />
              </div>
              
              <span
                style={{
                  fontFamily: "var(--font-sans)",
                  fontSize: "12px",
                  fontWeight: 600,
                  color: "#ef4444",
                  letterSpacing: "0.2em",
                  textTransform: "uppercase",
                }}
              >
                NEXT SCAN
              </span>
              
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
              
              {/* Right brackets */}
              <div style={{ position: "absolute", right: 0, top: 0, bottom: 0, width: "6px" }}>
                <div style={{ position: "absolute", top: 0, right: 0, width: "6px", height: "6px", borderTop: "2px solid #ef4444", borderRight: "2px solid #ef4444" }} />
                <div style={{ position: "absolute", bottom: 0, right: 0, width: "6px", height: "6px", borderBottom: "2px solid #ef4444", borderRight: "2px solid #ef4444" }} />
              </div>
            </button>
          </div>
        </div>
      )}

      {/* NETWORK / SERVICE ERROR View (Offline status, different from ACCESS DENIED) */}
      {result.state === "network_error" && (
        <div className="animate-fade-in" style={{ width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
          {/* Centered Warning Triangle Box */}
          <div className="animate-slide-up" style={{ position: "relative", width: "80px", height: "80px", margin: "24px 0" }}>
            <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
              <div style={{ position: "absolute", top: 0, left: 0, width: "10px", height: "10px", borderTop: "2px solid var(--muted-gray)", borderLeft: "2px solid var(--muted-gray)" }} />
              <div style={{ position: "absolute", top: 0, right: 0, width: "10px", height: "10px", borderTop: "2px solid var(--muted-gray)", borderRight: "2px solid var(--muted-gray)" }} />
              <div style={{ position: "absolute", bottom: 0, left: 0, width: "10px", height: "10px", borderBottom: "2px solid var(--muted-gray)", borderLeft: "2px solid var(--muted-gray)" }} />
              <div style={{ position: "absolute", bottom: 0, right: 0, width: "10px", height: "10px", borderBottom: "2px solid var(--muted-gray)", borderRight: "2px solid var(--muted-gray)" }} />
            </div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "100%", height: "100%" }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--muted-gray)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </div>
          </div>

          {/* Verification Unavailable Header */}
          <div className="animate-slide-up delay-100" style={{ textAlign: "center", width: "100%", marginBottom: "32px" }}>
            <h1
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "20px",
                fontWeight: 700,
                color: "#ffffff",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                margin: "0 0 8px 0",
                lineHeight: "1.3",
              }}
            >
              VERIFICATION
              <br />
              UNAVAILABLE
            </h1>
            
            {/* Separator line */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", margin: "16px 0" }}>
              <div style={{ flex: 1, height: "1px", backgroundColor: "#ffffff22" }} />
              <div style={{ width: "6px", height: "6px", backgroundColor: "var(--muted-gray)", margin: "0 10px" }} />
              <div style={{ flex: 1, height: "1px", backgroundColor: "#ffffff22" }} />
            </div>

            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                color: "var(--muted-gray)",
                letterSpacing: "0.2em",
                textTransform: "uppercase",
              }}
            >
              NETWORK ERROR
            </span>
          </div>

          {/* Error Description Block */}
          <div className="animate-slide-up delay-200" style={{ textAlign: "center", width: "100%", marginBottom: "40px" }}>
            <div
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "12px",
                color: "var(--muted-gray)",
                lineHeight: "1.6",
                maxWidth: "280px",
                margin: "0 auto",
              }}
            >
              The ticket could not be verified.
              <br />
              Please try again.
            </div>
          </div>

          {/* Retry Button */}
          <div className="animate-slide-up delay-200" style={{ width: "100%" }}>
            <button
              onClick={handleRetry}
              className="scanner-action-btn"
              style={{
                position: "relative",
                width: "100%",
                height: "56px",
                backgroundColor: "transparent",
                border: "none",
                padding: "0 24px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                cursor: "pointer",
                boxSizing: "border-box",
                transition: "opacity 150ms ease",
              }}
            >
              {/* Left brackets */}
              <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: "6px" }}>
                <div style={{ position: "absolute", top: 0, left: 0, width: "6px", height: "6px", borderTop: "2px solid #fff", borderLeft: "2px solid #fff" }} />
                <div style={{ position: "absolute", bottom: 0, left: 0, width: "6px", height: "6px", borderBottom: "2px solid #fff", borderLeft: "2px solid #fff" }} />
              </div>
              
              <span
                style={{
                  fontFamily: "var(--font-sans)",
                  fontSize: "12px",
                  fontWeight: 600,
                  color: "#ffffff",
                  letterSpacing: "0.2em",
                  textTransform: "uppercase",
                }}
              >
                RETRY
              </span>
              
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 4 23 10 17 10" />
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
              </svg>
              
              {/* Right brackets */}
              <div style={{ position: "absolute", right: 0, top: 0, bottom: 0, width: "6px" }}>
                <div style={{ position: "absolute", top: 0, right: 0, width: "6px", height: "6px", borderTop: "2px solid #fff", borderRight: "2px solid #fff" }} />
                <div style={{ position: "absolute", bottom: 0, right: 0, width: "6px", height: "6px", borderBottom: "2px solid #fff", borderRight: "2px solid #fff" }} />
              </div>
            </button>
          </div>
        </div>
      )}

      {/* Dynamic Instruction Footer Bar */}
      <div className="animate-slide-up delay-200" style={{ marginTop: "24px", textAlign: "center", width: "100%" }}>
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "8px",
            color: "var(--muted-gray)",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginBottom: "4px",
          }}
        >
          {shouldScan ? "ALIGN QR CODE WITHIN FRAME" : "VERIFICATION COMPLETE"}
        </div>
        
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "9px",
            color: "var(--fg-white)",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            display: "inline-block",
            borderLeft: "1px solid #3f3f46",
            borderRight: "1px solid #3f3f46",
            padding: "0 8px",
          }}
        >
          {shouldScan
            ? (result.state === "initializing" ? "INITIALIZING CAMERA" : "SCANNER READY")
            : "READY FOR OPERATOR ACTION"}
        </div>
      </div>
    </div>
  );
}
