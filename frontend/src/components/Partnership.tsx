
import { Handshake, Globe, Rocket, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Partnership = () => {
  const benefits = [
    {
      icon: Handshake,
      title: "Strategic Collaboration",
      description: "Joint development initiatives that leverage both parties' strengths for innovative solutions."
    },
    {
      icon: Globe,
      title: "Global Reach",
      description: "Expand your market presence through our network of photonics industry connections."
    },
    {
      icon: Rocket,
      title: "Accelerated Innovation",
      description: "Fast-track your product development with our AI-powered tools and expertise."
    },
    {
      icon: Shield,
      title: "Risk Mitigation",
      description: "Reduce development risks through proven methodologies and thorough testing protocols."
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Partnership <span className="bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">Opportunities</span>
          </h2>
          <p className="text-xl text-blue-200 max-w-3xl mx-auto">
            Join forces with us to create groundbreaking photonics solutions. Together, we can push the boundaries of what's possible with light-based technology.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          {benefits.map((benefit, index) => (
            <Card key={index} className="bg-white/10 backdrop-blur-sm border-white/20 hover:bg-white/15 transition-all duration-300">
              <CardHeader className="flex flex-row items-center space-y-0 space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
                  <benefit.icon className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-white">{benefit.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-blue-200">{benefit.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4">Ready to Collaborate?</h3>
            <p className="text-blue-200 mb-8 max-w-2xl mx-auto">
              Whether you're looking to integrate our Python-based solutions into your SDK, 
              explore joint development opportunities, or discuss strategic partnerships, 
              we're here to help you succeed.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4">
                Schedule Consultation
              </Button>
              <Button variant="outline" size="lg" className="border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-white px-8 py-4">
                Download Partnership Guide
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Partnership;
