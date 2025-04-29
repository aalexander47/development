// Wait for the page to load
document.addEventListener("DOMContentLoaded", function () {
  // Split the text into words
  let typeSplit = new SplitType("[animate]", {
    types: "lines, words, chars",
    tagName: "span",
  });

  // Register ScrollTrigger
  gsap.registerPlugin(ScrollTrigger);

  // GSAP Animation
  gsap.from("[animate] .word", {
    y: "110%",
    opacity: 0,
    rotationZ: 10,
    duration: 0.4,
    ease: "back.out",
    stagger: 0.1,
    scrollTrigger: {
      trigger: "[animate]",
      start: "top 80%", // Adjust when the animation starts
      toggleActions: "play none none none", // Play animation once
    },
  });
});
