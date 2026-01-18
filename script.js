// Mobile Menu Toggle
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const mobileMenu = document.getElementById('mobileMenu');
const menuIcon = document.getElementById('menuIcon');
const closeIcon = document.getElementById('closeIcon');

let isMenuOpen = false;

mobileMenuBtn.addEventListener('click', () => {
  isMenuOpen = !isMenuOpen;
  mobileMenu.classList.toggle('active', isMenuOpen);
  menuIcon.style.display = isMenuOpen ? 'none' : 'block';
  closeIcon.style.display = isMenuOpen ? 'block' : 'none';
});

// Close mobile menu when clicking a link
document.querySelectorAll('.mobile-nav-link').forEach(link => {
  link.addEventListener('click', () => {
    isMenuOpen = false;
    mobileMenu.classList.remove('active');
    menuIcon.style.display = 'block';
    closeIcon.style.display = 'none';
  });
});

// Animated Counter
class AnimatedCounter {
  constructor(element, target, duration = 2000, suffix = '') {
    this.element = element;
    this.target = target;
    this.duration = duration;
    this.suffix = suffix;
    this.hasAnimated = false;
  }

  animate() {
    if (this.hasAnimated) return;
    this.hasAnimated = true;

    const startTime = performance.now();
    
    const update = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / this.duration, 1);
      
      // Ease out quart
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const currentValue = Math.floor(easeOutQuart * this.target);
      
      this.element.textContent = currentValue.toLocaleString() + this.suffix;
      
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    };
    
    requestAnimationFrame(update);
  }
}

// Initialize counters with Intersection Observer
const counters = [];
document.querySelectorAll('[data-counter]').forEach(element => {
  const target = parseInt(element.dataset.counter);
  const suffix = element.dataset.suffix || '';
  counters.push(new AnimatedCounter(element, target, 2000, suffix));
});

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const index = Array.from(document.querySelectorAll('[data-counter]')).indexOf(entry.target);
      if (counters[index]) {
        counters[index].animate();
      }
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('[data-counter]').forEach(el => {
  counterObserver.observe(el);
});

// Smooth Scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Animate elements on scroll
const animateOnScroll = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-slide-up');
      animateOnScroll.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.feature-card, .stat-card').forEach(el => {
  el.style.opacity = '0';
  animateOnScroll.observe(el);
});

// Update copyright year
document.getElementById('currentYear').textContent = new Date().getFullYear();
