// API Configuration
const API_BASE_URL = 'http://localhost:5002';

// DOM Elements
const projectsContainer = document.getElementById('projectsContainer');
const projectDetails = document.getElementById('projectDetails');
const addProjectBtn = document.getElementById('addProjectBtn');
const saveProjectBtn = document.getElementById('saveProjectBtn');
const projectSearch = document.getElementById('projectSearch');
const searchBtn = document.getElementById('searchBtn');
const filterOptions = document.querySelectorAll('.filter-option');
const activeFilters = document.getElementById('activeFilters');
const filterInput = document.getElementById('filterInput');
const addFilterBtn = document.getElementById('addFilterBtn');
const selectedFilters = document.getElementById('selectedFilters');
const applyFiltersBtn = document.getElementById('applyFiltersBtn');
const matchAllFilters = document.getElementById('matchAllFilters');

// Chat elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendMessageBtn = document.getElementById('sendMessageBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const chatExampleLinks = document.querySelectorAll('.chat-example-link');

// Bootstrap modal instances
let addProjectModal;
let filterModal;

// Current filter state
let currentFilters = {
    type: null,
    values: [],
    matchAll: true
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Bootstrap modals
    addProjectModal = new bootstrap.Modal(document.getElementById('addProjectModal'));
    filterModal = new bootstrap.Modal(document.getElementById('filterModal'));
    
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
    
    // Filter options - show the filter modal
    filterOptions.forEach(option => {
        option.addEventListener('click', (e) => {
            const filterType = e.target.dataset.filter;
            
            // Set filter modal title and label based on the selected filter type
            const filterModalLabel = document.getElementById('filterModalLabel');
            const filterInputLabel = document.getElementById('filterInputLabel');
            
            // Clear any previous filter values
            selectedFilters.innerHTML = '';
            filterInput.value = '';
            
            // Check if we're reopening the same filter type
            if (currentFilters.type === filterType && currentFilters.values.length > 0) {
                // Restore existing filter values
                currentFilters.values.forEach(value => {
                    // Add to the UI
                    const filterTag = document.createElement('div');
                    filterTag.className = 'filter-tag';
                    filterTag.innerHTML = `
                        ${value}
                        <span class="remove-tag" data-value="${value}">&times;</span>
                    `;
                    
                    // Add click handler to remove button
                    const removeBtn = filterTag.querySelector('.remove-tag');
                    removeBtn.addEventListener('click', (e) => {
                        const valueToRemove = e.target.dataset.value;
                        // Remove from UI
                        e.target.parentElement.remove();
                        // Remove from array
                        currentFilters.values = currentFilters.values.filter(v => v !== valueToRemove);
                    });
                    
                    selectedFilters.appendChild(filterTag);
                });
                
                // Set the match all checkbox based on current state
                matchAllFilters.checked = currentFilters.matchAll;
            } else {
                // Set the filter type and reset values
                currentFilters.type = filterType;
                currentFilters.values = [];
                
                // Reset the match all checkbox
                matchAllFilters.checked = true;
            }
            
            // Update modal title and label based on filter type
            switch(filterType) {
                case 'tags':
                    filterModalLabel.textContent = 'Filter by Tags';
                    filterInputLabel.textContent = 'Enter tag to filter by:';
                    break;
                case 'category':
                    filterModalLabel.textContent = 'Filter by Category';
                    filterInputLabel.textContent = 'Enter category to filter by:';
                    break;
                case 'owner':
                    filterModalLabel.textContent = 'Filter by Owner';
                    filterInputLabel.textContent = 'Enter owner to filter by:';
                    break;
                default:
                    filterModalLabel.textContent = `Filter by ${filterType}`;
                    filterInputLabel.textContent = `Enter ${filterType} to filter by:`;
            }
            
            // Show the filter modal
            filterModal.show();
        });
    });
    
    // Add filter value when Enter is pressed in the filter input
    filterInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            addFilterValue();
        }
    });
    
    // Add filter button
    addFilterBtn.addEventListener('click', addFilterValue);
    
    // Apply filters button
    applyFiltersBtn.addEventListener('click', () => {
        if (currentFilters.values.length > 0) {
            // Save match all setting
            currentFilters.matchAll = matchAllFilters.checked;
            
            // Apply the filters
            applyFilters();
            
            // Hide the modal
            filterModal.hide();
        } else {
            alert('Please add at least one filter value.');
        }
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

// Add a filter value to the selected filters
function addFilterValue() {
    const value = filterInput.value.trim();
    
    if (value && !currentFilters.values.includes(value)) {
        // Add to the currentFilters values array
        currentFilters.values.push(value);
        
        // Add to the UI
        const filterTag = document.createElement('div');
        filterTag.className = 'filter-tag';
        filterTag.innerHTML = `
            ${value}
            <span class="remove-tag" data-value="${value}">&times;</span>
        `;
        
        // Add click handler to remove button
        const removeBtn = filterTag.querySelector('.remove-tag');
        removeBtn.addEventListener('click', (e) => {
            const valueToRemove = e.target.dataset.value;
            // Remove from UI
            e.target.parentElement.remove();
            // Remove from array
            currentFilters.values = currentFilters.values.filter(v => v !== valueToRemove);
        });
        
        selectedFilters.appendChild(filterTag);
        filterInput.value = '';
    }
}

// Apply the current filters
function applyFilters() {
    // Clear any existing active filters display
    activeFilters.innerHTML = '';
    
    // If we have filters, show them
    if (currentFilters.values.length > 0) {
        // Show the active filters container
        activeFilters.style.display = 'flex';
        
        // Create an active filter display
        const activeFilter = document.createElement('div');
        activeFilter.className = 'active-filter';
        
        // Format the filter label based on type
        let filterLabel = '';
        switch(currentFilters.type) {
            case 'tags': filterLabel = 'Tags'; break;
            case 'category': filterLabel = 'Category'; break;
            case 'owner': filterLabel = 'Owner'; break;
            default: filterLabel = currentFilters.type;
        }
        
        // Match type text
        const matchType = currentFilters.matchAll ? 'All of' : 'Any of';
        
        activeFilter.innerHTML = `
            <span class="filter-label">${filterLabel}:</span>
            <span class="match-type">${matchType}</span>
            <span class="filter-values">${currentFilters.values.join(', ')}</span>
            <span class="remove-filter" title="Remove filter">&times;</span>
        `;
        
        // Add click handler to remove filter button
        const removeFilterBtn = activeFilter.querySelector('.remove-filter');
        removeFilterBtn.addEventListener('click', () => {
            // Clear filters and reload all projects
            clearFilters();
        });
        
        activeFilters.appendChild(activeFilter);
        
        // Load filtered projects
        loadFilteredProjects();
    }
}

// Clear all filters
function clearFilters() {
    // Reset filter state
    currentFilters = {
        type: null,
        values: [],
        matchAll: true
    };
    
    // Clear UI
    activeFilters.innerHTML = '';
    activeFilters.style.display = 'none';
    
    // Reload all projects
    loadProjects();
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
async function loadFilteredProjects() {
    try {
        showLoading();
        
        // Construct filter query parameters
        const filterType = currentFilters.type;
        const filterValues = currentFilters.values.join(',');
        const matchAll = currentFilters.matchAll;
        
        // Build URL with filter parameters
        const url = `${API_BASE_URL}/projects?${filterType}=${encodeURIComponent(filterValues)}&match_all=${matchAll}`;
        
        console.log(`Loading filtered projects with URL: ${url}`);
        
        const response = await fetch(url);
        
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
    
    // Format description display
    const descriptionText = project.description || 'No description';
    const descriptionClass = project.description ? 'detail-value' : 'detail-value text-muted fst-italic';
    
    projectDetails.innerHTML = `
        <h3>${project.name || 'Untitled Project'}</h3>
        
        <div class="detail-section">
            <div class="detail-label d-flex justify-content-between align-items-center">
                Description:
                <button class="btn btn-sm btn-primary" onclick="editProjectDescription('${project.id}', '${(project.description || '').replace(/'/g, "\\'")}')" title="Add/Edit Description">
                    <i class="fas fa-edit"></i> Edit Description
                </button>
            </div>
            <div id="project-description-value" class="${descriptionClass}">${descriptionText}</div>
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
        // Ensure category is sent as an array
        category: category ? [category] : [], 
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
    // Find the project data
    const projectItem = document.querySelector(`.project-item[data-project-id="${projectId}"]`);
    if (!projectItem) {
        alert('Project not found!');
        return;
    }
    
    // Get current project data
    const projectTitle = projectItem.querySelector('.project-title').textContent;
    const projectDescription = projectItem.querySelector('.project-description').textContent;
    const projectOwner = projectItem.querySelector('.project-owner').textContent.replace('Owner: ', '');
    
    // Get category and tags (this is simplified, you might need to adjust based on your data structure)
    let projectCategory = '';
    const categoryEl = projectItem.querySelector('.project-category');
    if (categoryEl) {
        projectCategory = categoryEl.textContent;
    }
    
    let projectTags = '';
    const tagEls = projectItem.querySelectorAll('.tag');
    if (tagEls.length > 0) {
        const tags = Array.from(tagEls).map(tag => tag.textContent);
        projectTags = tags.join(',');
    }
    
    // Fill the form with project data
    document.getElementById('projectName').value = projectTitle;
    document.getElementById('projectDescription').value = projectDescription !== 'No description' ? projectDescription : '';
    document.getElementById('projectCategory').value = projectCategory;
    document.getElementById('projectTags').value = projectTags;
    document.getElementById('projectOwner').value = projectOwner !== 'Unknown' ? projectOwner : '';
    
    // Change the modal title
    document.getElementById('addProjectModalLabel').textContent = 'Edit Project';
    
    // Change the save button handler to update instead of create
    const saveBtn = document.getElementById('saveProjectBtn');
    // Remove existing event listeners
    const newSaveBtn = saveBtn.cloneNode(true);
    saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
    
    // Add new event listener for updating
    newSaveBtn.addEventListener('click', () => updateProject(projectId));
    
    // Show the modal
    addProjectModal.show();
}

// Update an existing project
async function updateProject(projectId) {
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
        // Ensure category is sent as an array
        category: category ? [category] : [],
        tags: tagsString ? tagsString.split(',').map(tag => tag.trim()) : [],
        owner
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
            method: 'PUT',
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
        
        // Reset the modal title and button handler
        document.getElementById('addProjectModalLabel').textContent = 'Add New Project';
        const saveBtn = document.getElementById('saveProjectBtn');
        const newSaveBtn = saveBtn.cloneNode(true);
        saveBtn.parentNode.replaceChild(newSaveBtn, saveBtn);
        newSaveBtn.addEventListener('click', saveProject);
        
        // Reload projects to show the updated data
        loadProjects();
        
    } catch (error) {
        alert('Failed to update project. Please try again.');
        console.error('Error updating project:', error);
    }
}

// Edit project description
function editProjectDescription(projectId, currentDescription) {
    // Create a modal for editing the description
    const descriptionModal = document.createElement('div');
    descriptionModal.className = 'modal fade';
    descriptionModal.id = 'descriptionEditModal';
    descriptionModal.setAttribute('tabindex', '-1');
    descriptionModal.setAttribute('aria-labelledby', 'descriptionEditModalLabel');
    descriptionModal.setAttribute('aria-hidden', 'true');
    
    // Create the modal content
    descriptionModal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="descriptionEditModalLabel">Edit Description</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="projectDescriptionEdit" class="form-label">Description</label>
                        <textarea class="form-control" id="projectDescriptionEdit" rows="4">${currentDescription || ''}</textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="saveDescriptionBtn">Save</button>
                </div>
            </div>
        </div>
    `;
    
    // Add the modal to the document
    document.body.appendChild(descriptionModal);
    
    // Initialize the modal
    const modal = new bootstrap.Modal(descriptionModal);
    modal.show();
    
    // Add event listener for the save button
    document.getElementById('saveDescriptionBtn').addEventListener('click', async () => {
        const newDescription = document.getElementById('projectDescriptionEdit').value.trim();
        
        try {
            // Update the project in the database
            await updateProjectDescription(projectId, newDescription);
            
            // Update the UI
            const descriptionElement = document.getElementById('project-description-value');
            descriptionElement.textContent = newDescription || 'No description';
            
            // Update the class based on whether there's a description
            if (newDescription) {
                descriptionElement.classList.remove('text-muted', 'fst-italic');
            } else {
                descriptionElement.classList.add('text-muted', 'fst-italic');
            }
            
            // Close the modal
            modal.hide();
            
            // Remove the modal element after it's hidden
            descriptionModal.addEventListener('hidden.bs.modal', () => {
                document.body.removeChild(descriptionModal);
            });
            
        } catch (error) {
            alert('Failed to update description. Please try again.');
            console.error('Error updating description:', error);
        }
    });
    
    // Remove the modal element when it's closed
    descriptionModal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(descriptionModal);
    });
}

// Update project description in database
async function updateProjectDescription(projectId, description) {
    try {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ description })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error updating project description:', error);
        throw error;
    }
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

// Send a message to the chat
async function sendChatMessage(message) {
    try {
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message to API
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
        
        // Remove typing indicator before adding response
        removeTypingIndicator();
        
        // Add response to chat
        addMessageToChat('bot', data.response);
        
        // If the response includes projects, display them
        if (data.projects && data.projects.length > 0) {
            // Display projects in the main list
            displayProjects(data.projects);
            
            // Add project data as a structured message in chat
            addProjectDataToChat(data.formatted_projects);
            
            // If filters were applied, update the UI to show active filters
            if (data.filters_applied) {
                // Update current filters
                currentFilters = {
                    type: Object.keys(data.filters_applied)[0], // Get the first filter type
                    values: data.filters_applied[Object.keys(data.filters_applied)[0]], // Get values for that type
                    matchAll: data.match_all !== undefined ? data.match_all : true // Get match_all value or default to true
                };
                
                // Clear any existing active filters
                activeFilters.innerHTML = '';
                
                // Create an active filter display element
                const activeFilter = document.createElement('div');
                activeFilter.className = 'active-filter';
                
                // Format filter label
                let filterLabel = '';
                switch(currentFilters.type) {
                    case 'tags': filterLabel = 'Tags'; break;
                    case 'category': filterLabel = 'Category'; break;
                    case 'owner': filterLabel = 'Owner'; break;
                    default: filterLabel = currentFilters.type;
                }
                
                // Match type text
                const matchType = currentFilters.matchAll ? 'All of' : 'Any of';
                
                // Create UI element
                activeFilter.innerHTML = `
                    <span class="filter-label">${filterLabel}:</span>
                    <span class="match-type">${matchType}</span>
                    <span class="filter-values">${currentFilters.values.join(', ')}</span>
                    <span class="remove-filter" title="Remove filter">&times;</span>
                `;
                
                // Add click handler
                const removeFilterBtn = activeFilter.querySelector('.remove-filter');
                removeFilterBtn.addEventListener('click', () => {
                    clearFilters();
                });
                
                // Show active filters
                activeFilters.appendChild(activeFilter);
                activeFilters.style.display = 'flex';
            }
        }
        
    } catch (error) {
        // Remove typing indicator in case of error
        removeTypingIndicator();
        
        // Add error message to chat
        addMessageToChat('bot', 'Sorry, I encountered an error while processing your request.');
        console.error('Error sending chat message:', error);
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