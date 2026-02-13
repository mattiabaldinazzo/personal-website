import { motion } from "framer-motion";
import { Mail, Calendar, Linkedin, Github, Instagram, ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";

const socialLinks = [
  { icon: Linkedin, href: "https://www.linkedin.com/in/mattiabaldinazzo", label: "LinkedIn" },
  { icon: Github, href: "https://github.com/mattiabaldinazzo", label: "GitHub" },
  { icon: Instagram, href: "https://instagram.com/mattiabaldinazzo", label: "Instagram" },
];

export const Contact = () => {
  return (
    <section id="contact" className="section-padding">
      <div className="container-narrow">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold text-foreground mb-4">
            Contatti
          </h2>
          <div className="w-16 h-1 bg-accent mx-auto rounded-full mb-6" />
          <p className="text-muted-foreground max-w-xl mx-auto mb-12">
            Potete contattarmi via mail o tramite i vari canali social. Sono sempre aperto a nuove opportunità e collaborazioni.
          </p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-12 max-w-lg mx-auto"
          >
            <Button variant="hero" size="lg" className="w-full" asChild>
              <a href="mailto:mattia.baldinazzo@gmail.com">
                <Mail size={18} />
                Inviami una mail
              </a>
            </Button>
            <Button variant="hero" size="lg" className="w-full" asChild>
              <a href="https://cal.com/mattiabaldinazzo" target="_blank" rel="noopener noreferrer">
                <Calendar size={18} />
                Prenota appuntamento
              </a>
            </Button>
          </motion.div>

          {/* Social Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="flex items-center justify-center gap-4"
          >
            {socialLinks.map((social) => (
              <a
                key={social.label}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                className="p-4 rounded-full border border-border bg-card hover:border-accent hover:text-accent transition-all duration-base shadow-sm hover:shadow-md"
                aria-label={social.label}
              >
                <social.icon size={22} />
              </a>
            ))}
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};
