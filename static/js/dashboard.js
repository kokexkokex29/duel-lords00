// Dashboard JavaScript for BombSquad Tournament Bot
class TournamentDashboard {
    constructor() {
        this.refreshInterval = 30000; // 30 seconds
        this.autoRefreshTimer = null;
        this.lastUpdateTime = new Date();
        this.isRefreshing = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.startAutoRefresh();
        this.updateLastUpdateTime();
        
        // Initialize tooltips if Bootstrap is available
        if (typeof bootstrap !== 'undefined') {
            this.initializeTooltips();
        }
        
        console.log('Tournament Dashboard initialized');
    }
    
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('[onclick="refreshData()"]');
        if (refreshBtn) {
            refreshBtn.removeAttribute('onclick');
            refreshBtn.addEventListener('click', () => this.refreshData());
        }
        
        // Filter buttons for various pages
        this.setupFilterButtons();
        
        // Setup card hover effects
        this.setupCardEffects();
        
        // Setup responsive behavior
        this.setupResponsiveBehavior();
    }
    
    setupFilterButtons() {
        // Tournament filters
        const tournamentFilters = document.querySelectorAll('[onclick*="filterTournaments"]');
        tournamentFilters.forEach(btn => {
            const status = btn.getAttribute('onclick').match(/filterTournaments\('(.*)'\)/)[1];
            btn.removeAttribute('onclick');
            btn.addEventListener('click', () => this.filterTournaments(status));
        });
        
        // Match filters
        const matchFilters = document.querySelectorAll('[onclick*="filterMatches"]');
        matchFilters.forEach(btn => {
            const status = btn.getAttribute('onclick').match(/filterMatches\('(.*)'\)/)[1];
            btn.removeAttribute('onclick');
            btn.addEventListener('click', () => this.filterMatches(status));
        });
        
        // Player sort buttons
        const playerSorts = document.querySelectorAll('[onclick*="sortPlayers"]');
        playerSorts.forEach(btn => {
            const sortBy = btn.getAttribute('onclick').match(/sortPlayers\('(.*)'\)/)[1];
            btn.removeAttribute('onclick');
            btn.addEventListener('click', () => this.sortPlayers(sortBy));
        });
    }
    
    setupCardEffects() {
        // Add hover effects to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', this.onCardHover);
            card.addEventListener('mouseleave', this.onCardLeave);
        });
        
        // Add click effects to status items
        const statusItems = document.querySelectorAll('.status-item');
        statusItems.forEach(item => {
            item.addEventListener('click', this.onStatusItemClick);
        });
    }
    
    setupResponsiveBehavior() {
        // Handle responsive navigation
        window.addEventListener('resize', this.onWindowResize.bind(this));
        
        // Setup mobile-friendly interactions
        if (window.innerWidth <= 768) {
            this.setupMobileInteractions();
        }
    }
    
    onCardHover(event) {
        const card = event.currentTarget;
        card.style.transform = 'translateY(-5px)';
        card.style.boxShadow = '0 12px 35px rgba(0, 0, 0, 0.3)';
    }
    
    onCardLeave(event) {
        const card = event.currentTarget;
        card.style.transform = 'translateY(0)';
        card.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    }
    
    onStatusItemClick(event) {
        const item = event.currentTarget;
        item.classList.add('success-pulse');
        setTimeout(() => {
            item.classList.remove('success-pulse');
        }, 1000);
    }
    
    onWindowResize() {
        if (window.innerWidth <= 768) {
            this.setupMobileInteractions();
        } else {
            this.removeMobileInteractions();
        }
    }
    
    setupMobileInteractions() {
        // Make cards tappable on mobile
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.cursor = 'pointer';
        });
    }
    
    removeMobileInteractions() {
        // Remove mobile-specific interactions
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.cursor = 'default';
        });
    }
    
    async refreshData() {
        if (this.isRefreshing) {
            console.log('Refresh already in progress');
            return;
        }
        
        this.isRefreshing = true;
        const refreshBtn = document.querySelector('.btn[onclick*="refreshData"], .btn i.fa-sync').closest('.btn');
        
        try {
            // Add loading state
            if (refreshBtn) {
                refreshBtn.classList.add('loading');
                const icon = refreshBtn.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-sync');
                    icon.classList.add('fa-spinner', 'fa-spin');
                }
            }
            
            console.log('Refreshing dashboard data...');
            
            // Fetch updated statistics
            const response = await fetch('/api/stats');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.updateStatistics(data);
            this.updateLastUpdateTime();
            
            // Show success feedback
            this.showNotification('Data refreshed successfully!', 'success');
            
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showNotification('Failed to refresh data. Please try again.', 'error');
        } finally {
            // Remove loading state
            if (refreshBtn) {
                refreshBtn.classList.remove('loading');
                const icon = refreshBtn.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-spinner', 'fa-spin');
                    icon.classList.add('fa-sync');
                }
            }
            
            this.isRefreshing = false;
        }
    }
    
    updateStatistics(data) {
        // Update individual stat elements
        const statElements = {
            'total-players': data.total_players || 0,
            'total-tournaments': data.total_tournaments || 0,
            'total-matches': data.total_matches || 0,
            'active-tournaments': data.active_tournaments || 0,
            'completed-matches': data.completed_matches || 0,
            'pending-matches': data.pending_matches || 0
        };
        
        Object.entries(statElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateNumberUpdate(element, parseInt(element.textContent) || 0, value);
            }
        });
    }
    
    animateNumberUpdate(element, startValue, endValue) {
        const duration = 1000; // 1 second
        const startTime = performance.now();
        
        const updateNumber = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const currentValue = Math.round(startValue + (endValue - startValue) * easeOutCubic);
            
            element.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        
        requestAnimationFrame(updateNumber);
    }
    
    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('last-update');
        if (lastUpdateElement) {
            this.lastUpdateTime = new Date();
            lastUpdateElement.textContent = 'Just now';
            
            // Start countdown timer
            this.startUpdateTimeCountdown();
        }
    }
    
    startUpdateTimeCountdown() {
        const lastUpdateElement = document.getElementById('last-update');
        if (!lastUpdateElement) return;
        
        const updateTimeDisplay = () => {
            const now = new Date();
            const diffSeconds = Math.floor((now - this.lastUpdateTime) / 1000);
            
            if (diffSeconds < 60) {
                lastUpdateElement.textContent = `${diffSeconds} seconds ago`;
            } else if (diffSeconds < 3600) {
                const minutes = Math.floor(diffSeconds / 60);
                lastUpdateElement.textContent = `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
            } else {
                const hours = Math.floor(diffSeconds / 3600);
                lastUpdateElement.textContent = `${hours} hour${hours > 1 ? 's' : ''} ago`;
            }
        };
        
        // Update every 10 seconds
        setInterval(updateTimeDisplay, 10000);
    }
    
    startAutoRefresh() {
        this.autoRefreshTimer = setInterval(() => {
            this.refreshData();
        }, this.refreshInterval);
        
        console.log(`Auto-refresh started (every ${this.refreshInterval / 1000} seconds)`);
    }
    
    stopAutoRefresh() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
            this.autoRefreshTimer = null;
            console.log('Auto-refresh stopped');
        }
    }
    
    filterTournaments(status) {
        const tournamentCards = document.querySelectorAll('.tournament-card');
        
        tournamentCards.forEach(card => {
            const shouldShow = status === 'all' || card.dataset.status === status;
            
            if (shouldShow) {
                card.style.display = 'block';
                card.style.opacity = '0';
                setTimeout(() => {
                    card.style.opacity = '1';
                }, 50);
            } else {
                card.style.opacity = '0';
                setTimeout(() => {
                    card.style.display = 'none';
                }, 300);
            }
        });
        
        this.updateFilterButtonState(event.target);
        this.showNotification(`Filtered tournaments by: ${status}`, 'info');
    }
    
    filterMatches(status) {
        const matchCards = document.querySelectorAll('.match-card');
        
        matchCards.forEach(card => {
            const shouldShow = status === 'all' || card.dataset.status === status;
            
            if (shouldShow) {
                card.style.display = 'block';
                card.style.opacity = '0';
                setTimeout(() => {
                    card.style.opacity = '1';
                }, 50);
            } else {
                card.style.opacity = '0';
                setTimeout(() => {
                    card.style.display = 'none';
                }, 300);
            }
        });
        
        this.updateFilterButtonState(event.target);
        this.showNotification(`Filtered matches by: ${status}`, 'info');
    }
    
    sortPlayers(sortBy) {
        const playerCards = Array.from(document.querySelectorAll('.player-card'));
        
        if (playerCards.length === 0) return;
        
        playerCards.sort((a, b) => {
            const aValue = parseFloat(a.dataset[sortBy]) || 0;
            const bValue = parseFloat(b.dataset[sortBy]) || 0;
            return bValue - aValue; // Descending order
        });
        
        const container = playerCards[0].parentElement.parentElement;
        
        // Fade out
        playerCards.forEach(card => {
            card.style.opacity = '0';
        });
        
        setTimeout(() => {
            // Re-arrange and update positions
            container.innerHTML = '';
            playerCards.forEach((card, index) => {
                const badge = card.querySelector('.badge');
                if (badge) {
                    badge.textContent = `#${index + 1}`;
                }
                container.appendChild(card.parentElement);
                
                // Fade in with delay
                setTimeout(() => {
                    card.style.opacity = '1';
                }, index * 50);
            });
        }, 300);
        
        this.updateFilterButtonState(event.target);
        this.showNotification(`Sorted players by: ${sortBy}`, 'info');
    }
    
    updateFilterButtonState(activeButton) {
        // Remove active state from all buttons in the same group
        const buttonGroup = activeButton.closest('.btn-group');
        if (buttonGroup) {
            buttonGroup.querySelectorAll('.btn').forEach(btn => {
                btn.classList.remove('active');
            });
        }
        
        // Add active state to clicked button
        activeButton.classList.add('active');
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${this.getNotificationIcon(type)} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 3000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    initializeTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Public API methods
    destroy() {
        this.stopAutoRefresh();
        console.log('Tournament Dashboard destroyed');
    }
    
    setRefreshInterval(interval) {
        this.refreshInterval = interval;
        this.stopAutoRefresh();
        this.startAutoRefresh();
    }
}

