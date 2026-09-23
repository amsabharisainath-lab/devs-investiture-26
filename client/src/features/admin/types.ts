export interface OperationalMetrics {
  registeredCount: number;
  presentCount: number;
  absentCount: number;
  forgeryCount: number;
  enteredCount: number;
  exitedCount: number;
  unresolvedExceptionsCount: number;
}

export interface ExceptionLog {
  id: string;
  studentName: string;
  rollNo: string;
  exceptionType: "invalid_qr" | "duplicate_scan" | "forgery";
  timestamp: string;
  resolved: boolean;
}
