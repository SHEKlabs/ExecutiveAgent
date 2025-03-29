// API Configuration
const API_BASE_URL = 'http://localhost:5001';

// DOM Elements
const projectsContainer = document.getElementById('projectsContainer');
const projectDetails = document.getElementById('projectDetails');
const addProjectBtn = document.getElementById('addProjectBtn');
const saveProjectBtn = document.getElementById('saveProjectBtn');
const projectSearch = document.getElementById('projectSearch');
const searchBtn = document.getElementById('searchBtn');
const filterOptions = document.querySelectorAll('.filter-option');

// Chat elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendMessageBtn = document.getElementById('sendMessageBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const chatExampleLinks = document.querySelectorAll('.chat-example-link');

// Bootstrap modal instance
let addProjectModal;

// Current filter state
let currentFilter = {
    type: null,
    value: null
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Bootstrap modal
    addProjectModal = new bootstrap.Modal(document.getElementById('addProjectModal'));
    
    // Load all projects when the page loads
    loadProjects();
    
    // Set up event listeners
    setupEventListeners();
});

// Set up all event listeners
function setupEventListeners() {
    // Add project button
    addProjectBtn.addEventListener('click', () => {
        // Clear form fields
        document.getElementById('addProjectForm').reset();
        // Show modal
        addProjectModal.show();
    });
    
    // Save project button
    saveProjectBtn.addEventListener('click', saveProject);
    
    // Search button
    searchBtn.addEventListener('click', () => {
        const searchTerm = projectSearch.value.trim();
        if (searchTerm) {
            searchProjects(searchTerm);
        } else {
            loadProjects();
        }
    });
    
    // Search input - search on Enter key
    projectSearch.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });
    
    // Filter options
    filterOptions.forEach(option => {
        option.addEventListener('click', (e) => {
            const filterType = e.target.dataset.filter;
            const filterValue = prompt(`Enter ${filterType} to filter by:`);
            
            if (filterValue && filterValue.trim()) {
                currentFilter = {
                    type: filterType,
                    value: filterValue.trim()
                };
                loadFilteredProjects(filterType, filterValue.trim());
            }
        });
    });
    
    // Chat input - send on Enter key
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            sendMessageBtn.click();
        }
    });
    
    // Send message button
    sendMessageBtn.addEventListener('click', () => {
        const message = chatInput.value.trim();
        if (message) {
            sendChatMessage(message);
            chatInput.value = '';
        }
    });
    
    // Clear chat button
    clearChatBtn.addEventListener('click', () => {
        // Clear all messages except the welcome message
        const welcomeMessage = chatMessages.querySelector('.bot-message');
        chatMessages.innerHTML = '';
        chatMessages.appendChild(welcomeMessage);
    });
    
    // Chat example links
    chatExampleLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const exampleText = link.textContent;
            chatInput.value = exampleText;
            sendMessageBtn.click();
        });
    });
}

