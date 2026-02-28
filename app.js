const vases = [
  { id: 1, name: 'Aero Minimal', style: 'minimal', material: 'PLA', basePrice: 32, colors: ['White','Black','Sand'], image: 'https://images.pexels.com/photos/1804035/pexels-photo-1804035.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop' },
  { id: 2, name: 'Helix Bloom', style: 'spiral', material: 'PETG', basePrice: 48, colors: ['Teal','Amber','Graphite'], image: 'https://images.pexels.com/photos/4611612/pexels-photo-4611612.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop' },
  { id: 3, name: 'Prism Nest', style: 'geometric', material: 'PLA', basePrice: 39, colors: ['Ivory','Olive','Slate'], image: 'https://images.pexels.com/photos/1166644/pexels-photo-1166644.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop' },
  { id: 4, name: 'Coral Flow', style: 'organic', material: 'Resin', basePrice: 74, colors: ['Pearl','Rose','Smoke'], image: 'https://images.pexels.com/photos/4207892/pexels-photo-4207892.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop' },
  { id: 5, name: 'Facet Tower', style: 'geometric', material: 'PETG', basePrice: 56, colors: ['Cobalt','Lime','Silver'], image: 'https://images.pexels.com/photos/6805522/pexels-photo-6805522.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop' },
  { id: 6, name: 'Zen Curve', style: 'minimal', material: 'PLA', basePrice: 29, colors: ['Cream','Navy','Terracotta'], image: 'https://images.pexels.com/photos/2062433/pexels-photo-2062433.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop' }
];

const sizeMultiplier = { small: 0.9, medium: 1, large: 1.25 };

const catalogEl = document.getElementById('catalog');
const cartEl = document.getElementById('cart');
const totalEl = document.getElementById('total');
const statusEl = document.getElementById('status');
const template = document.getElementById('cardTemplate');
const styleFilter = document.getElementById('styleFilter');
const materialFilter = document.getElementById('materialFilter');
const priceFilter = document.getElementById('priceFilter');
const priceValue = document.getElementById('priceValue');

let cart = [];

function money(n) { return Math.round(n * 100) / 100; }

function filteredVases() {
  return vases.filter(v => {
    const styleOK = styleFilter.value === 'all' || v.style === styleFilter.value;
    const matOK = materialFilter.value === 'all' || v.material === materialFilter.value;
    const priceOK = v.basePrice <= Number(priceFilter.value);
    return styleOK && matOK && priceOK;
  });
}

function renderCatalog() {
  catalogEl.innerHTML = '';
  filteredVases().forEach(vase => {
    const node = template.content.cloneNode(true);
    node.querySelector('.card-img').src = vase.image;
    node.querySelector('.card-img').alt = vase.name;
    node.querySelector('.title').textContent = vase.name;
    node.querySelector('.meta').textContent = `${vase.style} • ${vase.material}`;
    node.querySelector('.price').textContent = `From $${vase.basePrice}`;

    const colorSelect = node.querySelector('.color');
    vase.colors.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      colorSelect.appendChild(opt);
    });

    node.querySelector('.add').addEventListener('click', () => {
      const size = node.querySelector('.size').value;
      const color = colorSelect.value;
      const price = money(vase.basePrice * sizeMultiplier[size]);
      cart.push({ vaseId: vase.id, name: vase.name, size, color, price });
      renderCart();
    });

    catalogEl.appendChild(node);
  });
}

function renderCart() {
  cartEl.innerHTML = '';
  let total = 0;

  cart.forEach((item, i) => {
    total += item.price;
    const li = document.createElement('li');
    li.innerHTML = `${item.name} (${item.size}, ${item.color}) — $${item.price} <button data-i="${i}">x</button>`;
    li.querySelector('button').addEventListener('click', () => {
      cart.splice(i, 1);
      renderCart();
    });
    cartEl.appendChild(li);
  });

  totalEl.textContent = money(total);
}

[styleFilter, materialFilter, priceFilter].forEach(el => {
  el.addEventListener('input', () => {
    priceValue.textContent = priceFilter.value;
    renderCatalog();
  });
});

document.getElementById('checkoutForm').addEventListener('submit', (e) => {
  e.preventDefault();
  if (!cart.length) {
    statusEl.textContent = 'Your cart is empty.';
    return;
  }
  const order = {
    id: `ORD-${Date.now()}`,
    customer: {
      name: document.getElementById('name').value,
      email: document.getElementById('email').value,
      address: document.getElementById('address').value
    },
    items: cart,
    total: Number(totalEl.textContent)
  };

  localStorage.setItem(order.id, JSON.stringify(order));
  cart = [];
  renderCart();
  e.target.reset();
  statusEl.textContent = `Order ${order.id} placed successfully.`;
});

priceValue.textContent = priceFilter.value;
renderCatalog();
renderCart();
