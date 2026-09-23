export type UserRole = "ADMIN" | "SUPER_ADMIN";

export interface SessionUser {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  is_active: boolean;
}

export function useAdminAuth(): {
  user: SessionUser | null;
  role: UserRole;
  isAuthenticated: boolean;
  isLoading: boolean;
} {
  // Statically configure the mock role payload.
  // Toggle this value between "ADMIN" and "SUPER_ADMIN" to test role-aware rendering.
  const activeRole: UserRole = "SUPER_ADMIN";

  return {
    user: {
      id: 1,
      email: "test.admin@example.com",
      name: "Test Admin",
      role: activeRole,
      is_active: true,
    },
    role: activeRole,
    isAuthenticated: true,
    isLoading: false,
  };
}

