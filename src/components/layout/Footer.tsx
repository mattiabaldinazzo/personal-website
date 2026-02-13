import { Github, Linkedin, Instagram, Heart } from "lucide-react";

const socialLinks = [
  { icon: Linkedin, href: "https://www.linkedin.com/in/mattiabaldinazzo", label: "LinkedIn" },
  { icon: Github, href: "https://github.com/mattiabaldinazzo", label: "GitHub" },
  { icon: Instagram, href: "https://instagram.com/mattiabaldinazzo", label: "Instagram" },
];

export const Footer = () => {
  return (
    <footer className="py-8 border-t border-border">
      <div className="container-wide">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo */}
          <a
            href="#home"
            className="text-lg text-foreground italic tracking-wide"
            style={{ fontFamily: "'Cormorant Garamond', Georgia, serif" }}
          >
            M.B.
          </a>

          {/* Copyright */}
          <p className="text-sm text-muted-foreground flex items-center gap-1">
            Made with <Heart size={14} className="text-accent fill-accent" /> by Mattia Baldinazzo
          </p>

          {/* Social Links */}
          <div className="flex items-center gap-3">
            {socialLinks.map((social) => (
              <a
                key={social.label}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-muted-foreground hover:text-accent transition-colors"
                aria-label={social.label}
              >
                <social.icon size={18} />
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
};
