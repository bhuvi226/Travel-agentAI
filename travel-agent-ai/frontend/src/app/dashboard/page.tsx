'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Chatbot } from '@/components/chatbot/Chatbot';
import { FiSearch, FiCalendar, FiMapPin, FiClock, FiDollarSign } from 'react-icons/fi';

type QuickAction = {
  id: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  bgColor: string;
  textColor: string;
  href: string;
};

type Trip = {
  id: number;
  destination: string;
  date: string;
  status: 'upcoming' | 'in-progress' | 'completed';
  image: string;
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [upcomingTrips, setUpcomingTrips] = useState<Trip[]>([]);

  useEffect(() => {
    // Simulate loading data
    setRecentSearches(['New York', 'Paris', 'Tokyo']);
    
    setUpcomingTrips([
      {
        id: 1,
        destination: 'Bali, Indonesia',
        date: 'Dec 15-25, 2023',
        status: 'upcoming',
        image: '/images/bali.jpg',
      },
      {
        id: 2,
        destination: 'Paris, France',
        date: 'Mar 1-10, 2024',
        status: 'upcoming',
        image: '/images/paris.jpg',
      },
    ]);
  }, []);

  const quickActions: QuickAction[] = [
    {
      id: 1,
      title: 'Search Flights',
      description: 'Find the best flight deals',
      icon: <FiSearch className="h-6 w-6" />,
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-700',
      href: '/dashboard/search/flights',
    },
    {
      id: 2,
      title: 'Book Hotels',
      description: 'Find the perfect stay',
      icon: <FiMapPin className="h-6 w-6" />,
      bgColor: 'bg-green-100',
      textColor: 'text-green-700',
      href: '/dashboard/search/hotels',
    },
    {
      id: 3,
      title: 'Plan Trip',
      description: 'Create a custom itinerary',
      icon: <FiCalendar className="h-6 w-6" />,
      bgColor: 'bg-purple-100',
      textColor: 'text-purple-700',
      href: '/dashboard/planner',
    },
  ];

  const getStatusBadge = (status: string) => {
    const statusClasses = {
      upcoming: 'bg-yellow-100 text-yellow-800',
      'in-progress': 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
    };

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {status.replace('-', ' ')}
      </span>
    );
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.full_name?.split(' ')[0] || 'Traveler'}! ✈️
        </h1>
        <p className="mt-1 text-gray-600">
          Where would you like to go next? Your next adventure awaits!
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {quickActions.map((action) => (
          <a
            key={action.id}
            href={action.href}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className={`flex-shrink-0 rounded-md p-3 ${action.bgColor} ${action.textColor}`}>
                  {action.icon}
                </div>
                <div className="ml-5">
                  <h3 className="text-lg font-medium text-gray-900">{action.title}</h3>
                  <p className="mt-1 text-sm text-gray-500">{action.description}</p>
                </div>
              </div>
            </div>
          </a>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Trips */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-5 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Upcoming Trips</h3>
          </div>
          <div className="bg-white overflow-hidden">
            {upcomingTrips.length > 0 ? (
              <ul className="divide-y divide-gray-200">
                {upcomingTrips.map((trip) => (
                  <li key={trip.id} className="p-6 hover:bg-gray-50">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-16 w-16 rounded-md overflow-hidden">
                        <img
                          className="h-full w-full object-cover"
                          src={trip.image}
                          alt={trip.destination}
                        />
                      </div>
                      <div className="ml-4 flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium text-gray-900">{trip.destination}</h4>
                          {getStatusBadge(trip.status)}
                        </div>
                        <div className="mt-1 flex items-center text-sm text-gray-500">
                          <FiCalendar className="flex-shrink-0 mr-1.5 h-4 w-4" />
                          <span>{trip.date}</span>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="p-6 text-center">
                <p className="text-gray-500">No upcoming trips. Start planning your next adventure!</p>
                <a
                  href="/dashboard/planner"
                  className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Plan a Trip
                </a>
              </div>
            )}
          </div>
        </div>

        {/* Recent Searches */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-5 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Searches</h3>
          </div>
          <div className="p-6">
            {recentSearches.length > 0 ? (
              <div className="space-y-4">
                {recentSearches.map((search, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-md hover:bg-gray-100"
                  >
                    <div className="flex items-center">
                      <FiSearch className="h-5 w-5 text-gray-400" />
                      <span className="ml-3 text-gray-900">{search}</span>
                    </div>
                    <button
                      type="button"
                      className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                    >
                      Search again
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FiSearch className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No recent searches</h3>
                <p className="mt-1 text-sm text-gray-500">Start searching for your next destination.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chatbot */}
      <Chatbot />
    </div>
  );
}
