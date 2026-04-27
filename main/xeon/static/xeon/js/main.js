/* ═══════════════════════════════════════════════════════════
   XEON FASHION STORE — Cart & UI JavaScript
   ═══════════════════════════════════════════════════════════ */

// Enable JS-powered fade animations
document.body.classList.add('js-loaded');

// ── CSRF Token helper ─────────────────────────────────────────
function getCsrfToken() {
  return document.cookie.split(';')
    .find(c => c.trim().startsWith('csrftoken='))
    ?.split('=')[1] || '';
}

// ── Toast Notifications ──────────────────────────────────────
const toastContainer = document.getElementById('toast-container');

function showToast(message, type = 'success', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ── Update Cart Badge Count ───────────────────────────────────
function updateCartBadge(count) {
  const badge = document.getElementById('cart-count-badge');
  if (!badge) return;
  if (count > 0) {
    badge.textContent = count;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
}

// ── Add to Cart ───────────────────────────────────────────────
async function addToCart(productId, size, quantity = 1) {
  try {
    const res = await fetch('/cart/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ product_id: productId, size: size, quantity: quantity }),
    });
    const data = await res.json();
    if (data.success) {
      updateCartBadge(data.cart_count);
      showToast(data.message, 'success');
    } else {
      showToast(data.message || 'Error adding to cart', 'error');
    }
    return data;
  } catch (err) {
    showToast('Network error. Try again.', 'error');
  }
}

// ── Remove from Cart ──────────────────────────────────────────
async function removeFromCart(cartKey) {
  try {
    const res = await fetch('/cart/remove/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ key: cartKey }),
    });
    const data = await res.json();
    if (data.success) {
      updateCartBadge(data.cart_count);
      const row = document.getElementById(`cart-item-${cartKey}`);
      if (row) {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-16px)';
        setTimeout(() => { row.remove(); updateCartTotals(); }, 300);
      }
    }
    return data;
  } catch (err) {
    showToast('Network error.', 'error');
  }
}

// ── Update Cart Quantity ──────────────────────────────────────
async function updateCartQty(cartKey, quantity) {
  try {
    const res = await fetch('/cart/update/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ key: cartKey, quantity: quantity }),
    });
    const data = await res.json();
    if (data.success) {
      updateCartBadge(data.cart_count);
      updateCartTotals();
    }
    return data;
  } catch (err) {}
}

