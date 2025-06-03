class DriverTracker {
    constructor() {
        this.socket = null;
        this.map = null;
        this.markers = {};
        this.drivers = {};
        
        this.initializeMap();
        this.initializeSocket();
        this.setupEventListeners();
        this.loadDrivers();
        
        setInterval(() => this.loadDrivers(), 30000);
    }
    
    initializeMap() {
        this.map = L.map('map').setView([0, 0], 2);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        this.driverIcon = L.divIcon({
            className: 'driver-marker',
            html: '🚚',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
    }
    
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('location_update', (data) => {
            console.log('Location update received:', data);
            this.updateDriverLocation(data.driver_id, data.location);
            this.updateLastUpdateTime();
        });
    }
    
    setupEventListeners() {
        document.getElementById('generateLink').addEventListener('click', () => {
            this.generateTrackingLink();
        });
    }
    
    async loadDrivers() {
        try {
            const response = await fetch('/api/all-drivers');
            const drivers = await response.json();
            
            this.updateDriverList(drivers);
            this.updateMapMarkers(drivers);
        } catch (error) {
            console.error('Error loading drivers:', error);
        }
    }
    
    updateDriverList(drivers) {
        const driverList = document.getElementById('driverList');
        
        if (drivers.length === 0) {
            driverList.innerHTML = '<p style="color: #6c757d; text-align: center;">No active drivers</p>';
            return;
        }
        
        driverList.innerHTML = drivers.map(driver => {
            const isOnline = driver.latitude !== null;
            const statusClass = isOnline ? 'status-online' : 'status-offline';
            const statusText = isOnline ? 'Online' : 'Offline';
            const lastUpdate = driver.last_update ? 
                new Date(driver.last_update).toLocaleTimeString() : 'Never';
            
            return `
                <div class="driver-item ${isOnline ? 'active' : 'inactive'}" 
                     data-driver-id="${driver.driver_id}">
                    <div class="driver-name">${driver.username}</div>
                    <div class="driver-id">${driver.driver_id}</div>
                    <div class="driver-status">
                        <span class="${statusClass}">● ${statusText}</span>
                        <span>${lastUpdate}</span>
                    </div>
                </div>
            `;
        }).join('');
        
        driverList.querySelectorAll('.driver-item').forEach(item => {
            item.addEventListener('click', () => {
                const driverId = item.dataset.driverId;
                const driver = drivers.find(d => d.driver_id === driverId);
                if (driver && driver.latitude) {
                    this.map.setView([driver.latitude, driver.longitude], 15);
                    
                    if (this.markers[driverId]) {
                        this.markers[driverId].openPopup();
                    }
                }
            });
        });
    }
    
    updateMapMarkers(drivers) {
        Object.values(this.markers).forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = {};
        
        drivers.forEach(driver => {
            if (driver.latitude && driver.longitude) {
                const marker = L.marker([driver.latitude, driver.longitude], {
                    icon: this.driverIcon
                }).addTo(this.map);
                
                const lastUpdate = driver.last_update ? 
                    new Date(driver.last_update).toLocaleString() : 'Unknown';
                
                marker.bindPopup(`
                    <div class="popup-driver-info">
                        <div class="popup-driver-name">${driver.username}</div>
                        <div class="popup-driver-time">Last update: ${lastUpdate}</div>
                    </div>
                `);
                
                this.markers[driver.driver_id] = marker;
            }
        });
        
        if (Object.keys(this.markers).length > 0) {
            const group = new L.featureGroup(Object.values(this.markers));
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }
    
    updateDriverLocation(driverId, location) {
        if (this.markers[driverId]) {
            this.markers[driverId].setLatLng([location.latitude, location.longitude]);
        } else {
            const marker = L.marker([location.latitude, location.longitude], {
                icon: this.driverIcon
            }).addTo(this.map);
            
            marker.bindPopup(`
                <div class="popup-driver-info">
                    <div class="popup-driver-name">Driver ${driverId.substring(0, 8)}...</div>
                    <div class="popup-driver-time">Just updated</div>
                </div>
            `);
            
            this.markers[driverId] = marker;
        }
        
        this.loadDrivers();
    }
    
    async generateTrackingLink() {
        const button = document.getElementById('generateLink');
        const originalText = button.textContent;
        
        button.innerHTML = '<span class="loading"></span> Generating...';
        button.disabled = true;
        
        try {
            const response = await fetch('/generate-link');
            const data = await response.json();
            
            this.displayGeneratedLink(data);
        } catch (error) {
            console.error('Error generating link:', error);
            alert('Failed to generate tracking link');
        } finally {
            button.textContent = originalText;
            button.disabled = false;
        }
    }
    
    displayGeneratedLink(data) {
        const linksContainer = document.getElementById('generatedLinks');
        
        const linkElement = document.createElement('div');
        linkElement.className = 'generated-link';
        linkElement.innerHTML = `
            <div class="link-url">${data.tracking_link}</div>
            <button class="copy-btn" onclick="navigator.clipboard.writeText('${data.tracking_link}')">Copy Link</button>
            <div style="font-size: 0.8em; color: #666; margin-top: 10px;">Driver ID: ${data.driver_id}</div>
        `;
        
        linksContainer.insertBefore(linkElement, linksContainer.firstChild);
        
        if (linksContainer.children.length > 5) {
            linksContainer.removeChild(linksContainer.lastChild);
        }
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        statusElement.textContent = connected ? '🟢 Connected' : '🔴 Disconnected';
    }
    
    updateLastUpdateTime() {
        const updateElement = document.getElementById('lastUpdate');
        updateElement.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DriverTracker();
}); 