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
        
        projectItem.innerHTML = `
            <div class="project-title">${project.name || 'Untitled Project'}</div>
            <div class="project-description text-truncate">${project.description || 'No description'}</div>
            <div class="mt-2">
                ${project.category ? `<span class="project-category">${project.category}</span>` : ''}
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
    const tagsHtml = project.tags && project.tags.length > 0 
        ? project.tags.map(tag => `<span class="tag">${tag}</span>`).join('') 
        : 'No tags';
    
    projectDetails.innerHTML = `
        <h3>${project.name || 'Untitled Project'}</h3>
        
        <div class="detail-section">
            <div class="detail-label">Description:</div>
            <div class="detail-value">${project.description || 'No description'}</div>
        </div>
        
        <div class="detail-section">
            <div class="detail-label">Category:</div>
            <div class="detail-value">${project.category || 'Uncategorized'}</div>
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