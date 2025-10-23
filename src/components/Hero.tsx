import { Shield, Mail, Image, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import heroImage from "@/assets/hero-guardian.jpg";

interface HeroProps {
  onNavigate: (section: 'email' | 'deepfake') => void;
}

const Hero = ({ onNavigate }: HeroProps) => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div 
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `url(${heroImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-background/95 via-background/90 to-background/95" />
      </div>

      {/* Animated Glow Effect */}
      <div className="absolute inset-0 z-0 opacity-30">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/20 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
      </div>

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          {/* Icon */}
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-primary to-secondary shadow-lg">
            <Shield className="w-10 h-10 text-primary-foreground" />
          </div>

          {/* Heading */}
          <div className="space-y-4">
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
              <span className="text-gradient">AI Guardian</span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto">
              Your digital companion that cares about your safety
            </p>
          </div>

          {/* Description */}
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            In today's world, even truth wears a mask. Detect phishing emails and AI-generated deepfakes 
            with instant, AI-powered analysis that explains why something feels off.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Button 
              size="lg" 
              variant="hero"
              onClick={() => onNavigate('email')}
              className="group"
            >
              <Mail className="w-5 h-5" />
              Analyze Email
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              onClick={() => onNavigate('deepfake')}
              className="group border-primary/50 hover:border-primary"
            >
              <Image className="w-5 h-5" />
              Detect Deepfake
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 pt-12">
            <div className="card-gradient rounded-xl p-6 space-y-3 border border-border/50">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Mail className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-semibold text-lg">Email Protection</h3>
              <p className="text-sm text-muted-foreground">
                Detect suspicious patterns, malicious links, and phishing attempts with AI-powered analysis
              </p>
            </div>

            <div className="card-gradient rounded-xl p-6 space-y-3 border border-border/50">
              <div className="w-12 h-12 rounded-lg bg-secondary/10 flex items-center justify-center">
                <Image className="w-6 h-6 text-secondary" />
              </div>
              <h3 className="font-semibold text-lg">Deepfake Detection</h3>
              <p className="text-sm text-muted-foreground">
                Identify AI-generated images and manipulated media with advanced visual analysis
              </p>
            </div>

            <div className="card-gradient rounded-xl p-6 space-y-3 border border-border/50">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <Shield className="w-6 h-6 text-accent" />
              </div>
              <h3 className="font-semibold text-lg">Clear Explanations</h3>
              <p className="text-sm text-muted-foreground">
                Get detailed insights and confidence scores with human-friendly explanations
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;