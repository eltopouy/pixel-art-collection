let allItems = [];
let filteredItems = [];
let currentIndex = 0;
const PAGE_SIZE = 50;

const gallery = document.getElementById('gallery');
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const stats = document.getElementById('stats');
const loader = document.getElementById('loader');

// Load Metadata
fetch('meta.json')
    .then(res => res.json())
    .then(data => {
        allItems = data.items;
        filteredItems = [...allItems];
        stats.innerText = `${data.object_count.toLocaleString()} icons found | Generated with Gemini Banana`;
        
        // Setup Categories
        const categories = [...new Set(allItems.map(i => i.category))];
        categories.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = opt.innerText = cat;
            categoryFilter.appendChild(opt);
        });
        
        loadMore();
    });

// Render a batch of images
function loadMore() {
    const end = Math.min(currentIndex + PAGE_SIZE, filteredItems.length);
    const batch = filteredItems.slice(currentIndex, end);
    
    batch.forEach(item => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <img src="${item.file_name}" alt="${item.title}" loading="lazy">
            <h3>${item.title}</h3>
            <p>${item.category}</p>
        `;
        gallery.appendChild(card);
    });
    
    currentIndex = end;
    
    if (currentIndex >= filteredItems.length) {
        loader.style.display = 'none';
    } else {
        loader.style.display = 'block';
    }
}

// Search and Filter
function updateResults() {
    const q = searchInput.value.toLowerCase();
    const cat = categoryFilter.value;
    
    filteredItems = allItems.filter(item => {
        const matchSearch = item.title.toLowerCase().includes(q) || 
                            item.tags.some(t => t.toLowerCase().includes(q));
        const matchCat = cat === '' || item.category === cat;
        return matchSearch && matchCat;
    });
    
    gallery.innerHTML = '';
    currentIndex = 0;
    loadMore();
}

searchInput.addEventListener('input', updateResults);
categoryFilter.addEventListener('change', updateResults);

// Infinite Scroll
window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
        if (currentIndex < filteredItems.length) {
            loadMore();
        }
    }
});
