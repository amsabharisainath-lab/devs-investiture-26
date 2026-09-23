import type { VerificationScan } from "./types";

export async function scanTicketQr(qrData: string): Promise<VerificationScan> {
  console.log("scanTicketQr API request sent with payload:", qrData);

  // Simulate minimal operational network latency
  await new Promise((resolve) => setTimeout(resolve, 600));

  // Standard simulation patterns for testing various backend decline/error states:
  if (qrData === "decline-expired") {
    throw new Error("Ticket expired");
  }
  if (qrData === "decline-scanned") {
    throw new Error("Already scanned");
  }
  if (qrData === "decline-invalid") {
    throw new Error("Invalid QR");
  }
  if (qrData === "decline-verification") {
    throw new Error("Verification failed");
  }
  if (qrData === "error-network") {
    throw new Error("Network offline");
  }

  // Clean placeholder success response
  return {
    id: `scan_${Math.random().toString(36).substring(2, 9)}`,
    studentName: "Alex Morgan",
    rollNo: "STU-TEST-001",
    department: "Computer Science",
    year: "III Year",
    registrationStatus: "Completed",
    status: "present",
    scannedAt: new Date().toISOString(),
  };
}
