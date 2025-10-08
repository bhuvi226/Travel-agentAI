export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  // Add any additional user fields as needed
}

export interface UserProfile extends User {
  // Add any additional profile-specific fields here
  phone_number?: string;
  address?: string;
  // Add more fields as needed
}
