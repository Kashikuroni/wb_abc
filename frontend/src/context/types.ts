export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  avatar?: string;
  workspaces_member?: Workspace[];
  workspaces_owned?: Workspace[];
}

export interface Workspace {
  id: number;
  title: string;
  description: string;
  stores: Store[];
}

export interface Store {
  id: number;
  title: string;
  seller_id: number;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  refreshUser: () => Promise<void>;
  clearAuth: () => Promise<void>;
}
