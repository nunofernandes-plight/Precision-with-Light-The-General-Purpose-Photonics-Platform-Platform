
import { ArrowRight, Lightbulb, Cpu, Code } from "lucide-react";
import { Button } from "@/components/ui/button";

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-blue-300 rounded-full animate-pulse delay-1000"></div>
        <div className="absolute bottom-1/4 right-1/4 w-3 h-3 bg-blue-500 rounded-full animate-pulse delay-2000"></div>
        <div className="absolute bottom-1/3 left-1/3 w-1 h-1 bg-blue-200 rounded-full animate-pulse delay-500"></div>
      </div>
      
      <div className="container mx-auto px-6 text-center relative z-10">
        <div className="max-w-4xl mx-auto">
          {/* Main headline */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent animate-fade-in">
            Precision with Light
          </h1>
          
          {/* Subheadline */}
          <h2 className="text-xl md:text-2xl text-blue-200 mb-8 animate-fade-in">
            AI-Powered Photonics & Optoelectronics Solutions
          </h2>
          
          {/* Description */}
          <p className="text-lg md:text-xl text-slate-300 mb-12 max-w-3xl mx-auto leading-relaxed animate-fade-in">
            Transform your photonics platforms with cutting-edge AI-powered development, 
            custom Python-based scripts, and innovative optoelectronics solutions. 
            Partner with us to push the boundaries of light-based technology.
          </p>
          
          {/* Feature highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <div className="flex flex-col items-center p-6 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 hover:bg-white/15 transition-all duration-300 animate-fade-in">
              <Lightbulb className="w-12 h-12 text-blue-400 mb-4" />
              <h3 className="text-lg font-semibold mb-2">AI-Powered Design</h3>
              <p className="text-sm text-slate-300 text-center">Advanced algorithms for photonics system optimization</p>
            </div>
            
            <div className="flex flex-col items-center p-6 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 hover:bg-white/15 transition-all duration-300 animate-fade-in">
              <Code className="w-12 h-12 text-blue-400 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Python SDK Integration</h3>
              <p className="text-sm text-slate-300 text-center">Custom scripts for seamless platform integration</p>
            </div>
            
            <div className="flex flex-col items-center p-6 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 hover:bg-white/15 transition-all duration-300 animate-fade-in">
              <Cpu className="w-12 h-12 text-blue-400 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Proof of Concept</h3>
              <p className="text-sm text-slate-300 text-center">Rapid prototyping and validation services</p>
            </div>
          </div>
          
          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 text-lg">
              Explore Services
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button variant="outline" size="lg" className="border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-white px-8 py-4 text-lg">
              Partner with Us
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
