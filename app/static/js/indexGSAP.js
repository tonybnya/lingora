(function() {
gsap.registerPlugin(ScrollTrigger);

// Hero Text Reveal
gsap.from(".hero h1", {
    y: 50,
    opacity: 0,
    duration: 1,
    ease: "power3.out"
});

gsap.from(".hero p", {
    y: 30,
    opacity: 0,
    duration: 1,
    delay: 0.3,
    ease: "power3.out"
});

gsap.from(".hero .btn-primary", {
    y: 20,
    opacity: 0,
    duration: 1,
    delay: 0.6,
    ease: "power3.out"
});

// Hero Card Fade In
gsap.from(".hero-card", {
    scrollTrigger: {
        trigger: ".hero-card",
        start: "top 85%",
    },
    y: 60,
    opacity: 0,
    duration: 1,
    ease: "power3.out"
});

// Feature Cards Stagger
gsap.from(".feature-card", {
    scrollTrigger: {
        trigger: "#features",
        start: "top 80%",
    },
    y: 60,
    opacity: 0,
    duration: 1,
    stagger: 0.2,
    ease: "power3.out"
});

// CTA Section Fade
gsap.from(".cta-section h2, .cta-section p", {
    scrollTrigger: {
        trigger: ".cta-section",
        start: "top 80%",
    },
    y: 50,
    opacity: 0,
    duration: 1,
    stagger: 0.15,
    ease: "power3.out"
});
})();