// Load all projects
async function loadProjects() {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE_URL}/projects`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const projects = await response.json();
        displayProjects(projects);
        
    } catch (error) {
        showError('Failed to load projects. Please try again later.');
        console.error('Error loading projects:', error);
    }
}

// Load filtered projects
async function loadFilteredProjects(filterType, filterValue) {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE_URL}/projects?${filterType}=${encodeURIComponent(filterValue)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const projects = await response.json();
        displayProjects(projects);
        
    } catch (error) {
        showError('Failed to load filtered projects. Please try again later.');
        console.error('Error loading filtered projects:', error);
    }
}

// Search projects (client-side filtering)
function searchProjects(searchTerm) {
    // Get all project items
    const projectItems = document.querySelectorAll('.list-group-item');
    searchTerm = searchTerm.toLowerCase();
    
    // Filter projects based on search term
    projectItems.forEach(item => {
        const projectTitle = item.querySelector('.project-title').textContent.toLowerCase();
        const projectDescription = item.querySelector('.project-description')?.textContent.toLowerCase() || '';
        
        if (projectTitle.includes(searchTerm) || projectDescription.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Display projects in the UI
function displayProjects(projects) {
    projectsContainer.innerHTML = '';
    
    if (!projects || projects.length === 0) {
        projectsContainer.innerHTML = '<p class="text-center py-4">No projects found.</p>';
        return;
    }
    
    projects.forEach(project => {
        const projectItem = document.createElement('div');
        projectItem.className = 'list-group-item project-item';
        projectItem.dataset.projectId = project.id;
        
        // Create tags HTML
        let tagsHtml = '';
        if (project.tags && project.tags.length > 0) {
            tagsHtml = project.tags.map(tag => `<span class="tag">${tag}</span>`).join('');
        }
        
        // Get project name and description, with fallbacks
        const projectName = project.name || 'Untitled Project';
        const projectDescription = project.description || 'No description';
        
        // Get project category (could be string or array)
        let categoryDisplay = '';
        if (project.category) {
            if (Array.isArray(project.category)) {
                categoryDisplay = project.category.map(cat => 
                    `<span class="project-category">${cat}</span>`).join(' ');
            } else {
                categoryDisplay = `<span class="project-category">${project.category}</span>`;
            }
        }
        
        projectItem.innerHTML = `
            <div class="project-title">${projectName}</div>
            <div class="project-description text-truncate">${projectDescription}</div>
            <div class="mt-2">
                ${categoryDisplay}
                <div class="mt-1">${tagsHtml}</div>
            </div>
            <div class="project-owner">Owner: ${project.owner || 'Unknown'}</div>
        `;
        
        // Add click event to show project details
        projectItem.addEventListener('click', () => {
            // Remove active class from all items
            document.querySelectorAll('.project-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Add active class to clicked item
            projectItem.classList.add('active');
            
            // Show project details
            showProjectDetails(project);
        });
        
        projectsContainer.appendChild(projectItem);
    });
}

// Show project details in the sidebar
function showProjectDetails(project) {
    // Create tags HTML
    const tagsHtml = project.tags && project.tags.length > 0 
        ? project.tags.map(tag => `<span class="tag">${tag}</span>`).join('') 
        : 'No tags';
    
    // Create category HTML - handle both string and array
    let categoryHtml = 'Uncategorized';
    if (project.category) {
        if (Array.isArray(project.category)) {
            categoryHtml = project.category.map(cat => 
                `<span class="project-category">${cat}</span>`).join(' ');
        } else {
            categoryHtml = `<span class="project-category">${project.category}</span>`;
        }
    }
    
    projectDetails.innerHTML = `
        <h3>${project.name || 'Untitled Project'}</h3>
        
        <div class="detail-section">
            <div class="detail-label">Description:</div>
            <div class="detail-value">${project.description || 'No description'}</div>
        </div>
        
        <div class="detail-section">
            <div class="detail-label">Category:</div>
            <div class="detail-value">${categoryHtml}</div>
        </div>
        
        <div class="detail-section">
            <div class="detail-label">Tags:</div>
            <div class="detail-value">${tagsHtml}</div>
        </div>
        
        <div class="detail-section">
            <div class="detail-label">Owner:</div>
            <div class="detail-value">${project.owner || 'Unknown'}</div>
        </div>
        
        <div class="action-buttons">
            <button class="btn btn-sm btn-primary btn-action" onclick="editProject('${project.id}')">Edit</button>
            <button class="btn btn-sm btn-danger btn-action" onclick="deleteProject('${project.id}')">Delete</button>
        </div>
    `;
}

// Save a new project
async function saveProject() {
    // Get form values
    const name = document.getElementById('projectName').value.trim();
    const description = document.getElementById('projectDescription').value.trim();
    const category = document.getElementById('projectCategory').value.trim();
    const tagsString = document.getElementById('projectTags').value.trim();
    const owner = document.getElementById('projectOwner').value.trim();
    
    // Validate required fields
    if (!name) {
        alert('Project name is required!');
        return;
    }
    
    // Prepare project data
    const projectData = {
        name,
        description,
        category,
        tags: tagsString ? tagsString.split(',').map(tag => tag.trim()) : [],
        owner
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/projects`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(projectData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        // Close modal and reload projects
        addProjectModal.hide();
        loadProjects();
        
    } catch (error) {
        alert('Failed to save project. Please try again.');
        console.error('Error saving project:', error);
    }
}

