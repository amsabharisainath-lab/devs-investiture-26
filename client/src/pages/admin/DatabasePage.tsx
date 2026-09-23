import { useState, useMemo } from "react";
import { useAdminAuth } from "../../features/admin/hooks/useAdminAuth";

export interface RegistryRecord {
  id: string;
  name: string;
  rollNo: string;
  email: string;
  department: string;
  year: string;
  ticketCode: string;
  status: "VERIFIED" | "ACTIVE" | "PENDING" | "INACTIVE" | "SUSPENDED";
  timestamp: string;
  timeFormatted: string;
  gate?: string;
  history?: Array<{
    time: string;
    event: string;
  }>;
}

const INITIAL_RECORDS: RegistryRecord[] = [
  {
    id: "rec_001",
    name: "ALEX MORGAN",
    rollNo: "STU-TEST-001",
    email: "alex.morgan@example.com",
    department: "AI & DS",
    year: "YEAR 02",
    ticketCode: "DEV-TEST-101",
    status: "VERIFIED",
    timestamp: "2026-09-21T20:41:08Z",
    timeFormatted: "20:41",
    gate: "GATE 01 - MAIN",
    history: [
      { time: "20:41:08", event: "Entry verified at Gate 01" },
      { time: "19:15:00", event: "Ticket issued" },
    ],
  },
  {
    id: "rec_002",
    name: "JORDAN LEE",
    rollNo: "STU-TEST-002",
    email: "jordan.lee@example.com",
    department: "CSE",
    year: "YEAR 03",
    ticketCode: "DEV-TEST-102",
    status: "VERIFIED",
    timestamp: "2026-09-21T20:39:22Z",
    timeFormatted: "20:39",
    gate: "GATE 01 - MAIN",
    history: [
      { time: "20:39:22", event: "Entry verified at Gate 01" },
      { time: "18:40:11", event: "QR credential generated" },
    ],
  },
  {
    id: "rec_003",
    name: "TAYLOR CHEN",
    rollNo: "STU-TEST-003",
    email: "taylor.chen@example.com",
    department: "ECE",
    year: "YEAR 02",
    ticketCode: "DEV-TEST-103",
    status: "PENDING",
    timestamp: "2026-09-21T20:15:40Z",
    timeFormatted: "20:15",
    history: [
      { time: "20:15:40", event: "Registration logged - awaiting check-in" },
    ],
  },
  {
    id: "rec_004",
    name: "SAM CARTER",
    rollNo: "STU-TEST-004",
    email: "sam.carter@example.com",
    department: "IT",
    year: "YEAR 04",
    ticketCode: "DEV-TEST-104",
    status: "ACTIVE",
    timestamp: "2026-09-21T19:50:18Z",
    timeFormatted: "19:50",
    history: [
      { time: "19:50:18", event: "Invitation confirmed" },
    ],
  },
  {
    id: "rec_005",
    name: "PRIYA NAIR",
    rollNo: "STU-TEST-005",
    email: "priya.nair@example.com",
    department: "AI & DS",
    year: "YEAR 01",
    ticketCode: "DEV-TEST-105",
    status: "VERIFIED",
    timestamp: "2026-09-21T19:42:05Z",
    timeFormatted: "19:42",
    gate: "GATE 02 - NORTH",
    history: [
      { time: "19:42:05", event: "Entry verified at Gate 02" },
      { time: "17:30:00", event: "Pass issued" },
    ],
  },
  {
    id: "rec_006",
    name: "DANIEL BROOKS",
    rollNo: "STU-TEST-006",
    email: "daniel.brooks@example.com",
    department: "MECH",
    year: "YEAR 03",
    ticketCode: "DEV-TEST-106",
    status: "INACTIVE",
    timestamp: "2026-09-21T18:30:19Z",
    timeFormatted: "18:30",
    history: [
      { time: "18:30:19", event: "Ticket dormant" },
    ],
  },
  {
    id: "rec_007",
    name: "MORGAN REED",
    rollNo: "STU-TEST-007",
    email: "morgan.reed@example.com",
    department: "CSE",
    year: "YEAR 02",
    ticketCode: "DEV-TEST-107",
    status: "VERIFIED",
    timestamp: "2026-09-21T18:14:50Z",
    timeFormatted: "18:14",
    gate: "GATE 01 - MAIN",
    history: [
      { time: "18:14:50", event: "Entry verified at Gate 01" },
    ],
  },
  {
    id: "rec_008",
    name: "CASEY PATEL",
    rollNo: "STU-TEST-008",
    email: "casey.patel@example.com",
    department: "EEE",
    year: "YEAR 04",
    ticketCode: "DEV-TEST-108",
    status: "SUSPENDED",
    timestamp: "2026-09-21T17:55:00Z",
    timeFormatted: "17:55",
    history: [
      { time: "17:55:00", event: "Credential suspended by administrator" },
    ],
  },
  {
    id: "rec_009",
    name: "JAMIE VANCE",
    rollNo: "STU-TEST-009",
    email: "jamie.vance@example.com",
    department: "AI & DS",
    year: "YEAR 03",
    ticketCode: "DEV-TEST-109",
    status: "ACTIVE",
    timestamp: "2026-09-21T17:20:15Z",
    timeFormatted: "17:20",
    history: [
      { time: "17:20:15", event: "Pass issued - standby" },
    ],
  },
  {
    id: "rec_010",
    name: "RILEY AVERY",
    rollNo: "STU-TEST-010",
    email: "riley.avery@example.com",
    department: "IT",
    year: "YEAR 02",
    ticketCode: "DEV-TEST-110",
    status: "VERIFIED",
    timestamp: "2026-09-21T16:45:30Z",
    timeFormatted: "16:45",
    gate: "GATE 01 - MAIN",
    history: [
      { time: "16:45:30", event: "Entry verified at Gate 01" },
    ],
  },
];

