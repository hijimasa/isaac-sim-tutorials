/* Isaac Sim Tutorials - Extra JavaScript */

document.addEventListener("DOMContentLoaded", function () {
  // Add smooth entrance animation to tutorial cards
  const cards = document.querySelectorAll(".tutorial-card");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          entry.target.style.transitionDelay = `${index * 0.05}s`;
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  cards.forEach((card) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";
    card.style.transition = "opacity 0.4s ease, transform 0.4s ease";
    observer.observe(card);
  });

  // CSS class for visible state
  const style = document.createElement("style");
  style.textContent = `.tutorial-card.visible { opacity: 1 !important; transform: translateY(0) !important; }`;
  document.head.appendChild(style);
});