// ── Cart Page: Update Displayed Totals ────────────────────────
function updateCartTotals() {
  let subtotal = 0;
  document.querySelectorAll('.cart-item').forEach(row => {
    const price  = parseFloat(row.dataset.price  || 0);
    const qty    = parseInt(row.querySelector('.qty-val')?.textContent || 0);
    const lineEl = row.querySelector('.cart-item-price');
    const line   = price * qty;
    subtotal += line;
    if (lineEl) lineEl.textContent = '₹' + line.toFixed(2);
  });

  const shipping    = subtotal > 0 && subtotal < 999 ? 99 : 0;
  const total       = subtotal + shipping;
  const subtotalEl  = document.getElementById('summary-subtotal');
  const shippingEl  = document.getElementById('summary-shipping');
  const totalEl     = document.getElementById('summary-total');
  const freeShipEl  = document.getElementById('free-ship-note');

  if (subtotalEl)  subtotalEl.textContent  = '₹' + subtotal.toFixed(2);
  if (shippingEl)  shippingEl.textContent  = shipping === 0 ? 'FREE' : '₹99.00';
  if (totalEl)     totalEl.textContent     = '₹' + total.toFixed(2);
  if (freeShipEl)  freeShipEl.style.display = shipping === 0 ? 'block' : 'none';

  // If cart is empty
  const cartItems = document.querySelectorAll('.cart-item');
  if (cartItems.length === 0) {
    const cartBody = document.getElementById('cart-body');
    if (cartBody) {
      cartBody.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">🛍️</div>
          <h2 class="empty-state-title">Your cart is empty</h2>
          <p class="empty-state-text">Explore our collection and add items you love.</p>
          <a href="/collection/" class="btn btn-primary btn-lg">Browse Collection</a>
        </div>`;
    }
  }
}

// ── Cart Page: Bind Qty Controls ──────────────────────────────
document.querySelectorAll('.cart-item').forEach(row => {
  row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
  const key     = row.dataset.key;
  const minusBtn = row.querySelector('.qty-minus');
  const plusBtn  = row.querySelector('.qty-plus');
  const qtyEl    = row.querySelector('.qty-val');
  const removeBtn = row.querySelector('.cart-remove');

  if (minusBtn && plusBtn && qtyEl) {
    plusBtn.addEventListener('click', () => {
      const qty = parseInt(qtyEl.textContent) + 1;
      qtyEl.textContent = qty;
      updateCartQty(key, qty);
    });

    minusBtn.addEventListener('click', () => {
      const qty = parseInt(qtyEl.textContent) - 1;
      if (qty <= 0) {
        removeFromCart(key);
      } else {
        qtyEl.textContent = qty;
        updateCartQty(key, qty);
      }
    });
  }

  if (removeBtn) {
    removeBtn.addEventListener('click', () => removeFromCart(key));
  }
});

// ── Product Detail: Size Selection ───────────────────────────
const sizeBtns = document.querySelectorAll('.size-btn');
let selectedSize = '';

sizeBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    sizeBtns.forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    selectedSize = btn.dataset.size;
  });
});

// Auto-select first size
if (sizeBtns.length > 0) {
  sizeBtns[0].click();
}

// ── Add to Cart button on Detail Page ────────────────────────
const addToCartDetailBtn = document.getElementById('add-to-cart-btn');
if (addToCartDetailBtn) {
  addToCartDetailBtn.addEventListener('click', () => {
    const pid = addToCartDetailBtn.dataset.productId;
    const size = selectedSize || 'FREE';
    addToCart(pid, size);
  });
}

// ── Buy Now button on Detail Page ─────────────────────────────
const buyNowBtn = document.getElementById('buy-now-btn');
if (buyNowBtn) {
  buyNowBtn.addEventListener('click', async () => {
    const pid  = buyNowBtn.dataset.productId;
    const size = selectedSize || 'FREE';
    await addToCart(pid, size);
    window.location.href = '/checkout/';
  });
}

// ── Quick Add from Product Cards ──────────────────────────────
document.querySelectorAll('.btn-quick-add').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    const card = btn.closest('.product-card');
    const pid  = card.dataset.productId;
    const selectedChip = card.querySelector('.size-chip.selected');
    const size = selectedChip ? selectedChip.dataset.size : 'FREE';
    addToCart(pid, size);
  });
});

// ── Size chip selection on product cards ─────────────────────
document.querySelectorAll('.size-chip').forEach(chip => {
  chip.addEventListener('click', (e) => {
    e.stopPropagation();
    const card = chip.closest('.product-card');
    card.querySelectorAll('.size-chip').forEach(c => c.classList.remove('selected'));
    chip.classList.add('selected');
  });
});

// ── Wishlist Toggle ───────────────────────────────────────────
document.querySelectorAll('.product-wishlist').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    btn.classList.toggle('active');
    showToast(
      btn.classList.contains('active') ? 'Added to wishlist ♥' : 'Removed from wishlist',
      'info'
    );
  });
});

// ── Click card → go to product page ──────────────────────────
document.querySelectorAll('.product-card[data-href]').forEach(card => {
  card.addEventListener('click', (e) => {
    if (!e.target.closest('button') && !e.target.closest('.quick-add-overlay')) {
      window.location.href = card.dataset.href;
    }
  });
});

// ── Hero Slider ───────────────────────────────────────────────
const slides = document.querySelectorAll('.hero-slide');
const dots   = document.querySelectorAll('.hero-dot');
let current  = 0;
let sliderInterval;

function goToSlide(n) {
  slides.forEach((s, i) => s.classList.toggle('active', i === n));
  dots.forEach((d, i)  => d.classList.toggle('active', i === n));
  current = n;
}

function nextSlide() {
  goToSlide((current + 1) % slides.length);
}

if (slides.length > 1) {
  sliderInterval = setInterval(nextSlide, 5000);
  dots.forEach((dot, i) => {
    dot.addEventListener('click', () => {
      clearInterval(sliderInterval);
      goToSlide(i);
      sliderInterval = setInterval(nextSlide, 5000);
    });
  });
}

// ── User Dropdown Toggle ───────────────────────────────────────
const userMenuTrigger = document.getElementById('user-menu-trigger');
const userDropdown    = document.getElementById('user-dropdown');

if (userMenuTrigger && userDropdown) {
  userMenuTrigger.addEventListener('click', (e) => {
    e.stopPropagation();
    userDropdown.classList.toggle('active');
    userMenuTrigger.setAttribute('aria-expanded', userDropdown.classList.contains('active'));
  });

  document.addEventListener('click', (e) => {
    if (!userDropdown.contains(e.target) && !userMenuTrigger.contains(e.target)) {
      userDropdown.classList.remove('active');
      userMenuTrigger.setAttribute('aria-expanded', 'false');
    }
  });
}

// ── Mobile Nav ────────────────────────────────────────────────
const hamburger   = document.getElementById('hamburger');
const mobileNav   = document.getElementById('mobile-nav');
const mobileClose = document.getElementById('mobile-nav-close');
const mobileOverlay = document.getElementById('mobile-nav-overlay');

function openMobileNav() {
  mobileNav?.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeMobileNav() {
  mobileNav?.classList.remove('open');
  document.body.style.overflow = '';
}

hamburger?.addEventListener('click', () => {
  hamburger.classList.toggle('open');
  hamburger.classList.contains('open') ? openMobileNav() : closeMobileNav();
});

mobileClose?.addEventListener('click', closeMobileNav);
mobileOverlay?.addEventListener('click', closeMobileNav);

// ── Search Drawer ─────────────────────────────────────────────
const searchBtn    = document.getElementById('search-btn');
const searchDrawer = document.getElementById('search-drawer');
const searchClose  = document.getElementById('search-close');

searchBtn?.addEventListener('click', () => {
  searchDrawer?.classList.add('open');
  document.getElementById('search-input')?.focus();
});

searchClose?.addEventListener('click', () => searchDrawer?.classList.remove('open'));

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    searchDrawer?.classList.remove('open');
    closeMobileNav();
  }
});

// ── Newsletter Form ───────────────────────────────────────────
const newsletterForm = document.getElementById('newsletter-form');
if (newsletterForm) {
  newsletterForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = newsletterForm.querySelector('input[type="email"]').value;
    const msgEl = document.getElementById('newsletter-msg');
    try {
      const res = await fetch('/newsletter/subscribe/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (msgEl) {
        msgEl.textContent = data.message;
        msgEl.style.color = data.success ? '#27ae60' : '#c0392b';
      }
      if (data.success) newsletterForm.reset();
    } catch (e) {
      if (msgEl) msgEl.textContent = 'Something went wrong. Try again.';
    }
  });
}

// ── Scroll Reveal (fade-up) ───────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

// ── Sort select on collection page ───────────────────────────
const sortSelect = document.getElementById('sort-select');
if (sortSelect) {
  sortSelect.addEventListener('change', () => {
    const url = new URL(window.location.href);
    url.searchParams.set('sort', sortSelect.value);
    url.searchParams.delete('page');
    window.location.href = url.toString();
  });
}
