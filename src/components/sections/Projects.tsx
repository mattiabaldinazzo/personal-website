import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ExternalLink, X } from "lucide-react";

export type ProjectCategory = "tutti" | "personali" | "lavorativi" | "universitari";

export const categoryLabels: Record<ProjectCategory, string> = {
  tutti: "Tutti",
  personali: "Personali",
  lavorativi: "Lavorativi",
  universitari: "Universitari",
};

type ProjectLink = {
  company: string;
  subtitle?: string;
  description: string;
  image: string;
  category: ProjectCategory;
  link: string;
  modal?: never;
};

type ProjectModal = {
  company: string;
  subtitle?: string;
  description: string;
  image: string;
  category: ProjectCategory;
  link?: never;
  modal: {
    title: string;
    content: string;
  };
};

type Project = ProjectLink | ProjectModal;

const projects: Project[] = [
  {
    company: "iliad Space",
    description:
      "Partecipazione allo sviluppo e gestione del canale di vendita iliad Space.",
    image: "/iliadspace.webp",
    category: "lavorativi",
    modal: {
      title: "iliad Space",
      content: `Iliad Space è il canale di distribuzione retail che consente di attivare e gestire le offerte Iliad attraverso una rete di negozi di telefonia sul territorio, con l'obiettivo di ampliare la presenza fisica dell'operatore e migliorare l'accessibilità per gli utenti.

Ho collaborato allo sviluppo iniziale del progetto e al lancio del canale, contribuendo alla definizione del modello operativo e alla realizzazione del portale a supporto della rete di vendita.

Negli ultimi tre anni ho ricoperto il ruolo di Sales Project, Process & Support Leader, con responsabilità su evoluzione, stabilità e scalabilità del canale. In questo contesto ho coordinato un team di 10 persone, composto da:

- 4 risorse dedicate al project management
- 6 risorse dedicate alle CC Operations

Le principali aree di responsabilità includono:

- sviluppo e miglioramento continuo del portale e delle componenti software
- implementazione di nuove funzionalità e ottimizzazione dei processi operativi
- coordinamento del supporto operativo e amministrativo alla rete
- gestione delle attività necessarie a garantire efficienza, qualità del servizio e crescita del canale`,
    },
  },
  {
    company: "Spotify",
    description: "Analisi touchpoint, metriche e KPI",
    image: "/spotify.webp",
    link: "https://github.com/mattiabaldinazzo/works/tree/main/spotify",
    category: "universitari",
  },
  {
    company: "Ferrarelle S.p.A.",
    description: "Piano di marketing quinquennale",
    image: "/ferrarelle.webp",
    link: "https://github.com/mattiabaldinazzo/works/tree/main/ferrarelle",
    category: "universitari",
  },
  {
    company: "Edison S.p.A.",
    description: "Piano di marketing",
    image: "/edison.webp",
    link: "https://github.com/mattiabaldinazzo/works/tree/main/edison",
    category: "universitari",
  },
  {
    company: "Italgas Bludigit S.p.A.",
    description: "Data analysis, soluzioni innovative per smart working",
    image: "/italgas.webp",
    link: "https://github.com/mattiabaldinazzo/works/tree/main/italgas_bludigit",
    category: "universitari",
  },
  {
    company: "High Quality Food",
    description: "Analisi brand, piano di marketing e comunicazione",
    image: "/hqf.webp",
    link: "https://github.com/mattiabaldinazzo/works/tree/main/hqf",
    category: "universitari",
  },
  {
    company: "TIM",
    description: "Brief per la campagna Super Fibra TIM",
    image: "/tim.webp",
    link: "https://github.com/mattiabaldinazzo/works/tree/main/tim",
    category: "universitari",
  },
  {
    company: "Toyota Motor Italia S.p.A.",
    description: "Modifica business model da product-based a platform-based",
    image: "/toyota.webp",
    link: "https://github.com/mattiabaldinazzo/works/tree/main/toyota",
    category: "universitari",
  },
  {
    company: "24bottles S.r.l.",
    description: "Creazione brief marketing team",
    image: "/24bottles.webp",
    link: "https://github.com/mattiabaldinazzo/works/tree/main/24bottles",
    category: "universitari",
  },
  {
    company: "Woolrich Europe S.p.A.",
    description: "Digital Marketing Media Plan FW22",
    image: "/woolrich.webp",
    link: "https://github.com/mattiabaldinazzo/works/tree/main/woolrich",
    category: "universitari",
  },
];

const categories: ProjectCategory[] = ["tutti", "personali", "lavorativi", "universitari"];

function renderModalContent(content: string) {
  return content.split("\n").map((line, i) => {
    if (line.startsWith("- ")) {
      return (
        <li key={i} className="ml-4 list-disc text-foreground/80">
          {line.slice(2)}
        </li>
      );
    }
    if (line.trim() === "") {
      return <div key={i} className="h-3" />;
    }
    return (
      <p key={i} className="text-foreground/80 leading-relaxed">
        {line}
      </p>
    );
  });
}

export const Projects = () => {
  const [activeCategory, setActiveCategory] = useState<ProjectCategory>("tutti");
  const [openModal, setOpenModal] = useState<ProjectModal["modal"] | null>(null);

  useEffect(() => {
    const handler = (e: Event) => {
      const category = (e as CustomEvent).detail as ProjectCategory;
      setActiveCategory(category);
    };
    window.addEventListener("filter-projects", handler);
    return () => window.removeEventListener("filter-projects", handler);
  }, []);

  useEffect(() => {
    if (openModal) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [openModal]);

  const filteredProjects =
    activeCategory === "tutti"
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
          {filteredProjects.map((project, index) => {
            const isModal = !!project.modal;

            const cardContent = (
              <>
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
                      <span className="text-xs font-medium text-accent uppercase tracking-wider">
                        {isModal ? "Scopri di più" : "View Project"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="p-5">
                  <h3 className="font-display font-semibold text-lg text-foreground mb-1 group-hover:text-accent transition-colors">
                    {project.company}
                  </h3>
                  {project.subtitle && (
                    <p className="text-xs font-medium text-accent uppercase tracking-wide mb-2">
                      {project.subtitle}
                    </p>
                  )}
                  <p className="text-sm text-muted-foreground line-clamp-3">
                    {project.description}
                  </p>
                </div>
              </>
            );

            if (isModal) {
              return (
                <motion.button
                  key={project.company}
                  onClick={() => setOpenModal(project.modal!)}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="group relative overflow-hidden rounded-2xl bg-card border border-border shadow-sm hover:shadow-lg transition-all duration-base text-left w-full"
                >
                  {cardContent}
                </motion.button>
              );
            }

            return (
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
                {cardContent}
              </motion.a>
            );
          })}
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

      {/* Modal */}
      {openModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          onClick={() => setOpenModal(null)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
            className="relative bg-card border border-border rounded-2xl shadow-2xl overflow-hidden flex flex-col"
            style={{ width: "80vw", maxWidth: "900px", height: "80vh" }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-8 py-6 border-b border-border shrink-0">
              <h2 className="font-display font-bold text-2xl text-foreground">
                {openModal.title}
              </h2>
              <button
                onClick={() => setOpenModal(null)}
                className="rounded-full p-2 hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
                aria-label="Chiudi"
              >
                <X size={20} />
              </button>
            </div>

            {/* Scrollable content */}
            <div className="overflow-y-auto flex-1 px-8 py-6 space-y-1">
              {renderModalContent(openModal.content)}
            </div>
          </motion.div>
        </div>
      )}
    </section>
  );
};
