// Store for recently viewed services
let recentlyViewed = JSON.parse(localStorage.getItem('recentlyViewed') || '[]');

// Function to add a service to recently viewed
function addToRecentlyViewed(serviceName, iconSrc, href) {
    // Remove if already exists to avoid duplicates
    recentlyViewed = recentlyViewed.filter(item => item.name !== serviceName);
    
    // Add to beginning of array
    recentlyViewed.unshift({
        name: serviceName,
        icon: iconSrc,
        href: href,
        timestamp: Date.now()
    });
    
    // Keep only last 3 items
    if (recentlyViewed.length > 3) {
        recentlyViewed = recentlyViewed.slice(0, 3);
    }
    
    // Save to localStorage
    localStorage.setItem('recentlyViewed', JSON.stringify(recentlyViewed));
    
    // Update display
    updateLastViewedDisplay();
}

// Function to update the Last Viewed display
function updateLastViewedDisplay() {
    const lastViewedContent = document.getElementById('lastViewedContent');
    
    if (!lastViewedContent) return; // Element not found on this page
    
    if (recentlyViewed.length === 0) {
        lastViewedContent.innerHTML = `
            <img src="/static/image/ServiceIcon/NoResources.png" class="NoResources" alt="No Resources"/>
            <p class="no-recent-text">No resources have been viewed recently</p>
        `;
    } else {
        const buttonsHTML = recentlyViewed.map(item => `
            <div class="vertical">
                <a class="icon-link" href="${item.href}" onclick="addToRecentlyViewed('${item.name}', '${item.icon}', '${item.href}')">
                    <img src="${item.icon}" alt="${item.name}"/>
                    ${item.name}
                </a>
            </div>
        `).join('');
        
        lastViewedContent.innerHTML = `
            <div class="horizontal">${buttonsHTML}</div>
            <button class="clear-history-btn" onclick="clearRecentlyViewed()">Clear History</button>
        `;
    }
}

// Function to clear recently viewed services
function clearRecentlyViewed() {
    // Clear the array
    recentlyViewed = [];
    
    // Remove from localStorage
    localStorage.removeItem('recentlyViewed');
    
    // Update display
    updateLastViewedDisplay();
}

// Add click event listeners to all service buttons (for index page only)
document.addEventListener('DOMContentLoaded', function() {
    // Only run on index page
    if (window.location.pathname === '/' || window.location.pathname === '/index/') {
        const serviceLinks = document.querySelectorAll('.container .horizontal .icon-link');
        
        serviceLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const serviceName = this.textContent.trim();
                const iconSrc = this.querySelector('img').src;
                const href = this.href;
                
                addToRecentlyViewed(serviceName, iconSrc, href);
            });
        });
        
        // Initial display update
        updateLastViewedDisplay();
    }
});