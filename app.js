let allItems = [];
let filteredItems = [];
let currentIndex = 0;
const PAGE_SIZE = 60;
let selectedFiles = new Set();
let currentModalIndex = -1;

const gallery = document.getElementById('gallery');
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const stats = document.getElementById('stats');
const loader = document.getElementById('loader');
const selectionBar = document.getElementById('selectionBar');
const selectionCount = document.getElementById('selectionCount');

// Modal Elements
const assetModal = document.getElementById('assetModal');
const modalImg = document.getElementById('modalImg');
const modalTitle = document.getElementById('modalTitle');
const modalCategory = document.getElementById('modalCategory');
const modalTags = document.getElementById('modalTags');
const toastContainer = document.getElementById('toastContainer');

// Load Metadata
fetch('meta.json')
    .then(res => res.json())
    .then(data => {
        allItems = data.items;
        filteredItems = [...allItems];
        stats.innerText = `${data.object_count.toLocaleString()} icons found | Created with Nano Banana Pro`;
        
        const categories = [...new Set(allItems.map(i => i.category))];
        categories.sort();
        categories.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = opt.innerText = cat;
            categoryFilter.appendChild(opt);
        });
        
        loadMore();
    });

function loadMore() {
    const end = Math.min(currentIndex + PAGE_SIZE, filteredItems.length);
    const batch = filteredItems.slice(currentIndex, end);
    
    batch.forEach((item, index) => {
        const globalIndex = currentIndex + index;
        const card = document.createElement('div');
        card.className = 'card' + (selectedFiles.has(item.file_name) ? ' selected' : '');
        card.style.animationDelay = `${(index % PAGE_SIZE) * 20}ms`;
        card.dataset.index = globalIndex;
        
        card.innerHTML = `
            <img src="${item.file_name}" alt="${item.title}" loading="lazy">
            <h3>${item.title}</h3>
            <button class="dl-btn btn-secondary" onclick="downloadSingle('${item.file_name}', event)">Download</button>
        `;
        
        card.addEventListener('click', (e) => {
            if (e.target.tagName !== 'BUTTON') {
                if (e.ctrlKey || e.metaKey) {
                    toggleSelect(item.file_name, card);
                } else {
                    openModal(globalIndex);
                }
            }
        });
        
        gallery.appendChild(card);
    });
    
    currentIndex = end;
    loader.style.display = currentIndex >= filteredItems.length ? 'none' : 'block';
}

function toggleSelect(filename, element) {
    if (selectedFiles.has(filename)) {
        selectedFiles.delete(filename);
        element.classList.remove('selected');
    } else {
        selectedFiles.add(filename);
        element.classList.add('selected');
    }
    updateSelectionBar();
}

function updateSelectionBar() {
    const count = selectedFiles.size;
    selectionCount.innerText = `${count} items selected`;
    count > 0 ? selectionBar.classList.remove('hidden') : selectionBar.classList.add('hidden');
}

// Modal Logic
function openModal(index) {
    currentModalIndex = index;
    const item = filteredItems[index];
    modalImg.src = item.file_name;
    modalTitle.innerText = item.title;
    modalCategory.innerText = item.category;
    
    modalTags.innerHTML = '';
    item.tags.forEach(tag => {
        const span = document.createElement('span');
        span.className = 'tag';
        span.innerText = `#${tag}`;
        span.onclick = () => filterByTag(tag);
        modalTags.appendChild(span);
    });
    
    assetModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function filterByTag(tag) {
    closeModal();
    searchInput.value = tag;
    updateResults();
}

function closeModal() {
    assetModal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

document.querySelector('.close-modal').onclick = closeModal;
window.onclick = (e) => { if(e.target === assetModal) closeModal(); };

// Navigation inside Modal
document.getElementById('prevBtn').onclick = () => { if(currentModalIndex > 0) openModal(currentModalIndex - 1); };
document.getElementById('nextBtn').onclick = () => { if(currentModalIndex < filteredItems.length - 1) openModal(currentModalIndex + 1); };

// Keyboard shortcuts for modal
window.addEventListener('keydown', (e) => {
    if (assetModal.classList.contains('hidden')) return;
    if (e.key === 'ArrowLeft') document.getElementById('prevBtn').click();
    if (e.key === 'ArrowRight') document.getElementById('nextBtn').click();
    if (e.key === 'Escape') closeModal();
});

// Modal Actions
document.getElementById('modalDownloadBtn').onclick = () => downloadSingle(filteredItems[currentModalIndex].file_name);
document.getElementById('modalCopyBtn').onclick = () => {
    const url = window.location.href + filteredItems[currentModalIndex].file_name;
    navigator.clipboard.writeText(url);
    showToast('URL copied to clipboard! ✨');
};

function showToast(msg) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = msg;
    toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Global Actions
function downloadSingle(filename, e) {
    if (e) e.stopPropagation();
    const a = document.createElement('a');
    a.href = filename; a.download = filename;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
}

document.getElementById('downloadSelectedBtn').onclick = async () => {
    const files = Array.from(selectedFiles);
    for (const f of files) {
        downloadSingle(f);
        await new Promise(r => setTimeout(r, 150));
    }
    showToast(`Downloading ${files.length} items... 📦`);
};

document.getElementById('selectAllBtn').onclick = () => {
    document.querySelectorAll('.card').forEach(c => {
        const fn = c.dataset.filename || filteredItems[c.dataset.index].file_name;
        if (!selectedFiles.has(fn)) { selectedFiles.add(fn); c.classList.add('selected'); }
    });
    updateSelectionBar();
};

document.getElementById('deselectAllBtn').onclick = () => {
    selectedFiles.clear();
    document.querySelectorAll('.card').forEach(c => c.classList.remove('selected'));
    updateSelectionBar();
};

// Search & Filter
function updateResults() {
    const q = searchInput.value.toLowerCase();
    const cat = categoryFilter.value;
    filteredItems = allItems.filter(item => {
        return (item.title.toLowerCase().includes(q) || item.tags.some(t => t.toLowerCase().includes(q))) &&
               (cat === '' || item.category === cat);
    });
    gallery.innerHTML = ''; currentIndex = 0;
    loadMore();
}

searchInput.addEventListener('input', updateResults);
categoryFilter.addEventListener('change', updateResults);

// Infinite Scroll
window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 800) {
        if (currentIndex < filteredItems.length) loadMore();
    }
});
