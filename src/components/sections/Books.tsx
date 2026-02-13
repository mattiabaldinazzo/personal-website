import { motion } from "framer-motion";
import { Star, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

const books = [
  {
    title: "Colloqui con sé stesso",
    author: "Marco Aurelio",
    image: "https://mattiabaldinazzo.it/images/books/colloquiconsestesso.webp",
    rating: 5,
    description: "Raccolta di meditazioni sull'uomo, la sua vita, il suo rapporto con il cosmo.",
  },
  {
    title: "L'unica regola è che non ci sono regole",
    author: "Reed Hastings, Erin Meyer",
    image: "https://mattiabaldinazzo.it/images/books/netflix.webp",
    rating: 5,
    description: "Netflix e la cultura della reinvenzione.",
  },
  {
    title: "Padre ricco padre povero",
    author: "Robert T. Kiyosaki",
    image: "https://mattiabaldinazzo.it/images/books/padre_ricco_padre_povero.webp",
    rating: 5,
    description: "Quello che i ricchi insegnano ai figli sul denaro.",
  },
  {
    title: "La mucca viola",
    author: "Seth Godin",
    image: "https://mattiabaldinazzo.it/images/books/lamuccaviola.webp",
    rating: 5,
    description: "Bisogna essere straordinariamente innovativi, motivati e autentici.",
  },
  {
    title: "L'arte della guerra",
    author: "Sun Tzu",
    image: "https://mattiabaldinazzo.it/images/books/larte_della_guerra.webp",
    rating: 5,
    description: "Il trattato di strategia militare più antico e famoso.",
  },
  {
    title: "Rework",
    author: "Jason Fried, David Heinemeier Hansson",
    image: "https://mattiabaldinazzo.it/images/books/rework.webp",
    rating: 5,
    description: "Manifesto del nuovo imprenditore minimalista.",
  },
  {
    title: "Greenlights",
    author: "Matthew McConaughey",
    image: "https://mattiabaldinazzo.it/images/books/greenlights.webp",
    rating: 4,
    description: "Appunti su successi e fallimenti, gioie e dolori.",
  },
  {
    title: "Scrum",
    author: "Jeff Sutherland",
    image: "https://mattiabaldinazzo.it/images/books/scrum.webp",
    rating: 4,
    description: "L'approccio rivoluzionario al project management.",
  },
];

export const Books = () => {
  const [showAll, setShowAll] = useState(false);
  const displayedBooks = showAll ? books : books.slice(0, 4);

  return (
    <section id="books" className="section-padding bg-secondary/30">
      <div className="container-wide">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold text-foreground mb-4">
            Libri
          </h2>
          <div className="w-16 h-1 bg-accent mx-auto rounded-full mb-6" />
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Una selezione delle letture che mi hanno ispirato e formato.
          </p>
        </motion.div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {displayedBooks.map((book, index) => (
            <motion.article
              key={book.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              className="group bg-card rounded-xl border border-border shadow-sm hover:shadow-md transition-all duration-base overflow-hidden"
            >
              {/* Book Cover */}
              <div className="aspect-[2/3] overflow-hidden relative">
                <img
                  src={book.image}
                  alt={book.title}
                  className="w-full h-full object-cover transition-transform duration-slow group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-foreground/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-base" />
              </div>

              {/* Content */}
              <div className="p-2">
                {/* Rating */}
                <div className="flex items-center gap-0.5 mb-1">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      size={10}
                      className={i < book.rating ? "fill-accent text-accent" : "text-muted"}
                    />
                  ))}
                </div>

                <h3 className="font-display font-semibold text-xs text-foreground mb-0.5 line-clamp-1 group-hover:text-accent transition-colors">
                  {book.title}
                </h3>
                <p className="text-[10px] text-muted-foreground line-clamp-1">{book.author}</p>
              </div>
            </motion.article>
          ))}
        </div>

        {books.length > 4 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="text-center mt-10"
          >
            <button
              onClick={() => setShowAll(!showAll)}
              className="inline-flex items-center gap-2 px-6 py-3 text-sm font-medium text-foreground bg-card border border-border rounded-full hover:border-accent hover:text-accent transition-all duration-base"
            >
              {showAll ? (
                <>
                  Mostra meno <ChevronUp size={16} />
                </>
              ) : (
                <>
                  Visualizza tutti i libri <ChevronDown size={16} />
                </>
              )}
            </button>
          </motion.div>
        )}
      </div>
    </section>
  );
};
