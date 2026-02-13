import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ExternalLink } from "lucide-react";

export type ProjectCategory = "tutti" | "personali" | "lavorativi" | "universitari";

export const categoryLabels: Record<ProjectCategory, string> = {
  tutti: "Tutti",
  personali: "Personali",
  lavorativi: "Lavorativi",
  universitari: "Universitari",
};

const projects = [
  {
    company: "Spotify",
    description: "Analisi touchpoint, metriche e KPI",
    image: "https://mattiabaldinazzo.it/images/works/spotify.webp",
    link: "https://github.com/mattiabaldinazzo/spotify-analysis",
    category: "universitari" as ProjectCategory,
  },
  {
    company: "Ferrarelle S.p.A.",
    description: "Piano di marketing quinquennale",
    image: "https://mattiabaldinazzo.it/images/works/ferrarelle.webp",
    link: "https://github.com/mattiabaldinazzo/ferrarelle-marketing",
    category: "universitari" as ProjectCategory,
  },
  {
    company: "Edison S.p.A.",
    description: "Piano di marketing",
    image: "https://mattiabaldinazzo.it/images/works/edison.webp",
    link: "https://github.com/mattiabaldinazzo/edison-marketing",
    category: "universitari" as ProjectCategory,
  },
  {
    company: "Italgas Bludigit S.p.A.",
    description: "Data analysis, soluzioni innovative per smart working",
    image: "https://mattiabaldinazzo.it/images/works/italgas.webp",
    link: "https://github.com/mattiabaldinazzo/italgas-analysis",
    category: "universitari" as ProjectCategory,
  },
  {
    company: "High Quality Food",
    description: "Analisi brand, piano di marketing e comunicazione",
    image: "https://mattiabaldinazzo.it/images/works/hqf.webp",
    link: "https://github.com/mattiabaldinazzo/hqf-marketing",
    category: "universitari" as ProjectCategory,
  },
  {
    company: "TIM",
    description: "Brief per la campagna Super Fibra TIM",
    image: "https://mattiabaldinazzo.it/images/works/tim.webp",
    link: "https://github.com/mattiabaldinazzo/tim-campaign",
    category: "universitari" as ProjectCategory,
  },
  {
    company: "Toyota Motor Italia S.p.A.",
    description: "Modifica business model da product-based a platform-based",
    image: "https://mattiabaldinazzo.it/images/works/toyota.webp",
    link: "https://github.com/mattiabaldinazzo/toyota-business-model",
    category: "universitari" as ProjectCategory,
  },
  {
    company: "24bottles S.r.l.",
    description: "Creazione brief marketing team",
    image: "https://mattiabaldinazzo.it/images/works/24bottles.webp",
    link: "https://github.com/mattiabaldinazzo/24bottles-brief",
    category: "universitari" as ProjectCategory,
  },
  {
    company: "Woolrich Europe S.p.A.",
    description: "Digital Marketing Media Plan FW22",
    image: "https://mattiabaldinazzo.it/images/works/woolrich.webp",
    link: "https://github.com/mattiabaldinazzo/woolrich-media-plan",
    category: "universitari" as ProjectCategory,
  },
];

const categories: ProjectCategory[] = ["tutti", "personali", "lavorativi", "universitari"];

export const Projects = () => {
  const [activeCategory, setActiveCategory] = useState<ProjectCategory>("tutti");

  useEffect(() => {
    const handler = (e: Event) => {
      const category = (e as CustomEvent).detail as ProjectCategory;
      setActiveCategory(category);
    };
    window.addEventListener("filter-projects", handler);
    return () => window.removeEventListener("filter-projects", handler);
  }, []);

  const filteredProjects = activeCategory === "tutti"
    ? projects
    : projects.filter((p) => p.category === activeCategory);

  return (
    <section id="projects" className="section-padding">
      <div className="container-wide">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold text-foreground mb-4">
            Progetti
          </h2>
          <div className="w-16 h-1 bg-accent mx-auto rounded-full mb-6" />
          <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
            Una raccolta dei miei ultimi lavori. Puoi trovare la lista completa su{" "}
            <a
              href="https://github.com/mattiabaldinazzo/works"
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent hover:underline"
            >
              GitHub
            </a>
            .
          </p>

          {/* Category Filter Tabs */}
          <div className="flex items-center justify-center gap-2 flex-wrap">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-base ${
                  activeCategory === cat
                    ? "bg-accent text-accent-foreground shadow-md"
                    : "bg-secondary text-muted-foreground hover:text-foreground hover:bg-secondary/80"
                }`}
              >
                {categoryLabels[cat]}
              </button>
            ))}
          </div>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project, index) => (
            <motion.a
              key={project.company}
              href={project.link}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="group relative overflow-hidden rounded-2xl bg-card border border-border shadow-sm hover:shadow-lg transition-all duration-base block"
            >
              {/* Image */}
              <div className="aspect-[16/10] overflow-hidden">
                <img
                  src={project.image}
                  alt={project.company}
                  className="w-full h-full object-cover transition-transform duration-slow group-hover:scale-105"
                />
              </div>

              {/* Overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-foreground/90 via-foreground/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-base flex items-end">
                <div className="p-6 text-primary-foreground">
                  <div className="flex items-center gap-2 mb-2">
                    <ExternalLink size={16} className="text-accent" />
                    <span className="text-xs font-medium text-accent uppercase tracking-wider">View Project</span>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="p-5">
                <h3 className="font-display font-semibold text-lg text-foreground mb-2 group-hover:text-accent transition-colors">
                  {project.company}
                </h3>
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {project.description}
                </p>
              </div>
            </motion.a>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-center mt-12"
        >
          <a
            href="https://www.linkedin.com/in/mattiabaldinazzo"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm font-medium text-accent hover:underline"
          >
            Maggiori informazioni sulla mia pagina LinkedIn
            <ExternalLink size={16} />
          </a>
        </motion.div>
      </div>
    </section>
  );
};