// Global functions for backward compatibility
function refreshData() {
    if (window.tournamentDashboard) {
        window.tournamentDashboard.refreshData();
    }
}

function filterTournaments(status) {
    if (window.tournamentDashboard) {
        window.tournamentDashboard.filterTournaments(status);
    }
}

function filterMatches(status) {
    if (window.tournamentDashboard) {
        window.tournamentDashboard.filterMatches(status);
    }
}

function sortPlayers(sortBy) {
    if (window.tournamentDashboard) {
        window.tournamentDashboard.sortPlayers(sortBy);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.tournamentDashboard = new TournamentDashboard();
});

// Handle page visibility changes to pause/resume auto-refresh
document.addEventListener('visibilitychange', function() {
    if (window.tournamentDashboard) {
        if (document.hidden) {
            window.tournamentDashboard.stopAutoRefresh();
        } else {
            window.tournamentDashboard.startAutoRefresh();
            // Refresh immediately when page becomes visible
            window.tournamentDashboard.refreshData();
        }
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    if (window.tournamentDashboard) {
        // Ctrl+R or F5 to refresh
        if ((event.ctrlKey && event.key === 'r') || event.key === 'F5') {
            event.preventDefault();
            window.tournamentDashboard.refreshData();
        }
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TournamentDashboard;
}
