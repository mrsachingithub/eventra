document.addEventListener('DOMContentLoaded', () => {
    const carouselItems = document.querySelectorAll('.carousel-item');
    let currentIndex = 1; // Start with the middle item (index 1) active
    let textTimeout;

    function updateCarousel() {
        // Clear any existing timeout when switching
        clearTimeout(textTimeout);

        carouselItems.forEach((item, index) => {
            item.classList.remove('active', 'prev', 'next', 'hide-content');
            const video = item.querySelector('video');

            if (index === currentIndex) {
                item.classList.add('active');
                video.play();
                video.muted = false;

                // Hide content after 4 seconds
                textTimeout = setTimeout(() => {
                    item.classList.add('hide-content');
                }, 4000);

            } else {
                video.pause();
                video.currentTime = 0;
                video.muted = true;

                if (index === (currentIndex - 1 + 3) % 3) {
                    item.classList.add('prev');
                } else if (index === (currentIndex + 1) % 3) {
                    item.classList.add('next');
                }
            }
        });
    }

    carouselItems.forEach((item, index) => {
        item.addEventListener('click', () => {
            if (currentIndex !== index) {
                currentIndex = index;
                updateCarousel();
            }
        });
    });

    // Initial update
    updateCarousel();

    // Pause video on scroll (when out of view)
    // Pause video on scroll (when out of view)
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            // Find the active video *within* the container being observed
            const container = entry.target;
            const activeItem = container.querySelector('.carousel-item.active');
            const video = activeItem ? activeItem.querySelector('video') : null;

            if (!entry.isIntersecting) {
                // Paused when out of view (less than 50% visible)
                if (video && !video.paused) {
                    video.pause();
                    console.log('Hero section out of view - Video Paused');
                }
            } else {
                // Resume when back in view
                // Only play if it was paused by scroll (not manually) - simplified to just play for now
                if (video && video.paused) {
                    video.play().catch(e => console.log('Autoplay prevented:', e));
                    console.log('Hero section in view - Video Resumed');
                }
            }
        });
    }, { threshold: 0.2 }); // Trigger when 20% is visible/hidden (adjust as needed)

    const container = document.querySelector('.carousel-container');
    if (container) observer.observe(container);
});
