export interface VerificationScan {
  id: string;
  studentName: string;
  rollNo: string;
  department: string;
  year: string;
  registrationStatus: string;
  status: "present" | "absent" | "forgery";
  scannedAt: string;
}
