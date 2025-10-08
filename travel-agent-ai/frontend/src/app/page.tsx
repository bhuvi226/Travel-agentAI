import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Plan Your Perfect Trip with AI
        </h1>
        <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
          Discover amazing destinations, find the best deals, and create unforgettable memories with our AI-powered travel assistant.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Button size="lg" className="px-8 py-6 text-lg">
            <Link href="/auth/register">Get Started</Link>
          </Button>
          <Button variant="outline" size="lg" className="px-8 py-6 text-lg">
            <Link href="/auth/login">Sign In</Link>
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Why Choose Us?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'AI-Powered Search',
                description: 'Our advanced AI finds the best travel options tailored to your preferences.',
                icon: '🔍',
              },
              {
                title: 'Best Prices',
                description: 'Get the best deals on flights, hotels, and packages all in one place.',
                icon: '💰',
              },
              {
                title: '24/7 Support',
                description: 'Our team is always ready to assist you with your travel needs.',
                icon: '🛟',
              },
            ].map((feature, index) => (
              <div 
                key={index}
                className="p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 border border-gray-100"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Explore?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join thousands of travelers who trust us with their adventures.
          </p>
          <Button 
            variant="secondary" 
            size="lg" 
            className="px-8 py-6 text-lg text-blue-600"
          >
            <Link href="/auth/register">Start Planning Now</Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
