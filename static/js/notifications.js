/**
 * Real-time Notification System for Vector Space
 * Handles WebSocket connections, real-time updates, and notification UI
 */

class NotificationManager {
    constructor() {
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 5000;
        this.unreadCount = 0;

        this.init();
    }

    init() {
        this.createNotificationButton();
        this.connectSocket();
        this.setupEventListeners();
        this.loadInitialNotifications();

        // Request notification permission for browser notifications
        this.requestNotificationPermission();
    }

    connectSocket() {
        if (!window.WebSocket) {
            console.warn('WebSockets not supported');
            return;
        }

        // Use secure WebSocket if HTTPS, otherwise regular WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;

        try {
            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = (event) => {
                console.log('Notification WebSocket connected');
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
            };

            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };

            this.socket.onclose = (event) => {
                console.log('Notification WebSocket disconnected');
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };

            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };

        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.connectSocket();
            }, this.reconnectInterval);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    handleMessage(data) {
        switch (data.type) {
            case 'new_notification':
                this.showNewNotification(data.notification);
                this.updateUnreadCount(this.unreadCount + 1);
                break;

            case 'notification_count':
                this.updateUnreadCount(data.count);
                break;

            case 'notifications_list':
                this.updateNotificationsList(data.notifications);
                break;
        }
    }

    showNewNotification(notification) {
        // Show browser notification if permission granted
        if (Notification.permission === 'granted') {
            const browserNotification = new Notification(notification.title, {
                body: notification.message,
                icon: '/static/images/logo.png',
                tag: notification.id
            });

            browserNotification.onclick = () => {
                window.focus();
                if (notification.link) {
                    window.location.href = notification.link;
                }
                browserNotification.close();
            };

            // Auto close after 5 seconds
            setTimeout(() => browserNotification.close(), 5000);
        }

        // Show in-app notification popup
        this.showNotificationPopup(notification);

        // Update UI elements
        this.addNotificationToUI(notification);
    }

    showNotificationPopup(notification) {
            // Remove existing popup if any
            const existingPopup = document.querySelector('.notification-popup');
            if (existingPopup) existingPopup.remove();

            // Create popup element
            const popup = document.createElement('div');
            popup.className = 'notification-popup';
            popup.innerHTML = `
            <div class="notification-header">
                <strong class="notification-title">${notification.title}</strong>
                <button type="button" class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    ×
                </button>
            </div>
            <div class="notification-message">${notification.message}</div>
            <div class="notification-actions">
                ${notification.action_url ? `<a href="${notification.action_url}" class="btn btn-primary btn-sm">Action</a>` : ''}
                ${notification.link ? `<a href="${notification.link}" class="btn btn-outline-primary btn-sm">View</a>` : ''}
                <button type="button" class="btn btn-outline-secondary btn-sm" onclick="this.parentElement.parentElement.remove()">
                    Dismiss
                </button>
            </div>
        `;
        
        // Add popup to page
        document.body.appendChild(popup);
        
        // Animate in
        setTimeout(() => popup.classList.add('show'), 100);
        
        // Auto remove after 8 seconds
        setTimeout(() => {
            if (popup.parentElement) {
                popup.classList.remove('show');
                setTimeout(() => popup.remove(), 300);
            }
        }, 8000);
    }
    
    addNotificationToUI(notification) {
        // Add to dropdown if it exists
        const dropdown = document.querySelector('.notification-dropdown');
        if (dropdown) {
            const item = this.createNotificationItem(notification, true);
            dropdown.insertBefore(item, dropdown.firstChild);
            
            // Remove oldest if too many
            const items = dropdown.querySelectorAll('.notification-item');
            if (items.length > 10) {
                items[items.length - 1].remove();
            }
        }
    }
    
    createNotificationItem(notification, isNew = false) {
        const item = document.createElement('div');
        item.className = `dropdown-item notification-item ${isNew ? 'notification-new' : ''}`;
        item.setAttribute('data-notification-id', notification.id);
        
        const icon = this.getNotificationIcon(notification.type);
        
        item.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="notification-icon me-2">
                    ${icon}
                </div>
                <div class="flex-grow-1">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message}</div>
                    <small class="text-muted">${this.formatTime(notification.created_at)}</small>
                </div>
            </div>
        `;
        
        // Add click handler
        item.addEventListener('click', () => {
            if (notification.link) {
                window.location.href = notification.link;
            }
        });
        
        return item;
    }
    
    createNotificationButton() {
        // Find existing notification button or create one
        let notificationBtn = document.querySelector('#notification-btn');
        
        if (!notificationBtn) {
            // Create notification button and add to navbar
            const navbar = document.querySelector('.navbar-nav');
            if (navbar) {
                const li = document.createElement('li');
                li.className = 'nav-item dropdown';
                li.innerHTML = `
                    <a class="nav-link dropdown-toggle position-relative" href="#" id="notification-btn" 
                       role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="bi bi-bell"></i>
                        <span class="notification-count badge bg-danger" style="display: none;">0</span>
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end notification-widget">
                        <li class="dropdown-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <span>Notifications</span>
                                <a href="/dashboard/notifications/" class="btn btn-link btn-sm p-0">View All</a>
                            </div>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <div class="notification-dropdown">
                            <li class="dropdown-item text-center text-muted">
                                No new notifications
                            </li>
                        </div>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <a class="dropdown-item text-center" href="/dashboard/notifications/">
                                <small>View all notifications</small>
                            </a>
                        </li>
                    </ul>
                `;
                navbar.appendChild(li);
                notificationBtn = li.querySelector('#notification-btn');
            }
        }
        
        this.notificationBtn = notificationBtn;
        this.notificationCountBadge = document.querySelector('.notification-count');
        this.notificationDropdown = document.querySelector('.notification-dropdown');
    }
    
    setupEventListeners() {
        // Mark notifications as read when dropdown is opened
        if (this.notificationBtn) {
            this.notificationBtn.addEventListener('click', () => {
                this.loadNotifications();
            });
        }
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.socket && this.socket.readyState !== WebSocket.OPEN) {
                this.connectSocket();
            }
        });
    }
    
    loadInitialNotifications() {
        // Load unread count
        fetch('/api/notifications/widget/')
            .then(response => response.json())
            .then(data => {
                this.updateUnreadCount(data.unread_count);
                this.updateNotificationsList(data.notifications);
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
            });
    }
    
    loadNotifications() {
        fetch('/api/notifications/widget/')
            .then(response => response.json())
            .then(data => {
                this.updateNotificationsList(data.notifications);
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
            });
    }
    
    updateUnreadCount(count) {
        this.unreadCount = count;
        
        if (this.notificationCountBadge) {
            if (count > 0) {
                this.notificationCountBadge.textContent = count > 99 ? '99+' : count;
                this.notificationCountBadge.style.display = 'flex';
            } else {
                this.notificationCountBadge.style.display = 'none';
            }
        }
        
        // Update page title with count
        this.updatePageTitle(count);
    }
    
    updatePageTitle(count) {
        const baseTitle = document.title.replace(/^\(\d+\)\s*/, '');
        document.title = count > 0 ? `(${count}) ${baseTitle}` : baseTitle;
    }
    
    updateNotificationsList(notifications) {
        if (!this.notificationDropdown) return;
        
        this.notificationDropdown.innerHTML = '';
        
        if (notifications.length === 0) {
            this.notificationDropdown.innerHTML = `
                <li class="dropdown-item text-center text-muted">
                    No new notifications
                </li>
            `;
        } else {
            notifications.forEach(notification => {
                const item = this.createNotificationItem(notification);
                this.notificationDropdown.appendChild(item);
            });
        }
    }
    
    updateConnectionStatus(connected) {
        // You can add visual indicators for connection status here
        const statusIndicator = document.querySelector('.connection-status');
        if (statusIndicator) {
            statusIndicator.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
        }
    }
    
    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                console.log('Notification permission:', permission);
            });
        }
    }
    
    getNotificationIcon(type) {
        const icons = {
            'purchase': '<i class="bi bi-cart-check text-success"></i>',
            'review': '<i class="bi bi-star-fill text-warning"></i>',
            'comment': '<i class="bi bi-chat-fill text-info"></i>',
            'follow': '<i class="bi bi-person-plus text-primary"></i>',
            'job_application': '<i class="bi bi-briefcase text-warning"></i>',
            'mentorship_request': '<i class="bi bi-person-workspace text-purple"></i>',
            'system': '<i class="bi bi-gear text-secondary"></i>',
            'welcome': '<i class="bi bi-hand-thumbs-up text-success"></i>',
        };
        
        return icons[type] || '<i class="bi bi-bell text-primary"></i>';
    }
    
    formatTime(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        
        return date.toLocaleDateString();
    }
    
    // Public methods for manual actions
    markAsRead(notificationId) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                action: 'mark_read',
                notification_id: notificationId
            }));
        }
    }
    
    markAllAsRead() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                action: 'mark_all_read'
            }));
        }
    }
    
    getNotifications() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                action: 'get_notifications'
            }));
        }
    }
}

// Initialize notification manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if user is authenticated
    if (document.querySelector('meta[name="user-authenticated"]')?.content === 'true' ||
        window.location.pathname.includes('/dashboard/')) {
        window.notificationManager = new NotificationManager();
    }
});

// Expose for global access
window.NotificationManager = NotificationManager;