// Edit an existing project
function editProject(projectId) {
    // This would be implemented to open the modal with project data
    alert('Edit functionality will be implemented in the next phase');
}

// Delete a project
async function deleteProject(projectId) {
    if (confirm('Are you sure you want to delete this project?')) {
        try {
            const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            // Reload projects and clear details
            loadProjects();
            projectDetails.innerHTML = '<p class="text-muted">Select a project to view details</p>';
            
        } catch (error) {
            alert('Failed to delete project. Please try again.');
            console.error('Error deleting project:', error);
        }
    }
}

// Show loading state
function showLoading() {
    projectsContainer.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading projects...</p>
        </div>
    `;
}

// Show error message
function showError(message) {
    projectsContainer.innerHTML = `
        <div class="error-message">
            <p>${message}</p>
        </div>
    `;
}

// Chat functionality
async function sendChatMessage(message) {
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Chat response data:", data);
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Process the response
        if (data.projects) {
            // If projects were returned, add a message and display them
            addMessageToChat('bot', data.response);
            
            // Use formatted_projects if available, otherwise use projects
            const projectsToDisplay = data.formatted_projects || data.projects;
            addProjectDataToChat(projectsToDisplay);
            
            // Also update the projects container with these results
            if (Array.isArray(data.projects)) {
                displayProjects(data.projects);
            }
        } else if (data.response) {
            // Otherwise just show the chatbot's response
            addMessageToChat('bot', data.response);
        } else if (data.error) {
            // Show error message
            addMessageToChat('bot', `Sorry, I encountered an error: ${data.error}`);
        }
        
    } catch (error) {
        // Remove typing indicator
        removeTypingIndicator();
        
        console.error('Error sending message:', error);
        addMessageToChat('bot', 'Sorry, I encountered an error while processing your request. Please try again.');
    }
}

function addMessageToChat(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Replace newlines with <br> tags for proper formatting
    const formattedContent = content.replace(/\n/g, '<br>');
    messageContent.innerHTML = `<p>${formattedContent}</p>`;
    
    // Add timestamp
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageContent.appendChild(timestamp);
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addProjectDataToChat(projectData) {
    if (typeof projectData === 'string') {
        // If projectData is already a formatted string
        const dataDiv = document.createElement('div');
        dataDiv.className = 'message bot-message';
        
        const dataContent = document.createElement('div');
        dataContent.className = 'message-content';
        
        const preElement = document.createElement('pre');
        preElement.className = 'project-data-message';
        preElement.textContent = projectData;
        
        dataContent.appendChild(preElement);
        dataDiv.appendChild(dataContent);
        chatMessages.appendChild(dataDiv);
    } else if (Array.isArray(projectData)) {
        // If projectData is an array of projects, format it nicely
        const formattedData = projectData.map((project, index) => {
            let projectStr = `Project ${index + 1}:\n`;
            
            // Define display order for fields
            const fieldOrder = [
                'name', 'description', 'category', 'owner', 'tags', 
                'contributors', 'connected_project'
            ];
            
            // First add fields in the preferred order
            for (const field of fieldOrder) {
                const value = project[field];
                if (value) {
                    const displayName = field.charAt(0).toUpperCase() + field.slice(1).replace('_', ' ');
                    
                    if (Array.isArray(value)) {
                        projectStr += `  ${displayName}: ${value.join(', ')}\n`;
                    } else {
                        projectStr += `  ${displayName}: ${value}\n`;
                    }
                }
            }
            
            // Then add any remaining fields
            for (const [key, value] of Object.entries(project)) {
                if (value && !fieldOrder.includes(key) && !['id', 'created_at', 'updated_at'].includes(key)) {
                    const displayName = key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ');
                    
                    if (Array.isArray(value)) {
                        projectStr += `  ${displayName}: ${value.join(', ')}\n`;
                    } else {
                        projectStr += `  ${displayName}: ${value}\n`;
                    }
                }
            }
            
            return projectStr;
        }).join('\n');
        
        addProjectDataToChat(formattedData);
    }
    
    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
} 