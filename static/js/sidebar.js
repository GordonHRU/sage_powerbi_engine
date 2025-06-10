// Sidebar functionality
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content-sidebar');
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Mobile behavior - show/hide sidebar with overlay
        sidebar.classList.toggle('mobile-open');
        toggleOverlay();
    } else {
        // Desktop behavior - collapse/expand
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('collapsed');
        
        // Update arrow state
        updateToggleArrow();
    }
}

// Update toggle arrow based on sidebar state
function updateToggleArrow() {
    const sidebar = document.getElementById('sidebar');
    const collapseArrow = document.getElementById('collapseArrow');
    
    if (sidebar.classList.contains('collapsed')) {
        // When collapsed, show right arrow (expand icon)
        collapseArrow.textContent = '›';
    } else {
        // When expanded, show left arrow (collapse icon)
        collapseArrow.textContent = '‹';
    }
}

function toggleOverlay() {
    let overlay = document.querySelector('.sidebar-overlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.onclick = closeSidebar;
        document.body.appendChild(overlay);
    }
    
    overlay.classList.toggle('show');
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    sidebar.classList.remove('mobile-open');
    if (overlay) {
        overlay.classList.remove('show');
    }
}

// Handle window resize
window.addEventListener('resize', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (window.innerWidth > 768) {
        // Desktop mode - remove mobile classes
        sidebar.classList.remove('mobile-open');
        if (overlay) {
            overlay.classList.remove('show');
        }
        // Update arrow for desktop mode
        updateToggleArrow();
    } else {
        // Mobile mode - reset desktop classes
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('collapsed');
        // Reset arrow for mobile
        document.getElementById('collapseArrow').textContent = '‹';
    }
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const collapseBtn = document.querySelector('.collapse-btn');
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile && 
        sidebar.classList.contains('mobile-open') && 
        !sidebar.contains(event.target) && 
        !collapseBtn.contains(event.target)) {
        closeSidebar();
    }
});

// Initialize sidebar state
document.addEventListener('DOMContentLoaded', function() {
    // FORCE EXPANDED STATE - completely ignore any stored preferences
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content-sidebar');
    
    // Explicitly ensure expanded state
    sidebar.classList.remove('collapsed');
    mainContent.classList.remove('collapsed');
    
    // Clear any stored collapsed preference to start fresh
    localStorage.setItem('sidebarCollapsed', 'false');
    
    // Set the arrow to show left arrow (collapse action)
    const collapseArrow = document.getElementById('collapseArrow');
    collapseArrow.textContent = '‹';
    
    // Add smooth transition after ensuring expanded state
    setTimeout(() => {
        sidebar.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    }, 100);
    
    console.log('Sidebar initialized - Expanded state enforced');
});

// Save sidebar state
window.addEventListener('beforeunload', function() {
    const sidebar = document.getElementById('sidebar');
    const isCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('sidebarCollapsed', isCollapsed);
});

// Save sidebar state
window.addEventListener('beforeunload', function() {
    const sidebar = document.getElementById('sidebar');
    const isCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('sidebarCollapsed', isCollapsed);
});