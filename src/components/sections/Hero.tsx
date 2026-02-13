import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ArrowDown, Github, Linkedin, Instagram, Facebook, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";

const roles = ["Project & Process Manager", "Developer", "AI Enthusiast"];

export const Hero = () => {
  const [currentRole, setCurrentRole] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentRole((prev) => (prev + 1) % roles.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const socialLinks = [
    { icon: Linkedin, href: "https://www.linkedin.com/in/mattiabaldinazzo", label: "LinkedIn" },
    { icon: Github, href: "https://github.com/mattiabaldinazzo", label: "GitHub" },
    { icon: Instagram, href: "https://instagram.com/mattiabaldinazzo", label: "Instagram" },
    { icon: Facebook, href: "https://facebook.com/mattiabaldinazzo", label: "Facebook" },
  ];

  return (
    <section id="home" className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/4 w-[800px] h-[800px] rounded-full bg-accent/5 blur-3xl" />
        <div className="absolute -bottom-1/2 -left-1/4 w-[600px] h-[600px] rounded-full bg-accent/5 blur-3xl" />
      </div>

      <div className="container-wide relative z-10">
        <div className="flex flex-col items-center text-center pt-20 md:pt-0">

          {/* Greeting */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-muted-foreground text-lg md:text-xl mb-4"
          >
            Ciao, sono
          </motion.p>

          {/* Name */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="text-4xl md:text-6xl lg:text-7xl font-display font-bold text-foreground mb-6"
          >
            Mattia Baldinazzo
          </motion.h1>

          {/* Role Switcher */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="h-10 md:h-12 mb-8 overflow-hidden"
          >
            <motion.p
              key={currentRole}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              transition={{ duration: 0.4 }}
              className="text-xl md:text-2xl lg:text-3xl text-accent font-medium"
            >
              {roles[currentRole]}
            </motion.p>
          </motion.div>

          {/* Social Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="flex items-center gap-4 mb-10"
          >
            {socialLinks.map((social) => (
              <a
                key={social.label}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 rounded-full border border-border bg-card hover:border-accent hover:text-accent transition-all duration-base shadow-sm hover:shadow-md"
                aria-label={social.label}
              >
                <social.icon size={20} />
              </a>
            ))}
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl"
          >
            <Button variant="hero" size="lg" className="w-full" asChild>
              <a href="#contact">
                <Mail size={18} />
                Contattami
              </a>
            </Button>
            <Button variant="heroOutline" size="lg" className="w-full" asChild>
              <a href="mailto:mattia.baldinazzo@gmail.com?subject=Richiesta%20CV">
                Richiedi il mio CV
              </a>
            </Button>
            <Button variant="heroOutline" size="lg" className="w-full" asChild>
              <a href="https://cal.com/mattiabaldinazzo" target="_blank" rel="noopener noreferrer">
                Prenota appuntamento
              </a>
            </Button>
          </motion.div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 0.6 }}
        className="hidden md:block absolute bottom-4 left-1/2 -translate-x-1/2"
      >
        <motion.a
          href="#about"
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="flex flex-col items-center gap-2 text-muted-foreground hover:text-accent transition-colors"
        >
          <span className="text-xs font-medium tracking-wider uppercase">Scopri di più</span>
          <ArrowDown size={20} />
        </motion.a>
      </motion.div>
    </section>
  );
};
