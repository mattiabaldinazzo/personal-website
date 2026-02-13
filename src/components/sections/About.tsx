import { motion } from "framer-motion";
import { GraduationCap, Code, TrendingUp, Lightbulb } from "lucide-react";
import avatarImage from "@/assets/avatar.webp";

const skills = [
  {
    icon: TrendingUp,
    title: "Sales & Marketing",
    description: "Strategie di vendita e marketing digitale",
  },
  {
    icon: Code,
    title: "Development",
    description: "Sviluppo siti web e applicazioni",
  },
  {
    icon: Lightbulb,
    title: "Open Source",
    description: "Contributi e progetti open source per la community",
  },
  {
    icon: GraduationCap,
    title: "AI & Innovation",
    description: "Intelligenza artificiale e nuove tecnologie",
  },
];

export const About = () => {
  return (
    <section id="about" className="section-padding bg-secondary/30">
      <div className="container-wide">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold text-foreground mb-4">
            Chi Sono
          </h2>
          <div className="w-16 h-1 bg-accent mx-auto rounded-full" />
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Image */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="relative order-2 lg:order-1"
          >
            <div className="relative aspect-[4/5] max-w-md mx-auto">
              <div className="absolute inset-0 bg-accent/10 rounded-3xl transform rotate-3" />
              <div className="absolute inset-0 bg-accent/5 rounded-3xl transform -rotate-2" />
              <div className="relative h-full rounded-2xl overflow-hidden shadow-xl">
                <img
                  src={avatarImage}
                  alt="Mattia Baldinazzo"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </motion.div>

          {/* Content */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="order-1 lg:order-2"
          >
            <h3 className="text-2xl md:text-3xl font-display font-semibold text-foreground mb-6">
              Ciao! Sono <span className="text-accent">Mattia Baldinazzo</span>
            </h3>
            <p className="text-muted-foreground leading-relaxed mb-6">
              Lavoro come Project & Process Manager in una multinazionale. Vengo dal mondo dello sviluppo 
              software e dell'informatica, ambiti che continuo a praticare con un approccio pratico e 
              orientato all'efficienza.
            </p>
            <p className="text-muted-foreground leading-relaxed mb-6">
              Mi appassionano l'intelligenza artificiale e l'open source, soprattutto quando diventano 
              strumenti concreti per migliorare processi, prodotti e organizzazione del lavoro. Mi interessa 
              capire come la tecnologia possa semplificare, automatizzare e rendere scalabili le attività reali.
            </p>
            <p className="text-muted-foreground leading-relaxed mb-8">
              I miei interessi sono trasversali e spaziano tra tecnologia, processi e sistemi digitali. 
              Se vuoi approfondire o confrontarti, contattami.
            </p>

            {/* Skills Grid */}
            <div className="grid grid-cols-2 gap-4">
              {skills.map((skill, index) => (
                <motion.div
                  key={skill.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                  className="p-4 rounded-xl bg-card border border-border shadow-sm hover:shadow-md hover:border-accent/30 transition-all duration-base group"
                >
                  <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-3 group-hover:bg-accent/20 transition-colors">
                    <skill.icon size={20} className="text-accent" />
                  </div>
                  <h4 className="font-semibold text-foreground text-sm mb-1">{skill.title}</h4>
                  <p className="text-xs text-muted-foreground">{skill.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
