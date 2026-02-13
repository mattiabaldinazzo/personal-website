import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";

import { categoryLabels, type ProjectCategory } from "@/components/sections/Projects";

const navItems = [
  { label: "Home", href: "#home" },
  { label: "Chi Sono", href: "#about" },
  {
    label: "Progetti",
    href: "#projects",
    subItems: [
      { label: "Personali", category: "personali" as ProjectCategory },
      { label: "Lavorativi", category: "lavorativi" as ProjectCategory },
      { label: "Universitari", category: "universitari" as ProjectCategory },
    ],
  },
  { label: "Libri", href: "#books" },
  { label: "Contatti", href: "#contact" },
];

export const Header = () => {
  const scrollToSection = (href: string) => {
    const id = href.replace("#", "");
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-base ${
        isScrolled ? "glass shadow-md" : "bg-transparent"
      }`}
    >
      <nav className="container-wide">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <a
            href="#home"
            onClick={(e) => { e.preventDefault(); scrollToSection("#home"); }}
            className="text-lg text-foreground italic tracking-wide"
            style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
          >
            M.B.
          </a>

          {/* Desktop Navigation - Centered */}
          <ul className="hidden md:flex items-center gap-8 absolute left-1/2 -translate-x-1/2">
            {navItems.map((item) => (
              <li key={item.href} className="relative group">
                <a
                  href={item.href}
                  onClick={(e) => { e.preventDefault(); scrollToSection(item.href); }}
                  className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-base link-underline"
                >
                  {item.label}
                </a>
                {"subItems" in item && item.subItems && (
                  <div className="absolute top-full left-1/2 -translate-x-1/2 pt-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                    <div className="bg-card border border-border rounded-lg shadow-lg py-2 min-w-[160px]">
                      {item.subItems.map((sub) => (
                        <a
                          key={sub.category}
                          href="#projects"
                          onClick={(e) => {
                            e.preventDefault();
                            const event = new CustomEvent("filter-projects", { detail: sub.category });
                            window.dispatchEvent(event);
                            scrollToSection("#projects");
                          }}
                          className="block px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
                        >
                          {sub.label}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>

          {/* Spacer for flex alignment */}
          <div className="hidden md:block w-8" />

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-foreground"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden glass border-t border-border"
          >
            <div className="container-wide py-6">
              <ul className="flex flex-col gap-4">
                {navItems.map((item) => (
                  <li key={item.href}>
                    <a
                      href={item.href}
                      className="block py-2 text-lg font-medium text-foreground hover:text-accent transition-colors"
                      onClick={(e) => {
                        e.preventDefault();
                        scrollToSection(item.href);
                        setIsMobileMenuOpen(false);
                      }}
                    >
                      {item.label}
                    </a>
                    {"subItems" in item && item.subItems && (
                      <ul className="pl-4 mt-1 flex flex-col gap-1">
                        {item.subItems.map((sub) => (
                          <li key={sub.category}>
                            <a
                              href="#projects"
                              className="block py-1.5 text-base text-muted-foreground hover:text-accent transition-colors"
                              onClick={(e) => {
                                e.preventDefault();
                                const event = new CustomEvent("filter-projects", { detail: sub.category });
                                window.dispatchEvent(event);
                                scrollToSection("#projects");
                                setIsMobileMenuOpen(false);
                              }}
                            >
                              {sub.label}
                            </a>
                          </li>
                        ))}
                      </ul>
                    )}
                  </li>
                ))}
                <li className="pt-4">
                  <Button variant="hero" size="lg" className="w-full" asChild>
                    <a href="https://cal.com/mattiabaldinazzo" target="_blank" rel="noopener noreferrer">
                      Prenota un appuntamento
                    </a>
                  </Button>
                </li>
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
};
