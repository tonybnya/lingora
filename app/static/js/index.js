(function () {
    document.getElementById('footer-year').textContent = new Date().getFullYear();

    function init() {
    const canvas = document.getElementById('bg-canvas');
    if (!window.THREE) { console.warn('Three.js not loaded.'); return; }

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.domElement.style.width = '100%';
    renderer.domElement.style.height = '100%';

    // Particle System
    const particleCount = 800;
    const particlesGeometry = new THREE.BufferGeometry();
    const posArray = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 5;
    }
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

    const particlesMaterial = new THREE.PointsMaterial({
        size: 0.015,
        color: 0x00FF00,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending
    });

    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particlesMesh);
    camera.position.z = 2;

    // Mouse State
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;
    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX - windowHalfX) * 0.001;
        mouseY = (event.clientY - windowHalfY) * 0.001;
    });

    // Animation
    const clock = new THREE.Clock();
    function animate() {
        requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        // Breathing pulse effect
        particlesMaterial.size = 0.015 + Math.sin(elapsedTime * 0.5) * 0.005;
        particlesMaterial.opacity = 0.4 + Math.sin(elapsedTime * 0.8) * 0.2;

        // Parallax Drift
        targetX = mouseX * 0.5;
        targetY = mouseY * 0.5;
        particlesMesh.rotation.y += 0.05 * (targetX - particlesMesh.rotation.y);
        particlesMesh.rotation.x += 0.05 * (targetY - particlesMesh.rotation.x);

        renderer.render(scene, camera);
    }
    animate();

    // Resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
    }

    // Defer the heavy WebGL scene until the browser is idle so the page
    // text and CSS paint first. 2s hard ceiling in case the callback
    // never fires (some browsers throttle idle in background tabs).
    if ('requestIdleCallback' in window) {
        requestIdleCallback(init, { timeout: 2000 });
    } else {
        setTimeout(init, 200);
    }
})();