type FilterType = "ALL" | "VERIFIED" | "ACTIVE" | "PENDING" | "INACTIVE" | "SUSPENDED";
type SortType = "RECENT" | "NAME" | "ROLL";

export default function DatabasePage() {
  const { role } = useAdminAuth();
  const isSuperAdmin = role === "SUPER_ADMIN";

  const [records, setRecords] = useState<RegistryRecord[]>(INITIAL_RECORDS);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState<FilterType>("ALL");
  const [activeSort, setActiveSort] = useState<SortType>("RECENT");
  const [selectedRecordId, setSelectedRecordId] = useState<string | null>(null);

  const [isAddingRecord, setIsAddingRecord] = useState(false);
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);
  const [newName, setNewName] = useState("");
  const [newRollNo, setNewRollNo] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newDepartment, setNewDepartment] = useState("AI & DS");
  const [newYear, setNewYear] = useState("YEAR 02");

  // Selected Record Object
  const selectedRecord = useMemo(() => {
    return records.find((r) => r.id === selectedRecordId) || null;
  }, [records, selectedRecordId]);

  // Filtered and Sorted Records
  const filteredRecords = useMemo(() => {
    return records
      .filter((rec) => {
        // Status filter
        if (activeFilter !== "ALL" && rec.status !== activeFilter) {
          return false;
        }
        // Search query across name, rollNo, email, department, ticketCode
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase().trim();
          const matchName = rec.name.toLowerCase().includes(q);
          const matchRoll = rec.rollNo.toLowerCase().includes(q);
          const matchEmail = rec.email.toLowerCase().includes(q);
          const matchDept = rec.department.toLowerCase().includes(q);
          const matchTicket = rec.ticketCode.toLowerCase().includes(q);
          return matchName || matchRoll || matchEmail || matchDept || matchTicket;
        }
        return true;
      })
      .sort((a, b) => {
        if (activeSort === "NAME") {
          return a.name.localeCompare(b.name);
        }
        if (activeSort === "ROLL") {
          return a.rollNo.localeCompare(b.rollNo);
        }
        // RECENT: latest timestamp first
        return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
      });
  }, [records, searchQuery, activeFilter, activeSort]);

  // Delete handler for Super Admin
  const handleDeleteRecord = (id: string) => {
    setRecords((prev) => prev.filter((r) => r.id !== id));
    setSelectedRecordId(null);
    setIsConfirmingDelete(false);
  };

  // Status toggle handler for Super Admin
  const handleUpdateStatus = (id: string, newStatus: RegistryRecord["status"]) => {
    setRecords((prev) =>
      prev.map((r) => {
        if (r.id === id) {
          const updatedHistory = [
            {
              time: new Date().toTimeString().slice(0, 8),
              event: `Status updated to ${newStatus}`,
            },
            ...(r.history || []),
          ];
          return { ...r, status: newStatus, history: updatedHistory };
        }
        return r;
      })
    );
  };

  // Add Record Submission
  const handleCreateRecord = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newRollNo.trim()) return;

    const newRecord: RegistryRecord = {
      id: `rec_${Date.now().toString().slice(-4)}`,
      name: newName.trim().toUpperCase(),
      rollNo: newRollNo.trim(),
      email: newEmail.trim().toLowerCase() || `${newRollNo.trim().toLowerCase()}@example.com`,
      department: newDepartment.toUpperCase(),
      year: newYear,
      ticketCode: `DEV-TEST-${Math.floor(100 + Math.random() * 900)}`,
      status: "ACTIVE",
      timestamp: new Date().toISOString(),
      timeFormatted: new Date().toTimeString().slice(0, 5),
      history: [
        {
          time: new Date().toTimeString().slice(0, 8),
          event: "Record added by administrator",
        },
      ],
    };

    setRecords((prev) => [newRecord, ...prev]);
    setNewName("");
    setNewRollNo("");
    setNewEmail("");
    setIsAddingRecord(false);
  };

  // Status styling definition
  const getStatusBadgeStyle = (status: RegistryRecord["status"]) => {
    switch (status) {
      case "VERIFIED":
        return { color: "#ffffff", borderColor: "#3f3f46", bg: "#18181b" };
      case "ACTIVE":
        return { color: "#e4e4e7", borderColor: "#27272a", bg: "transparent" };
      case "PENDING":
        return { color: "#a1a1aa", borderColor: "#27272a", bg: "transparent" };
      case "INACTIVE":
        return { color: "#71717a", borderColor: "#27272a", bg: "transparent" };
      case "SUSPENDED":
        return { color: "#ef4444", borderColor: "#7f1d1d", bg: "transparent" };
      default:
        return { color: "#a1a1aa", borderColor: "#27272a", bg: "transparent" };
    }
  };

  // --------------------------------------------------------------------------
  // RECORD DETAIL VIEW (When a record is tapped)
  // --------------------------------------------------------------------------
  if (selectedRecord) {
    const statusStyle = getStatusBadgeStyle(selectedRecord.status);

    return (
      <div className="page-container" style={{ textAlign: "left", alignItems: "stretch" }}>
        {/* Back navigation button */}
        <button
          onClick={() => setSelectedRecordId(null)}
          style={{
            background: "transparent",
            border: "none",
            color: "var(--muted-gray)",
            fontFamily: "var(--font-mono)",
            fontSize: "11px",
            letterSpacing: "0.08em",
            cursor: "pointer",
            padding: "0 0 24px 0",
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            transition: "color 150ms ease",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = "#ffffff")}
          onMouseLeave={(e) => (e.currentTarget.style.color = "var(--muted-gray)")}
        >
          <span>←</span>
          <span>Back to Database</span>
        </button>

        {/* Identity Header */}
        <div style={{ marginBottom: "28px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              gap: "12px",
              marginBottom: "8px",
            }}
          >
            <h1
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "24px",
                fontWeight: 700,
                color: "#ffffff",
                letterSpacing: "0.02em",
                margin: 0,
                lineHeight: "1.2",
              }}
            >
              {selectedRecord.name}
            </h1>

            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                fontWeight: 600,
                color: statusStyle.color,
                border: `1px solid ${statusStyle.borderColor}`,
                background: statusStyle.bg,
                padding: "3px 8px",
                letterSpacing: "0.08em",
                flexShrink: 0,
              }}
            >
              {selectedRecord.status}
            </span>
          </div>

          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "12px",
              color: "var(--muted-gray)",
              letterSpacing: "0.05em",
            }}
          >
            {selectedRecord.rollNo} · {selectedRecord.department} · {selectedRecord.year}
          </div>
        </div>

        {/* Separator line */}
        <div style={{ width: "100%", height: "1px", backgroundColor: "var(--border-dark)", marginBottom: "24px" }} />

        {/* Metadata Grid */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px", marginBottom: "28px" }}>
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "9px",
              color: "var(--muted-gray)",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
            }}
          >
            REGISTRATION DETAILS
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--muted-gray)", marginBottom: "4px" }}>
                ROLL NUMBER
              </div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "13px", color: "#ffffff", fontWeight: 600 }}>
                {selectedRecord.rollNo}
              </div>
            </div>

            <div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--muted-gray)", marginBottom: "4px" }}>
                TICKET CODE
              </div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "13px", color: "#ffffff", fontWeight: 600 }}>
                {selectedRecord.ticketCode}
              </div>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--muted-gray)", marginBottom: "4px" }}>
                EMAIL
              </div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "#d4d4d8", wordBreak: "break-all" }}>
                {selectedRecord.email}
              </div>
            </div>

            <div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--muted-gray)", marginBottom: "4px" }}>
                DEPARTMENT & YEAR
              </div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "#ffffff" }}>
                {selectedRecord.department} ({selectedRecord.year})
              </div>
            </div>
          </div>

          {selectedRecord.gate && (
            <div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--muted-gray)", marginBottom: "4px" }}>
                ASSIGNED GATE
              </div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "#ffffff" }}>
                {selectedRecord.gate}
              </div>
            </div>
          )}
        </div>

        {/* Event History */}
        {selectedRecord.history && selectedRecord.history.length > 0 && (
          <div style={{ marginBottom: "32px" }}>
            <div
              style={{
                width: "100%",
                height: "1px",
                backgroundColor: "var(--border-dark)",
                marginBottom: "20px",
              }}
            />

            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "9px",
                color: "var(--muted-gray)",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                marginBottom: "12px",
              }}
            >
              ACTIVITY LOG
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {selectedRecord.history.map((h, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "12px",
                    fontFamily: "var(--font-mono)",
                    fontSize: "11px",
                    paddingLeft: "10px",
                    borderLeft: "1px solid #27272a",
                  }}
                >
                  <span style={{ color: "var(--muted-gray)", flexShrink: 0 }}>{h.time}</span>
                  <span style={{ color: "#d4d4d8" }}>{h.event}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SUPER ADMIN CONTROLS */}
        {isSuperAdmin && (
          <div style={{ marginTop: "auto", paddingTop: "12px" }}>
            <div
              style={{
                width: "100%",
                height: "1px",
                backgroundColor: "var(--border-dark)",
                marginBottom: "20px",
              }}
            />

            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "9px",
                color: "var(--muted-gray)",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                marginBottom: "12px",
              }}
            >
              ADMINISTRATOR ACTIONS
            </div>

            {/* Status switcher row */}
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "16px" }}>
              {(["VERIFIED", "ACTIVE", "PENDING", "INACTIVE", "SUSPENDED"] as const).map((st) => (
                <button
                  key={st}
                  onClick={() => handleUpdateStatus(selectedRecord.id, st)}
                  style={{
                    background: selectedRecord.status === st ? "#27272a" : "transparent",
                    border: "1px solid #27272a",
                    color: selectedRecord.status === st ? "#ffffff" : "var(--muted-gray)",
                    fontFamily: "var(--font-mono)",
                    fontSize: "9px",
                    letterSpacing: "0.08em",
                    padding: "6px 10px",
                    cursor: "pointer",
                    transition: "all 150ms ease",
                  }}
                >
                  Set {st}
                </button>
              ))}
            </div>

            {/* Delete Confirmation */}
            {isConfirmingDelete ? (
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  onClick={() => handleDeleteRecord(selectedRecord.id)}
                  style={{
                    flex: 1,
                    height: "38px",
                    background: "none",
                    border: "1px solid #ef4444",
                    color: "#ef4444",
                    fontFamily: "var(--font-mono)",
                    fontSize: "10px",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                    cursor: "pointer",
                  }}
                >
                  Confirm Delete Record
                </button>
                <button
                  onClick={() => setIsConfirmingDelete(false)}
                  style={{
                    height: "38px",
                    padding: "0 16px",
                    background: "none",
                    border: "1px solid var(--border-dark)",
                    color: "var(--muted-gray)",
                    fontFamily: "var(--font-mono)",
                    fontSize: "10px",
                    letterSpacing: "0.08em",
                    cursor: "pointer",
                  }}
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsConfirmingDelete(true)}
                style={{
                  width: "100%",
                  height: "38px",
                  background: "transparent",
                  border: "1px solid var(--border-dark)",
                  color: "var(--muted-gray)",
                  fontFamily: "var(--font-mono)",
                  fontSize: "10px",
                  letterSpacing: "0.08em",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "color 150ms ease, border-color 150ms ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = "#ef4444";
                  e.currentTarget.style.borderColor = "#ef4444";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = "var(--muted-gray)";
                  e.currentTarget.style.borderColor = "var(--border-dark)";
                }}
              >
                Delete Record
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  // --------------------------------------------------------------------------
  // PRIMARY REGISTRY VIEW
  // --------------------------------------------------------------------------
  const filterOptions: FilterType[] = ["ALL", "VERIFIED", "ACTIVE", "PENDING", "INACTIVE", "SUSPENDED"];
  const isFiltered = activeFilter !== "ALL" || searchQuery.trim() !== "";

  return (
    <div className="page-container" style={{ textAlign: "left", alignItems: "stretch" }}>
      {/* Page Title & Stats */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "20px" }}>
        <div>
          <h1
            style={{
              fontFamily: "var(--font-sans)",
              fontSize: "24px",
              fontWeight: 700,
              color: "#ffffff",
              letterSpacing: "0.04em",
              textTransform: "uppercase",
              margin: "0 0 4px 0",
            }}
          >
            Database
          </h1>
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              color: "var(--muted-gray)",
              letterSpacing: "0.05em",
            }}
          >
            Attendee and registration directory
          </div>
        </div>

        <div style={{ textAlign: "right" }}>
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "14px",
              fontWeight: 700,
              color: "#ffffff",
              letterSpacing: "0.05em",
            }}
          >
            {records.length}
          </div>
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "9px",
              color: "var(--muted-gray)",
              letterSpacing: "0.05em",
              textTransform: "uppercase",
            }}
          >
            Total
          </div>
        </div>
      </div>

      {/* Super Admin Insert Record Action */}
      {isSuperAdmin && !isAddingRecord && (
        <div style={{ marginBottom: "16px" }}>
          <button
            onClick={() => setIsAddingRecord(true)}
            style={{
              width: "100%",
              height: "36px",
              background: "#09090b",
              border: "1px dashed var(--border-dark)",
              color: "#d4d4d8",
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              letterSpacing: "0.08em",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "6px",
              transition: "border-color 150ms ease, color 150ms ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "#3f3f46";
              e.currentTarget.style.color = "#ffffff";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "var(--border-dark)";
              e.currentTarget.style.color = "#d4d4d8";
            }}
          >
            <span>+</span>
            <span>Add New Record</span>
          </button>
        </div>
      )}

      {/* Super Admin Inline Record Creation Form */}
      {isSuperAdmin && isAddingRecord && (
        <form
          onSubmit={handleCreateRecord}
          style={{
            border: "1px solid var(--border-dark)",
            backgroundColor: "#09090b",
            padding: "16px",
            marginBottom: "20px",
          }}
        >
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "9px",
              color: "var(--muted-gray)",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              marginBottom: "12px",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <span>NEW RECORD ENTRY</span>
            <button
              type="button"
              onClick={() => setIsAddingRecord(false)}
              style={{
                background: "none",
                border: "none",
                color: "var(--muted-gray)",
                cursor: "pointer",
                fontFamily: "var(--font-mono)",
                fontSize: "9px",
              }}
            >
              Cancel
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "14px" }}>
            <input
              type="text"
              placeholder="Full Name (e.g. Alex Morgan)"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              required
              style={{
                height: "36px",
                backgroundColor: "#000000",
                border: "1px solid var(--border-dark)",
                color: "#ffffff",
                padding: "0 10px",
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                outline: "none",
              }}
            />

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
              <input
                type="text"
                placeholder="Roll Number (STU-TEST-001)"
                value={newRollNo}
                onChange={(e) => setNewRollNo(e.target.value)}
                required
                style={{
                  height: "36px",
                  backgroundColor: "#000000",
                  border: "1px solid var(--border-dark)",
                  color: "#ffffff",
                  padding: "0 10px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  outline: "none",
                }}
              />

              <input
                type="text"
                placeholder="Department (AI & DS)"
                value={newDepartment}
                onChange={(e) => setNewDepartment(e.target.value)}
                required
                style={{
                  height: "36px",
                  backgroundColor: "#000000",
                  border: "1px solid var(--border-dark)",
                  color: "#ffffff",
                  padding: "0 10px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  outline: "none",
                }}
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
              <input
                type="email"
                placeholder="Email Address (Optional)"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                style={{
                  height: "36px",
                  backgroundColor: "#000000",
                  border: "1px solid var(--border-dark)",
                  color: "#ffffff",
                  padding: "0 10px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  outline: "none",
                }}
              />

              <select
                value={newYear}
                onChange={(e) => setNewYear(e.target.value)}
                style={{
                  height: "36px",
                  backgroundColor: "#000000",
                  border: "1px solid var(--border-dark)",
                  color: "#ffffff",
                  padding: "0 8px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  outline: "none",
                }}
              >
                <option value="YEAR 01">Year 01</option>
                <option value="YEAR 02">Year 02</option>
                <option value="YEAR 03">Year 03</option>
                <option value="YEAR 04">Year 04</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="scanner-btn"
            style={{ width: "100%", height: "36px", fontSize: "10px", letterSpacing: "0.1em" }}
          >
            SAVE RECORD
          </button>
        </form>
      )}

      {/* 1. PRIMARY SEARCH INPUT */}
      <div style={{ position: "relative", marginBottom: "12px" }}>
        <input
          type="text"
          placeholder="Search by name, roll number, or department..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: "100%",
            height: "42px",
            backgroundColor: "#09090b",
            border: "1px solid var(--border-dark)",
            color: "#ffffff",
            padding: "0 36px 0 14px",
            fontFamily: "var(--font-mono)",
            fontSize: "11px",
            letterSpacing: "0.02em",
            outline: "none",
            boxSizing: "border-box",
            transition: "border-color 150ms ease",
          }}
          onFocus={(e) => (e.currentTarget.style.borderColor = "#3f3f46")}
          onBlur={(e) => (e.currentTarget.style.borderColor = "var(--border-dark)")}
        />

        {searchQuery && (
          <button
            onClick={() => setSearchQuery("")}
            style={{
              position: "absolute",
              right: "12px",
              top: "50%",
              transform: "translateY(-50%)",
              background: "none",
              border: "none",
              color: "var(--muted-gray)",
              fontFamily: "var(--font-mono)",
              fontSize: "14px",
              cursor: "pointer",
              padding: "4px",
            }}
          >
            ×
          </button>
        )}
      </div>

      {/* 2. UNIFIED SEGMENTED FILTER BAR */}
      <div
        style={{
          display: "flex",
          border: "1px solid var(--border-dark)",
          backgroundColor: "#09090b",
          marginBottom: "12px",
          width: "100%",
          boxSizing: "border-box",
          overflowX: "auto",
          scrollbarWidth: "none",
        }}
      >
        {filterOptions.map((filter, idx) => {
          const isActive = activeFilter === filter;
          const isLast = idx === filterOptions.length - 1;
          return (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              style={{
                flex: "1 0 auto",
                minWidth: "52px",
                height: "32px",
                background: isActive ? "#ffffff" : "transparent",
                border: "none",
                borderRight: isLast ? "none" : "1px solid var(--border-dark)",
                color: isActive ? "#000000" : "var(--muted-gray)",
                fontFamily: "var(--font-mono)",
                fontSize: "9px",
                fontWeight: isActive ? 700 : 500,
                letterSpacing: "0.06em",
                cursor: "pointer",
                textTransform: "uppercase",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "0 8px",
                whiteSpace: "nowrap",
                transition: "all 120ms ease",
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.color = "#ffffff";
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.color = "var(--muted-gray)";
              }}
            >
              {filter}
            </button>
          );
        })}
      </div>

      {/* 3. SUB-TOOLBAR: Matched Count & Aligned Sort */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "6px 0 10px",
          borderBottom: "1px solid var(--border-dark)",
          marginBottom: "4px",
          width: "100%",
        }}
      >
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            color: "var(--muted-gray)",
            letterSpacing: "0.06em",
          }}
        >
          {isFiltered ? (
            <span>
              <strong style={{ color: "#ffffff" }}>{filteredRecords.length}</strong> of {records.length} matching
            </span>
          ) : (
            <span>
              <strong style={{ color: "#ffffff" }}>{records.length}</strong> records
            </span>
          )}
        </div>

        {/* Sort Control */}
        <button
          onClick={() => {
            if (activeSort === "RECENT") setActiveSort("NAME");
            else if (activeSort === "NAME") setActiveSort("ROLL");
            else setActiveSort("RECENT");
          }}
          style={{
            background: "transparent",
            border: "1px solid var(--border-dark)",
            color: "var(--muted-gray)",
            fontFamily: "var(--font-mono)",
            fontSize: "9.5px",
            letterSpacing: "0.06em",
            padding: "4px 8px",
            cursor: "pointer",
            textTransform: "uppercase",
            display: "flex",
            alignItems: "center",
            gap: "5px",
            transition: "border-color 150ms ease, color 150ms ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "#3f3f46";
            e.currentTarget.style.color = "#ffffff";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--border-dark)";
            e.currentTarget.style.color = "var(--muted-gray)";
          }}
        >
          <span>Sort:</span>
          <span style={{ color: "#ffffff", fontWeight: 600 }}>{activeSort}</span>
          <span style={{ fontSize: "8px" }}>▾</span>
        </button>
      </div>

      {/* 4. REGISTRY LIST */}
      {filteredRecords.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column" }}>
          {filteredRecords.map((rec, index) => {
            const indexStr = (index + 1).toString().padStart(2, "0");
            const statusStyle = getStatusBadgeStyle(rec.status);

            return (
              <div
                key={rec.id}
                onClick={() => setSelectedRecordId(rec.id)}
                style={{
                  padding: "14px 0",
                  borderBottom: "1px solid var(--border-dark)",
                  cursor: "pointer",
                  transition: "opacity 150ms ease",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.75")}
                onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
              >
                {/* Name and Status Header */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: "12px",
                    marginBottom: "4px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "baseline", gap: "8px" }}>
                    <span
                      style={{
                        fontFamily: "var(--font-mono)",
                        fontSize: "10px",
                        color: "var(--muted-gray)",
                      }}
                    >
                      {indexStr}
                    </span>
                    <span
                      style={{
                        fontFamily: "var(--font-sans)",
                        fontSize: "14px",
                        fontWeight: 700,
                        color: "#ffffff",
                        letterSpacing: "0.02em",
                      }}
                    >
                      {rec.name}
                    </span>
                  </div>

                  <span
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: "9px",
                      fontWeight: 600,
                      color: statusStyle.color,
                      border: `1px solid ${statusStyle.borderColor}`,
                      background: statusStyle.bg,
                      padding: "2px 6px",
                      letterSpacing: "0.08em",
                      flexShrink: 0,
                    }}
                  >
                    {rec.status}
                  </span>
                </div>

                {/* Subtitle Details */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    fontFamily: "var(--font-mono)",
                    fontSize: "10.5px",
                    color: "var(--muted-gray)",
                    paddingLeft: "22px",
                  }}
                >
                  <span>
                    {rec.rollNo} · {rec.department}
                  </span>
                  <span style={{ fontSize: "9.5px" }}>{rec.timeFormatted}</span>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Empty State */
        <div style={{ textAlign: "center", padding: "48px 16px" }}>
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              color: "#ffffff",
              letterSpacing: "0.08em",
              marginBottom: "6px",
            }}
          >
            No records found
          </div>
          <div
            style={{
              fontFamily: "var(--font-sans)",
              fontSize: "12px",
              color: "var(--muted-gray)",
              marginBottom: "16px",
            }}
          >
            Try changing the filter or search keywords
          </div>
          <button
            onClick={() => {
              setSearchQuery("");
              setActiveFilter("ALL");
            }}
            style={{
              background: "transparent",
              border: "1px solid var(--border-dark)",
              color: "#ffffff",
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              letterSpacing: "0.08em",
              padding: "6px 14px",
              cursor: "pointer",
            }}
          >
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
}

