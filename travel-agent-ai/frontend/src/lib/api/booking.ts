import { apiClient } from './client';

export interface TravelDetails {
  origin: string;
  destination: string;
  departure_date: string;
  return_date?: string;
  adults: number;
  children?: number;
  travel_class?: string;
  flight_number?: string;
  train_number?: string;
  // Add more fields as needed
}

export interface PassengerInfo {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  passport_number?: string;
  nationality?: string;
  seat_preference?: string;
  meal_preference?: string;
  special_requests?: string;
}

export interface BookingRequest {
  travel_type: 'flight' | 'train' | 'hotel' | 'package';
  travel_details: TravelDetails;
  passengers: PassengerInfo[];
  contact_info: {
    email: string;
    phone: string;
  };
  payment_method: {
    type: string;
    token: string;
  };
}

export interface BookingResponse {
  id: number;
  reference: string;
  status: string;
  travel_type: string;
  travel_details: TravelDetails;
  amount: number;
  currency: string;
  payment_status: string;
  created_at: string;
  updated_at: string;
  passengers: PassengerInfo[];
}

export const bookingService = {
  // Create a new booking
  async createBooking(bookingData: BookingRequest): Promise<BookingResponse> {
    return await apiClient.post<BookingResponse>('/bookings', bookingData);
  },

  // Get booking by ID
  async getBooking(bookingId: number): Promise<BookingResponse> {
    return await apiClient.get<BookingResponse>(`/bookings/${bookingId}`);
  },

  // List all bookings for the current user
  async listBookings(params?: {
    status?: string;
    travel_type?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    limit?: number;
  }): Promise<{ data: BookingResponse[]; total: number }> {
    return await apiClient.get<{ data: BookingResponse[]; total: number }>('/bookings', { params });
  },

  // Cancel a booking
  async cancelBooking(bookingId: number): Promise<BookingResponse> {
    return await apiClient.post<BookingResponse>(`/bookings/${bookingId}/cancel`);
  },

  // Search for travel options
  async searchFlights(params: {
    origin: string;
    destination: string;
    departure_date: string;
    return_date?: string;
    adults: number;
    children?: number;
    travel_class?: string;
  }) {
    return await apiClient.post('/agents/search', {
      query: 'search_flights',
      context: params,
    });
  },

  async searchTrains(params: {
    origin: string;
    destination: string;
    date: string;
    class?: string;
  }) {
    return await apiClient.post('/agents/search', {
      query: 'search_trains',
      context: params,
    });
  },
};
