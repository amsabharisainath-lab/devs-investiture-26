import { useState, useRef } from "react";
import QRScanner from "../../features/attendance/components/QRScanner";
import type { ScannerResult } from "../../features/attendance/components/QRScanner";

const ERROR_REASONS = [
  "ALREADY SCANNED",
  "TICKET EXPIRED",
  "INVALID QR CODE",
  "TICKET NOT FOUND",
  "TICKET REVOKED",
  "REGISTRATION NOT FOUND",
  "EVENT ACCESS NOT PERMITTED",
];

export default function ScannerPage() {
  const [result, setResult] = useState<ScannerResult>({
    state: "initializing",
  });
  const [lastQrPayload, setLastQrPayload] = useState<string | null>(null);
  const [showErrorSelector, setShowErrorSelector] = useState(false);
  const [isDevModeExpanded, setIsDevModeExpanded] = useState(false);

  // Guard reference to block duplicate submissions during scan evaluation
  const isProcessingRef = useRef(false);

  const handleScan = (decodedText: string) => {
    if (isProcessingRef.current) {
      return;
    }
    isProcessingRef.current = true;
    setLastQrPayload(decodedText);
    setResult({ state: "detected" });
  };

  const handleReset = () => {
    isProcessingRef.current = false;
    setLastQrPayload(null);
    setShowErrorSelector(false);
    setResult({ state: "initializing" });
  };

  const handleCameraReady = () => {
    setResult({ state: "ready" });
  };

  const handleCameraError = (err: unknown) => {
    console.error("Camera initialization failed:", err);
    const errStr = String(err).toLowerCase();
    
    if (
      errStr.includes("permission") ||
      errStr.includes("notallowed") ||
      errStr.includes("denied")
    ) {
      setResult({ state: "camera_permission_denied" });
    } else {
      setResult({ state: "camera_error" });
    }
  };

  // Simulates an accepted ticket entry
  const triggerTestAccept = () => {
    isProcessingRef.current = true;
    setShowErrorSelector(false);
    setResult({
      state: "accepted",
      student: {
        name: "ALEX MORGAN",
        rollNo: "STU-TEST-001",
        department: "AI & DS",
        year: "2",
        registration: "VERIFIED",
      },
    });
  };

  // Triggers selection panel for simulation reasons
  const triggerTestErrorSelection = () => {
    setShowErrorSelector((prev) => !prev);
  };

  // Simulates a declined ticket entry with selected reason
  const triggerTestDecline = (reason: string) => {
    isProcessingRef.current = true;
    setShowErrorSelector(false);
    setResult({
      state: "declined",
      reason: reason,
    });
  };

  // Simulates a network offline error
  const triggerTestNetworkError = () => {
    isProcessingRef.current = true;
    setShowErrorSelector(false);
    setResult({
      state: "network_error",
      reason: "The ticket could not be verified. Please try again.",
    });
  };

  return (
    <div className="page-container" style={{ paddingBottom: "120px" }}>
      <QRScanner
        result={result}
        lastQrPayload={lastQrPayload}
        onScan={handleScan}
        onReset={handleReset}
        onCameraReady={handleCameraReady}
        onCameraError={handleCameraError}
      />

      {/* Collapsible Developer Tooling Panel */}
      <div
        style={{
          marginTop: "auto",
          width: "100%",
          maxWidth: "360px",
          border: "1px solid #18181b",
          backgroundColor: "#09090b",
          boxSizing: "border-box",
          position: "fixed",
          bottom: "96px", // Floats cleanly above the bottom navigation
          zIndex: 50,
        }}
      >
        <button
          onClick={() => setIsDevModeExpanded((prev) => !prev)}
          style={{
            width: "100%",
            height: "28px",
            backgroundColor: "#0c0c0e",
            border: "none",
            color: "var(--muted-gray)",
            fontFamily: "var(--font-mono)",
            fontSize: "8px",
            letterSpacing: "0.2em",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 12px",
          }}
        >
          <span>DEV MODE</span>
          <span>{isDevModeExpanded ? "▲ CLOSE" : "▼ OPEN"}</span>
        </button>

        {isDevModeExpanded && (
          <div style={{ padding: "12px", borderTop: "1px solid #18181b" }}>
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                onClick={triggerTestAccept}
                style={{
                  flex: 1,
                  height: "26px",
                  backgroundColor: "transparent",
                  border: "1px solid #27272a",
                  color: "#a1a1aa",
                  fontFamily: "var(--font-mono)",
                  fontSize: "9px",
                  letterSpacing: "0.1em",
                  cursor: "pointer",
                  textTransform: "uppercase",
                }}
              >
                ACCEPT
              </button>
              <button
                onClick={triggerTestErrorSelection}
                style={{
                  flex: 1,
                  height: "26px",
                  backgroundColor: showErrorSelector ? "#27272a" : "transparent",
                  border: "1px solid #27272a",
                  color: showErrorSelector ? "#ffffff" : "#a1a1aa",
                  fontFamily: "var(--font-mono)",
                  fontSize: "9px",
                  letterSpacing: "0.1em",
                  cursor: "pointer",
                  textTransform: "uppercase",
                }}
              >
                ERROR
              </button>
              <button
                onClick={triggerTestNetworkError}
                style={{
                  flex: 1,
                  height: "26px",
                  backgroundColor: "transparent",
                  border: "1px solid #27272a",
                  color: "#a1a1aa",
                  fontFamily: "var(--font-mono)",
                  fontSize: "9px",
                  letterSpacing: "0.1em",
                  cursor: "pointer",
                  textTransform: "uppercase",
                }}
              >
                OFFLINE
              </button>
            </div>

            {showErrorSelector && (
              <div
                style={{
                  marginTop: "8px",
                  display: "flex",
                  flexDirection: "column",
                  gap: "2px",
                  borderTop: "1px solid #18181b",
                  paddingTop: "8px",
                }}
              >
                {ERROR_REASONS.map((reason) => (
                  <button
                    key={reason}
                    onClick={() => triggerTestDecline(reason)}
                    style={{
                      height: "22px",
                      textAlign: "left",
                      backgroundColor: "transparent",
                      border: "none",
                      color: "#a1a1aa",
                      fontFamily: "var(--font-mono)",
                      fontSize: "9px",
                      letterSpacing: "0.05em",
                      cursor: "pointer",
                      padding: "2px 4px",
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.color = "#ffffff")}
                    onMouseLeave={(e) => (e.currentTarget.style.color = "#a1a1aa")}
                  >
                    {reason}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
