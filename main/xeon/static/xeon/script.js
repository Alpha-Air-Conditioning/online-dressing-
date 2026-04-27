document.addEventListener('DOMContentLoaded', () => {

    // 1. Sticky Header UI Change on Scroll
    const header = document.getElementById('header');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // 2. Newsletter Popup Logic
    const popup = document.getElementById('newsletterPopup');
    const closeBtn = document.getElementById('closePopup');

    // Show popup after 3 seconds if not already shown in this session
    if (!sessionStorage.getItem('newsletterShown')) {
        setTimeout(() => {
            popup.classList.add('show');
            sessionStorage.setItem('newsletterShown', 'true');
        }, 3000);
    }

    // Close logic
    const closePopup = () => {
        popup.classList.remove('show');
    };

    closeBtn.addEventListener('click', closePopup);

    // Close on outside click (click overlay to close)
    popup.addEventListener('click', (e) => {
        if (e.target === popup) {
            closePopup();
        }
    });
    
    // Close on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && popup.classList.contains('show')) {
            closePopup();
        }
    });

    // 3. Mobile Navigation Drawer Logic
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const closeMenuBtn = document.getElementById('closeMenuBtn');
    const mobileDrawer = document.getElementById('mobileDrawer');
    const mobileDrawerOverlay = document.getElementById('mobileDrawerOverlay');

    const openDrawer = () => {
        mobileDrawer.classList.add('open');
        mobileDrawerOverlay.classList.add('show');
    };

    const closeDrawer = () => {
        mobileDrawer.classList.remove('open');
        mobileDrawerOverlay.classList.remove('show');
    };

    if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', openDrawer);
    if (closeMenuBtn) closeMenuBtn.addEventListener('click', closeDrawer);
    if (mobileDrawerOverlay) mobileDrawerOverlay.addEventListener('click', closeDrawer);

});
