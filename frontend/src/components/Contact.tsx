
import { Mail, Phone, MapPin, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState } from "react";

const Contact = () => {
  const [selectedService, setSelectedService] = useState<string>("");

  return (
    <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            Get in <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">Touch</span>
          </h2>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Ready to transform your photonics platform? Let's discuss how we can help you achieve your goals.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Contact Information */}
          <div className="space-y-8">
            <Card className="border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-2xl text-slate-900">Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
                    <Mail className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Email</h3>
                    <p className="text-slate-600">info@precisionwithlight.com</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
                    <Phone className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Phone</h3>
                    <p className="text-slate-600">+1 (555) 123-4567</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
                    <MapPin className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Location</h3>
                    <p className="text-slate-600">San Francisco, CA</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <div className="bg-gradient-to-br from-blue-600 to-cyan-500 rounded-2xl p-8 text-white">
              <h3 className="text-2xl font-bold mb-4">Why Choose Us?</h3>
              <ul className="space-y-3">
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-white rounded-full mr-3"></div>
                  Expert team with 10+ years in photonics
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-white rounded-full mr-3"></div>
                  AI-powered solutions for optimal performance
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-white rounded-full mr-3"></div>
                  Seamless Python SDK integration
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-white rounded-full mr-3"></div>
                  24/7 technical support
                </li>
              </ul>
            </div>
          </div>

          {/* Contact Form */}
          <Card className="border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl text-slate-900">Send us a Message</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Name</label>
                    <Input placeholder="Your name" className="border-slate-300 focus:border-blue-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Company</label>
                    <Input placeholder="Your company" className="border-slate-300 focus:border-blue-500" />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                  <Input type="email" placeholder="your.email@company.com" className="border-slate-300 focus:border-blue-500" />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Service Interest</label>
                  <Select value={selectedService} onValueChange={setSelectedService}>
                    <SelectTrigger className="border-slate-300 focus:border-blue-500">
                      <SelectValue placeholder="Select a service" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="mpw-coordination">MPW Run Coordination</SelectItem>
                      <SelectItem value="python-pdk">Python PDK Development</SelectItem>
                      <SelectItem value="wafer-allocation">Wafer Space Allocation</SelectItem>
                      <SelectItem value="design-verification">Design Verification</SelectItem>
                      <SelectItem value="process-integration">Process Integration</SelectItem>
                      <SelectItem value="characterization">Characterization Support</SelectItem>
                      <SelectItem value="collaboration">Collaboration Platform</SelectItem>
                      <SelectItem value="general">General Inquiry</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {selectedService === "python-pdk" && (
                  <div className="space-y-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h4 className="font-semibold text-blue-900">Python PDK Requirements</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Target Process Node</label>
                        <Input placeholder="e.g., 220nm SOI" className="border-slate-300 focus:border-blue-500" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Foundry</label>
                        <Input placeholder="e.g., AIM Photonics" className="border-slate-300 focus:border-blue-500" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">Required Components</label>
                      <Textarea 
                        placeholder="Please specify required photonic components (e.g., waveguides, modulators, detectors, etc.)"
                        className="border-slate-300 focus:border-blue-500 min-h-[80px]"
                      />
                    </div>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Subject</label>
                  <Input 
                    placeholder={selectedService === "python-pdk" ? "Python PDK Development Request" : "How can we help you?"} 
                    className="border-slate-300 focus:border-blue-500" 
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Message</label>
                  <Textarea 
                    placeholder={
                      selectedService === "python-pdk" 
                        ? "Please describe your Python PDK requirements, timeline, and any specific technical needs..."
                        : "Tell us about your project requirements..."
                    }
                    className="border-slate-300 focus:border-blue-500 min-h-[120px]"
                  />
                </div>
                
                <Button className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white py-3">
                  <Send className="w-5 h-5 mr-2" />
                  Send Message
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default Contact;
