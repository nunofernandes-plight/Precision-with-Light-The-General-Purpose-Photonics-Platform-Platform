
import { Cpu, Layers, Zap, Target, Users, Microscope, Code, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const Services = () => {
  const services = [
    {
      icon: Cpu,
      title: "MPW Run Coordination",
      description: "Complete management of Multi-Project Wafer runs, from design submission to fabrication delivery.",
      features: ["Design rule compliance", "Layout optimization", "Timeline coordination", "Python PDK integration"]
    },
    {
      icon: Code,
      title: "Python PDK Development",
      description: "Software-focused Process Design Kit for photonics designs with digital twin integration potential.",
      features: ["Standard cell libraries", "Process design rules", "Simulation models", "Layout verification"],
      isHighlighted: true
    },
    {
      icon: Layers,
      title: "Wafer Space Allocation",
      description: "Efficient allocation and optimization of wafer real estate for multiple photonics projects.",
      features: ["Space optimization", "Cost-effective sharing", "Layout planning"]
    },
    {
      icon: Target,
      title: "Design Verification",
      description: "Comprehensive design rule checking and verification services for MPW submissions.",
      features: ["DRC validation", "Process compatibility", "Design optimization"]
    },
    {
      icon: Zap,
      title: "Process Integration",
      description: "Expert guidance on process flows and integration strategies for photonics devices.",
      features: ["Process selection", "Integration planning", "Yield optimization"]
    },
    {
      icon: Microscope,
      title: "Characterization Support",
      description: "Post-fabrication testing and characterization services for MPW participants.",
      features: ["Device testing", "Performance analysis", "Data reporting"]
    },
    {
      icon: Users,
      title: "Collaboration Platform",
      description: "Facilitating partnerships and collaborations between MPW participants and foundries.",
      features: ["Partner matching", "Resource sharing", "Joint development"]
    }
  ];

  const scrollToContact = () => {
    const contactSection = document.getElementById('contact');
    if (contactSection) {
      contactSection.scrollIntoView({ behavior: 'smooth' });
      // Pre-select Python PDK in the contact form
      setTimeout(() => {
        const serviceSelect = document.querySelector('[data-service-selector]') as HTMLElement;
        if (serviceSelect) {
          serviceSelect.click();
        }
      }, 500);
    }
  };

  return (
    <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            MPW <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">Services</span>
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Comprehensive Multi-Project Wafer run services for photonics and optoelectronics development
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <Card key={index} className={`group hover:shadow-xl transition-all duration-300 border-0 bg-white/80 backdrop-blur-sm hover:bg-white hover:scale-105 ${service.isHighlighted ? 'ring-2 ring-blue-500/20' : ''}`}>
              <CardHeader className="text-center pb-4">
                <div className={`w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-300 ${service.isHighlighted ? 'ring-2 ring-blue-400/30' : ''}`}>
                  <service.icon className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-xl font-bold text-slate-900">{service.title}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-slate-600 mb-6">{service.description}</p>
                <ul className="space-y-2 mb-6">
                  {service.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center text-sm text-slate-700">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-3 flex-shrink-0"></div>
                      {feature}
                    </li>
                  ))}
                </ul>
                {service.isHighlighted && (
                  <Button 
                    onClick={scrollToContact}
                    className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white"
                  >
                    Request PDK Access
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Services;
