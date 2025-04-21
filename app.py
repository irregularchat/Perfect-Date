import os
import gradio as gr
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from utilities.openai_tools import generate_date_ideas, is_openai_available, generate_event_ideas
from utilities.map_tools import is_maps_available

# Load environment variables
load_dotenv()

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "custom.css")
with open(css_path, "r") as f:
    custom_css = f.read()

# Add additional CSS for location input
custom_css += """
.location-input label {
    color: var(--primary-color) !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
}

.location-input textarea, .location-input input {
    border: 2px solid var(--primary-color) !important;
    background-color: #fff !important;
    color: #000 !important;
}

/* Dark mode overrides for location input */
@media (prefers-color-scheme: dark) {
    .location-input textarea, .location-input input {
        background-color: #374151 !important;
        color: #f9fafb !important;
        border-color: #818cf8 !important;
    }
    
    .location-input label {
        color: #818cf8 !important;
    }
    
    /* Fix for all input fields in dark mode */
    input, textarea, select {
        background-color: #374151 !important;
        color: #f9fafb !important;
        border-color: #4b5563 !important;
    }
    
    /* Make labels more visible */
    label {
        color: #e5e7eb !important;
    }
}
"""

# Add custom CSS for better rendering and dark mode compatibility
css = """
.timeline-output h2 {
    color: #4f46e5;
    border-bottom: 2px solid #818cf8;
    padding-bottom: 10px;
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 24px;
    font-weight: bold;
    display: block;
    width: 100%;
}

.timeline-item {
    margin-bottom: 30px;
}

.timeline-content {
    background-color: #f9fafb;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    color: #111827; /* Ensure dark text on light background */
}

.timeline-entry {
    margin-bottom: 12px;
    padding-left: 15px;
    border-left: 3px solid #4f46e5;
}

.map-output {
    width: 100%;
    height: 400px;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 20px;
}

.place-info {
    padding: 20px;
    background-color: #f9fafb;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    color: #111827; /* Ensure dark text on light background */
}

/* Place card styling */
.recommended-places-header h3 {
    color: #ff6b6b;
    font-size: 22px;
    font-weight: bold;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
    margin-top: 0;
    margin-bottom: 20px;
}

.place-card {
    margin-bottom: 25px;
    padding: 20px;
    border: 1px solid #eee;
    border-radius: 8px;
    background-color: #f9f9f9;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    color: #333; /* Ensure consistent text color */
}

.place-name {
    color: #4ade80; /* Bright green for better visibility */
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 18px;
    font-weight: bold;
}

.maps-button {
    display: inline-block;
    padding: 6px 12px;
    background-color: #4285F4;
    color: white !important;
    border-radius: 4px;
    text-decoration: none;
    font-weight: 600;
    margin-top: 8px;
}

.website-link {
    color: #4285F4;
    text-decoration: none;
    font-weight: 600;
}

.hours-list {
    margin-left: 20px;
    margin-bottom: 15px;
    color: #333; /* Ensure consistent text color */
}

.hours-list li {
    margin-bottom: 5px;
}

.review-box {
    margin-bottom: 10px;
    padding: 12px;
    border-left: 3px solid #ddd;
    background-color: #f5f5f5;
    border-radius: 0 4px 4px 0;
    color: #333; /* Ensure consistent text color */
}

/* Fix for the View on Google Maps button */
a.maps-button:hover {
    background-color: #3367d6;
    text-decoration: none;
    color: white !important;
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
    body {
        background-color: #111827 !important;
        color: #f3f4f6 !important;
    }
    
    .timeline-content, .place-info {
        background-color: #1f2937 !important;
        color: #f3f4f6 !important;
        border-color: #374151 !important;
    }
    
    .timeline-output h2, .timeline-item h3 {
        color: #818cf8 !important;
    }
    
    .clickable-place {
        color: #93c5fd !important;
        text-decoration: underline;
        cursor: pointer;
    }
    
    .place-details {
        background-color: #1f2937 !important;
        color: #f3f4f6 !important;
        border: 1px solid #374151 !important;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    
    /* Place card dark mode styles */
    .recommended-places-header h3 {
        color: #f87171 !important;
        border-bottom-color: #374151 !important;
    }
    
    .place-card {
        background-color: #1f2937 !important;
        color: #f3f4f6 !important;
        border-color: #374151 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    }
    
    .place-name {
        color: #4ade80 !important; /* Bright green for visibility */
    }
    
    .website-link {
        color: #60a5fa !important;
    }
    
    /* Fix hours list in dark mode */
    .hours-list {
        color: #f3f4f6 !important;
    }
    
    .hours-list li {
        color: #f3f4f6 !important;
    }
    
    /* Fix reviews in dark mode */
    .review-box {
        background-color: #374151 !important;
        border-left-color: #6b7280 !important;
        color: #f3f4f6 !important;
    }
    
    .review-box p, .review-box strong {
        color: #f3f4f6 !important;
    }
    
    /* Fix for recommendations section */
    .place-info h3, .place-info h4 {
        color: #4ade80 !important; /* Green headings for better visibility */
    }
    
    .place-info strong {
        color: #d1d5db !important; /* Lighter color for labels */
    }
    
    .place-info p, .place-info li, .place-info div {
        color: #f3f4f6 !important; /* Ensure text is visible */
    }
    
    /* Fix all elements with inline styles */
    [style*="color:#"] {
        color: #f3f4f6 !important;
    }
    
    [style*="background-color:#f"] {
        background-color: #374151 !important;
    }
    
    [style*="border-color"], [style*="border:"] {
        border-color: #4b5563 !important;
    }
}

/* Always ensure text in generated blocks is visible */
.output-text {
    color: currentColor;
}

/* Main content styles */
.output-container {
    background-color: #ffffff;
    color: #111827;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

/* Style the event idea headers and text */
.output-container h1,
.output-container h2 {
    color: #4f46e5;
}

.output-container h3 {
    color: #6366f1;
}

/* Make sure links are visible in both modes */
a, a:visited {
    color: #3b82f6;
}

@media (prefers-color-scheme: dark) {
    a, a:visited {
        color: #60a5fa !important;
    }
    
    .output-container {
        background-color: #1f2937 !important;
        color: #f3f4f6 !important;
        border: 1px solid #374151 !important;
    }
    
    .output-container h1,
    .output-container h2 {
        color: #818cf8 !important;
    }
    
    .output-container h3 {
        color: #a5b4fc !important;
    }
    
    /* Override any inline styles that might conflict */
    .output-container p, 
    .output-container li, 
    .output-container span {
        color: #f3f4f6 !important;
    }
    
    .output-container strong {
        color: #e5e7eb !important;
    }
    
    /* Fix gradio components in dark mode */
    .gradio-container {
        background-color: #111827 !important;
    }
    
    .dark .gr-box, .dark .gr-button, .dark .gr-form, .dark .gr-input, .dark .gr-panel {
        background-color: #1f2937 !important;
        color: #f3f4f6 !important;
    }
    
    /* Force all text to white in dark mode */
    div, p, span, h1, h2, h3, h4, h5, h6, li, label {
        color: #f3f4f6 !important;
    }
    
    /* Ensure buttons are visible */
    button {
        background-color: #4f46e5 !important;
        color: white !important;
    }
}

/* Force dark mode styling for specific problematic elements */
.footer, .footer * {
    color: #f3f4f6 !important;
}

/* Force dark mode on all reviews */
[id^="place_"] * {
    color: #f3f4f6 !important;
    background-color: #374151 !important;
}

/* Place names in dark mode */
.place-name, h4[style*="color:#ff6b6b"], h4.place-name {
    color: #4ade80 !important; /* Bright green for maximum visibility */
}

/* Force all text within review boxes to be visible */
div[style*="background-color:#f5f5f5"], 
div[style*="background-color: #f5f5f5"],
.review-box {
    background-color: #374151 !important;
    border-left: 3px solid #6b7280 !important;
    color: #f3f4f6 !important;
}

div[style*="background-color:#f5f5f5"] *, 
div[style*="background-color: #f5f5f5"] *,
.review-box * {
    color: #f3f4f6 !important;
}

/* Last resort - inject overrides for all elements */
.place-info div, .place-info p, .place-info span, 
.place-info li, .place-info a:not(.maps-button) {
    color: #f3f4f6 !important;
}

/* Special override for Top Review */
.place-info p strong:contains("Top Review") {
    color: #f3f4f6 !important;
    font-size: 16px !important;
}

/* Force light text on all cards in dark mode */
.place-card * {
    color: #f3f4f6 !important;
}

/* Ensure strong elements are visible */
.place-card strong, .place-info strong {
    color: #e5e7eb !important;
}

/* Force Google Maps button to remain visible */
a[href*="maps.google.com"], a[href*="google.com/maps"], .maps-button {
    color: white !important;
    background-color: #4285F4 !important;
}

/* Itinerary section styling */
.itinerary-container {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 20px;
    margin-top: 20px;
    background-color: #f9fafb;
}

.itinerary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    border-bottom: 2px solid #818cf8;
    padding-bottom: 10px;
}

.itinerary-header h3 {
    color: #4f46e5;
    margin: 0;
    font-size: 20px;
    font-weight: bold;
}

.itinerary-item {
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    background-color: white;
    position: relative;
}

.itinerary-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.itinerary-item-title {
    font-weight: bold;
    color: #4f46e5;
    font-size: 16px;
    margin: 0;
}

.itinerary-item-time {
    color: #6b7280;
    font-size: 14px;
}

.itinerary-item-description {
    margin-bottom: 8px;
    font-size: 14px;
}

.itinerary-item-cost {
    font-weight: bold;
    color: #10b981;
}

.itinerary-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 15px;
}

.itinerary-empty {
    text-align: center;
    padding: 20px;
    color: #6b7280;
    font-style: italic;
}

.remove-item-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: #ef4444;
    color: white;
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 14px;
    line-height: 1;
}

.remove-item-btn:hover {
    background-color: #dc2626;
}

.add-to-itinerary-btn {
    background-color: #4f46e5;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    cursor: pointer;
    font-size: 14px;
    margin-top: 10px;
}

.add-to-itinerary-btn:hover {
    background-color: #4338ca;
}

.export-btn, .share-btn, .regenerate-btn {
    background-color: #10b981;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    font-size: 14px;
}

.export-btn:hover, .share-btn:hover {
    background-color: #059669;
}

.regenerate-btn {
    background-color: #f59e0b;
}

.regenerate-btn:hover {
    background-color: #d97706;
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
    .itinerary-container {
        background-color: #1f2937;
        border-color: #374151;
    }
    
    .itinerary-item {
        background-color: #111827;
        border-color: #374151;
    }
    
    .itinerary-item-title {
        color: #818cf8;
    }
    
    .itinerary-item-time {
        color: #9ca3af;
    }
    
    .itinerary-item-cost {
        color: #34d399;
    }
    
    .itinerary-empty {
        color: #9ca3af;
    }
}
"""

def render_itinerary(itinerary_items):
    """Render the itinerary as HTML"""
    if not itinerary_items:
        return """
        <div class="itinerary-container">
            <div class="itinerary-header">
                <h3>Your Itinerary</h3>
            </div>
            <div class="itinerary-empty">
                Your itinerary is empty. Add items from the recommendations.
            </div>
        </div>
        """
    
    html = """
    <div class="itinerary-container">
        <div class="itinerary-header">
            <h3>Your Itinerary</h3>
        </div>
        <div class="itinerary-items-container" id="itinerary-items-container">
    """
    
    for i, item in enumerate(itinerary_items):
        if item['type'] == 'event':
            # Format the timeline for display
            timeline_html = ""
            for line in item['timeline'].strip().split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-'):
                    # It's a time entry, format it specially
                    line = line.replace('-', '•', 1).strip()
                    
                    # Extract time if possible for editable fields
                    time_pattern = r'(\d+:\d+ [AP]M) - (\d+:\d+ [AP]M)'
                    time_match = re.search(time_pattern, line)
                    
                    if time_match:
                        start_time = time_match.group(1)
                        end_time = time_match.group(2)
                        activity = line.split(':', 1)[1].strip() if ':' in line else line
                        
                        # Create editable time fields
                        timeline_html += f'''
                        <div class="timeline-entry editable-timeline-entry" style="margin-bottom:8px; padding-left:10px; border-left:2px solid #4f46e5;">
                            <div class="time-edit-container">
                                <input type="text" class="time-edit start-time" value="{start_time}" 
                                       data-item-id="{item['id']}" data-line-index="{len(timeline_html.split('timeline-entry'))-1}">
                                <span>-</span>
                                <input type="text" class="time-edit end-time" value="{end_time}" 
                                       data-item-id="{item['id']}" data-line-index="{len(timeline_html.split('timeline-entry'))-1}">
                                <span class="activity-text">{activity}</span>
                            </div>
                        </div>
                        '''
                    else:
                        timeline_html += f'<div class="timeline-entry" style="margin-bottom:8px; padding-left:10px; border-left:2px solid #4f46e5;">{line}</div>'
                else:
                    timeline_html += f'<div style="margin-bottom:6px;">{line}</div>'
            
            html += f"""
            <div class="itinerary-item" data-id="{item['id']}" draggable="true">
                <button class="remove-item-btn" onclick="removeFromItinerary('{item['id']}')">×</button>
                <div class="itinerary-item-header">
                    <h4 class="itinerary-item-title">{item['title']}</h4>
                    <button class="regenerate-place-btn" onclick="regeneratePlace('{item['id']}')">🔄 Regenerate</button>
                </div>
                <div class="itinerary-item-description">
                    {timeline_html}
                </div>
                <div class="itinerary-item-cost">
                    Total Cost: ${item['cost']}
                </div>
            </div>
            """
        elif item['type'] == 'place':
            # For places, add time fields if they don't exist
            start_time = item.get('start_time', '')
            end_time = item.get('end_time', '')
            
            html += f"""
            <div class="itinerary-item" data-id="{item['id']}" draggable="true">
                <button class="remove-item-btn" onclick="removeFromItinerary('{item['id']}')">×</button>
                <div class="itinerary-item-header">
                    <h4 class="itinerary-item-title">{item['name']}</h4>
                    <button class="regenerate-place-btn" onclick="regeneratePlace('{item['id']}')">🔄 Regenerate</button>
                </div>
                <div class="itinerary-item-time-edit">
                    <label>Visit time:</label>
                    <input type="text" class="time-edit start-time" placeholder="Start time" value="{start_time}" 
                           data-item-id="{item['id']}">
                    <span>-</span>
                    <input type="text" class="time-edit end-time" placeholder="End time" value="{end_time}" 
                           data-item-id="{item['id']}">
                </div>
                <div class="itinerary-item-description">
                    <p><strong>Address:</strong> {item['address']}</p>
                    <p><strong>Rating:</strong> {item['rating']}/5</p>
                    <p><a href="{item['url']}" target="_blank" class="maps-button">View on Google Maps</a></p>
                </div>
            </div>
            """
    
    html += """
        </div>
        <script>
        // Function to handle removing items from itinerary
        function removeFromItinerary(id) {
            // Dispatch the event to Gradio
            document.dispatchEvent(new CustomEvent('remove_from_itinerary', {
                detail: id
            }));
        }
        
        // Function to handle regenerating a specific place
        function regeneratePlace(id) {
            // Dispatch the event to Gradio
            document.dispatchEvent(new CustomEvent('regenerate_place', {
                detail: id
            }));
        }
        
        // Set up drag and drop for reordering
        document.addEventListener('DOMContentLoaded', function() {
            setupDragAndDrop();
            setupTimeEditing();
        });
        
        function setupDragAndDrop() {
            const container = document.getElementById('itinerary-items-container');
            if (!container) return;
            
            const items = container.querySelectorAll('.itinerary-item');
            
            items.forEach(item => {
                item.addEventListener('dragstart', function(e) {
                    e.dataTransfer.setData('text/plain', item.getAttribute('data-id'));
                    item.classList.add('dragging');
                });
                
                item.addEventListener('dragend', function() {
                    item.classList.remove('dragging');
                });
                
                item.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    const draggingItem = container.querySelector('.dragging');
                    if (draggingItem !== item) {
                        const rect = item.getBoundingClientRect();
                        const y = e.clientY - rect.top;
                        
                        if (y < rect.height / 2) {
                            container.insertBefore(draggingItem, item);
                        } else {
                            container.insertBefore(draggingItem, item.nextSibling);
                        }
                        
                        // Save the new order
                        saveItineraryOrder();
                    }
                });
            });
            
            container.addEventListener('dragover', function(e) {
                e.preventDefault();
            });
        }
        
        function setupTimeEditing() {
            const timeInputs = document.querySelectorAll('.time-edit');
            
            timeInputs.forEach(input => {
                input.addEventListener('change', function() {
                    const itemId = this.getAttribute('data-item-id');
                    const isStartTime = this.classList.contains('start-time');
                    const timeValue = this.value;
                    
                    // Dispatch event to update the time
                    document.dispatchEvent(new CustomEvent('update_item_time', {
                        detail: JSON.stringify({
                            id: itemId,
                            timeType: isStartTime ? 'start' : 'end',
                            value: timeValue
                        })
                    }));
                });
            });
        }
        
        function saveItineraryOrder() {
            const container = document.getElementById('itinerary-items-container');
            if (!container) return;
            
            const items = container.querySelectorAll('.itinerary-item');
            const newOrder = Array.from(items).map(item => item.getAttribute('data-id'));
            
            // Dispatch event to update the order
            document.dispatchEvent(new CustomEvent('update_itinerary_order', {
                detail: JSON.stringify(newOrder)
            }));
        }
        </script>
    </div>
    """
    
    return html

def add_to_itinerary(itinerary_state, item_json):
    """Add an item to the itinerary"""
    try:
        item = json.loads(item_json)
        # Check if item is already in itinerary
        if not any(existing['id'] == item['id'] for existing in itinerary_state):
            # Add place_id if it's a place
            if item['type'] == 'place' and 'place_id' not in item and 'id' in item:
                # Extract place_id from the id (format: place_PLACEID)
                if item['id'].startswith('place_'):
                    item['place_id'] = item['id'].split('_', 1)[1]
            
            itinerary_state.append(item)
            
            # Add JavaScript to update marker color
            if item['type'] == 'place' and 'place_id' in item:
                # Add script to update marker color
                script = f"""
                <script>
                try {{
                    // Update marker color to green
                    if (typeof updateMarkerColor === 'function') {{
                        updateMarkerColor("{item['place_id']}", "green");
                    }}
                }} catch (e) {{
                    console.error("Error updating marker color:", e);
                }}
                </script>
                """
                return render_itinerary(itinerary_state) + script, itinerary_state
        
        # Render the updated itinerary
        return render_itinerary(itinerary_state), itinerary_state
    except Exception as e:
        print(f"Error adding to itinerary: {str(e)}")
        return render_itinerary(itinerary_state), itinerary_state

def remove_from_itinerary(itinerary_state, item_id):
    """Remove an item from the itinerary"""
    # Find the item to be removed
    item_to_remove = None
    for item in itinerary_state:
        if item['id'] == item_id:
            item_to_remove = item
            break
    
    # Remove the item
    itinerary_state = [item for item in itinerary_state if item['id'] != item_id]
    
    # If it was a place, update the marker color
    if item_to_remove and item_to_remove['type'] == 'place' and 'place_id' in item_to_remove:
        # Add script to update marker color
        script = f"""
        <script>
        try {{
            // Update marker color back to blue
            if (typeof updateMarkerColor === 'function') {{
                updateMarkerColor("{item_to_remove['place_id']}", "blue");
            }}
        }} catch (e) {{
            console.error("Error updating marker color:", e);
        }}
        </script>
        """
        return render_itinerary(itinerary_state) + script, itinerary_state
    
    return render_itinerary(itinerary_state), itinerary_state

def update_item_time(itinerary_state, update_data_json):
    """Update the time for an item in the itinerary"""
    try:
        update_data = json.loads(update_data_json)
        item_id = update_data.get('id')
        time_type = update_data.get('timeType')
        time_value = update_data.get('value')
        
        for item in itinerary_state:
            if item['id'] == item_id:
                if time_type == 'start':
                    item['start_time'] = time_value
                else:
                    item['end_time'] = time_value
                break
        
        # Render the updated itinerary
        return render_itinerary(itinerary_state), itinerary_state
    except Exception as e:
        print(f"Error updating item time: {str(e)}")
        return render_itinerary(itinerary_state), itinerary_state

def update_itinerary_order(itinerary_state, order_json):
    """Update the order of items in the itinerary"""
    try:
        new_order = json.loads(order_json)
        
        # Create a dictionary of items by ID for quick lookup
        items_by_id = {item['id']: item for item in itinerary_state}
        
        # Create a new itinerary with the updated order
        new_itinerary = [items_by_id[item_id] for item_id in new_order if item_id in items_by_id]
        
        # Render the updated itinerary
        return render_itinerary(new_itinerary), new_itinerary
    except Exception as e:
        print(f"Error updating itinerary order: {str(e)}")
        return render_itinerary(itinerary_state), itinerary_state

def regenerate_recommendations(last_inputs, current_recommendations):
    """Regenerate recommendations with the same inputs"""
    if not last_inputs:
        return "Please generate recommendations first.", "", "", "", render_itinerary([])
    
    # Extract inputs
    inputs = last_inputs.get('inputs', {})
    
    # Generate new recommendations
    main_content, timeline_content, map_html, place_details = generate_event_ideas(
        inputs.get('time_available', 4),
        inputs.get('budget', 100),
        inputs.get('vibe', []),
        inputs.get('location_type', []),
        inputs.get('physical_activity', 5),
        inputs.get('partner_likes', ""),
        inputs.get('partner_dislikes', ""),
        inputs.get('partner_hobbies', ""),
        inputs.get('partner_personality', ""),
        inputs.get('self_preferences', ""),
        inputs.get('misc_input', ""),
        inputs.get('location', ""),
        inputs.get('event_type', "Casual Dating")
    )
    
    # Extract event ideas from the content
    event_ideas = []
    
    # Extract titles and descriptions
    title_pattern = r'## Event Idea: (.*?)[\r\n]'
    titles = re.findall(title_pattern, main_content)
    
    # Extract timeline sections
    timeline_pattern = r'### Timeline:(.*?)(?=###|$)'
    timeline_matches = re.findall(timeline_pattern, main_content, re.DOTALL)
    
    # Extract cost information
    cost_pattern = r'\*\*Total Cost\*\*: \$([\d.]+)'
    costs = re.findall(cost_pattern, main_content)
    
    # Extract why it's a good fit
    fit_pattern = r'\*\*Why It\'s a Good Fit\*\*: (.*?)[\r\n]'
    fits = re.findall(fit_pattern, main_content)
    
    # Combine the extracted information
    for i in range(len(titles)):
        if i < len(timeline_matches) and i < len(costs) and i < len(fits):
            event_ideas.append({
                "title": titles[i],
                "timeline": timeline_matches[i].strip(),
                "cost": costs[i],
                "fit": fits[i],
                "id": f"event_{i}"
            })
    
    # Store the recommendations and inputs
    current_recommendations_data = {
        "event_ideas": event_ideas,
        "place_details": place_details,
        "inputs": inputs
    }
    
    # Add buttons to add events to itinerary
    main_content_with_buttons = main_content
    for i, idea in enumerate(event_ideas):
        button_html = f"""
        <button onclick="addToItinerary('{idea['id']}')" class="add-to-itinerary-btn">
            Add to Itinerary
        </button>
        """
        # Add the button after each event idea title
        pattern = f"## Event Idea: {re.escape(idea['title'])}"
        replacement = f"## Event Idea: {idea['title']}\n{button_html}"
        main_content_with_buttons = re.sub(pattern, replacement, main_content_with_buttons)
    
    # Format place details for display
    place_info_html = ""
    if place_details:
        place_info_html = """
        <div class="recommended-places-header">
            <h3>Recommended Places</h3>
        </div>
        """
        
        for i, place in enumerate(place_details):
            name = place.get('name', 'Unknown Place')
            address = place.get('formatted_address', place.get('vicinity', 'No address available'))
            rating = place.get('rating', 'No rating')
            maps_url = place.get('url', place.get('maps_url', '#'))
            
            # Get busy status if available
            busy_status = ""
            if 'opening_hours' in place:
                if place['opening_hours'].get('open_now', False):
                    busy_status = "Currently open"
                else:
                    busy_status = "Currently closed"
            
            place_info_html += f"""
            <div class="place-card">
                <h4 class="place-name">{name}</h4>
                <p><strong>Address:</strong> {address}</p>
                <p><strong>Rating:</strong> {rating}/5</p>
                {f"<p><strong>Status:</strong> {busy_status}</p>" if busy_status else ""}
                <p><a href="{maps_url}" target="_blank" class="maps-button">View on Google Maps</a></p>
                <button onclick="addPlaceToItinerary('place_{i}', '{place.get('place_id', '')}')" class="add-to-itinerary-btn">
                    Add to Itinerary
                </button>
            """
            
            # Add website if available
            if place.get('website'):
                place_info_html += f"""
                <p><strong>Website:</strong> <a href="{place['website']}" target="_blank" class="website-link">{place['website']}</a></p>
                """
            
            # Add phone if available
            if place.get('formatted_phone_number'):
                place_info_html += f"""
                <p><strong>Phone:</strong> {place['formatted_phone_number']}</p>
                """
            
            # Add opening hours if available
            if 'opening_hours' in place and 'weekday_text' in place['opening_hours']:
                place_info_html += "<p><strong>Opening Hours:</strong></p><ul class='hours-list'>"
                for day in place['opening_hours']['weekday_text']:
                    place_info_html += f"<li>{day}</li>"
                place_info_html += "</ul>"
            
            # Add reviews if available
            if 'reviews' in place and place['reviews']:
                place_info_html += "<p><strong>Top Review:</strong></p>"
                review = place['reviews'][0]
                author = review.get('author_name', 'Anonymous')
                review_rating = review.get('rating', 'No rating')
                text = review.get('text', 'No comment')
                time = review.get('relative_time_description', '')
                
                place_info_html += f"""
                <div class="review-box">
                    <p><strong>{author}</strong> - {review_rating}/5 ({time})</p>
                    <p>{text}</p>
                </div>
                """
            
            place_info_html += "</div>"
    
    # Add JavaScript for adding items to itinerary
    js_for_itinerary = f"""
    <script>
    // Store the current recommendations
    window.currentRecommendations = {json.dumps(current_recommendations_data)};
    
    function addToItinerary(id) {{
        // Find the event in the recommendations
        const event = window.currentRecommendations.event_ideas.find(e => e.id === id);
        if (event) {{
            // Create a custom event to trigger the Python function
            const event_data = {{
                type: 'event',
                id: id,
                title: event.title,
                timeline: event.timeline,
                cost: event.cost,
                fit: event.fit
            }};
            
            // Dispatch the event to Gradio
            document.dispatchEvent(new CustomEvent('add_to_itinerary', {{
                detail: JSON.stringify(event_data)
            }}));
        }}
    }}
    
    function addPlaceToItinerary(id, placeId) {{
        // Extract the index from the id (format: place_X)
        const index = parseInt(id.split('_')[1]);
        if (!isNaN(index) && index >= 0 && index < window.currentRecommendations.place_details.length) {{
            const place = window.currentRecommendations.place_details[index];
            
            // Create a custom event to trigger the Python function
            const place_data = {{
                type: 'place',
                id: id,
                place_id: placeId || place.place_id || '',
                name: place.name || 'Unknown Place',
                address: place.formatted_address || place.vicinity || 'No address available',
                rating: place.rating || 'No rating',
                url: place.url || place.maps_url || '#'
            }};
            
            // Dispatch the event to Gradio
            document.dispatchEvent(new CustomEvent('add_to_itinerary', {{
                detail: JSON.stringify(place_data)
            }}));
        }}
    }}
    </script>
    """
    
    # Add the JavaScript to the main content
    main_content_with_buttons += js_for_itinerary
    
    return main_content_with_buttons, timeline_content, map_html, place_info_html, current_recommendations_data

def regenerate_place(itinerary_state, current_recommendations, place_id):
    """Regenerate a specific place in the itinerary"""
    if not current_recommendations:
        return "Please generate recommendations first.", "", "", "", render_itinerary(itinerary_state), itinerary_state
    
    # Find the place in the itinerary
    place_to_regenerate = None
    for item in itinerary_state:
        if item['id'] == place_id:
            place_to_regenerate = item
            break
    
    if not place_to_regenerate:
        return "Place not found in itinerary.", "", "", "", render_itinerary(itinerary_state), itinerary_state
    
    # Extract inputs from current recommendations
    inputs = current_recommendations.get('inputs', {})
    
    # If it's an event, regenerate a similar event
    if place_to_regenerate['type'] == 'event':
        # Generate new recommendations with the same inputs
        main_content, timeline_content, map_html, place_details = generate_event_ideas(
            inputs.get('time_available', 4),
            inputs.get('budget', 100),
            inputs.get('vibe', []),
            inputs.get('location_type', []),
            inputs.get('physical_activity', 5),
            inputs.get('partner_likes', ""),
            inputs.get('partner_dislikes', ""),
            inputs.get('partner_hobbies', ""),
            inputs.get('partner_personality', ""),
            inputs.get('self_preferences', ""),
            inputs.get('misc_input', ""),
            inputs.get('location', ""),
            inputs.get('event_type', "Casual Dating")
        )
        
        # Extract event ideas from the content
        event_ideas = []
        
        # Extract titles and descriptions
        title_pattern = r'## Event Idea: (.*?)[\r\n]'
        titles = re.findall(title_pattern, main_content)
        
        # Extract timeline sections
        timeline_pattern = r'### Timeline:(.*?)(?=###|$)'
        timeline_matches = re.findall(timeline_pattern, main_content, re.DOTALL)
        
        # Extract cost information
        cost_pattern = r'\*\*Total Cost\*\*: \$([\d.]+)'
        costs = re.findall(cost_pattern, main_content)
        
        # Extract why it's a good fit
        fit_pattern = r'\*\*Why It\'s a Good Fit\*\*: (.*?)[\r\n]'
        fits = re.findall(fit_pattern, main_content)
        
        # Combine the extracted information
        for i in range(len(titles)):
            if i < len(timeline_matches) and i < len(costs) and i < len(fits):
                event_ideas.append({
                    "title": titles[i],
                    "timeline": timeline_matches[i].strip(),
                    "cost": costs[i],
                    "fit": fits[i],
                    "id": f"event_{i}"
                })
        
        # Replace the old event with the first new one
        if event_ideas:
            new_event = event_ideas[0]
            new_event['id'] = place_to_regenerate['id']  # Keep the same ID
            
            # Preserve time if it was set
            if 'start_time' in place_to_regenerate:
                new_event['start_time'] = place_to_regenerate['start_time']
            if 'end_time' in place_to_regenerate:
                new_event['end_time'] = place_to_regenerate['end_time']
            
            # Replace the old event with the new one
            for i, item in enumerate(itinerary_state):
                if item['id'] == place_id:
                    itinerary_state[i] = new_event
                    break
        
        # Update the current recommendations
        current_recommendations_data = {
            "event_ideas": event_ideas,
            "place_details": place_details,
            "inputs": inputs
        }
        
        # Format the output similar to regenerate_recommendations
        main_content_with_buttons = main_content
        for i, idea in enumerate(event_ideas):
            button_html = f"""
            <button onclick="addToItinerary('{idea['id']}')" class="add-to-itinerary-btn">
                Add to Itinerary
            </button>
            """
            pattern = f"## Event Idea: {re.escape(idea['title'])}"
            replacement = f"## Event Idea: {idea['title']}\n{button_html}"
            main_content_with_buttons = re.sub(pattern, replacement, main_content_with_buttons)
        
        # Format place details for display
        place_info_html = ""
        if place_details:
            place_info_html = """
            <div class="recommended-places-header">
                <h3>Recommended Places</h3>
            </div>
            """
            
            for i, place in enumerate(place_details):
                name = place.get('name', 'Unknown Place')
                address = place.get('formatted_address', place.get('vicinity', 'No address available'))
                rating = place.get('rating', 'No rating')
                maps_url = place.get('url', place.get('maps_url', '#'))
                
                # Get busy status if available
                busy_status = ""
                if 'opening_hours' in place:
                    if place['opening_hours'].get('open_now', False):
                        busy_status = "Currently open"
                    else:
                        busy_status = "Currently closed"
                
                place_info_html += f"""
                <div class="place-card">
                    <h4 class="place-name">{name}</h4>
                    <p><strong>Address:</strong> {address}</p>
                    <p><strong>Rating:</strong> {rating}/5</p>
                    {f"<p><strong>Status:</strong> {busy_status}</p>" if busy_status else ""}
                    <p><a href="{maps_url}" target="_blank" class="maps-button">View on Google Maps</a></p>
                    <button onclick="addPlaceToItinerary('place_{i}', '{place.get('place_id', '')}')" class="add-to-itinerary-btn">
                        Add to Itinerary
                    </button>
                """
                
                # Add website if available
                if place.get('website'):
                    place_info_html += f"""
                    <p><strong>Website:</strong> <a href="{place['website']}" target="_blank" class="website-link">{place['website']}</a></p>
                    """
                
                # Add phone if available
                if place.get('formatted_phone_number'):
                    place_info_html += f"""
                    <p><strong>Phone:</strong> {place['formatted_phone_number']}</p>
                    """
                
                # Add opening hours if available
                if 'opening_hours' in place and 'weekday_text' in place['opening_hours']:
                    place_info_html += "<p><strong>Opening Hours:</strong></p><ul class='hours-list'>"
                    for day in place['opening_hours']['weekday_text']:
                        place_info_html += f"<li>{day}</li>"
                    place_info_html += "</ul>"
                
                # Add reviews if available
                if 'reviews' in place and place['reviews']:
                    place_info_html += "<p><strong>Top Review:</strong></p>"
                    review = place['reviews'][0]
                    author = review.get('author_name', 'Anonymous')
                    review_rating = review.get('rating', 'No rating')
                    text = review.get('text', 'No comment')
                    time = review.get('relative_time_description', '')
                    
                    place_info_html += f"""
                    <div class="review-box">
                        <p><strong>{author}</strong> - {review_rating}/5 ({time})</p>
                        <p>{text}</p>
                    </div>
                    """
                
                place_info_html += "</div>"
        
        # Add JavaScript for adding items to itinerary
        js_for_itinerary = f"""
        <script>
        // Store the current recommendations
        window.currentRecommendations = {json.dumps(current_recommendations_data)};
        
        function addToItinerary(id) {{
            // Find the event in the recommendations
            const event = window.currentRecommendations.event_ideas.find(e => e.id === id);
            if (event) {{
                // Create a custom event to trigger the Python function
                const event_data = {{
                    type: 'event',
                    id: id,
                    title: event.title,
                    timeline: event.timeline,
                    cost: event.cost,
                    fit: event.fit
                }};
                
                // Dispatch the event to Gradio
                document.dispatchEvent(new CustomEvent('add_to_itinerary', {{
                    detail: JSON.stringify(event_data)
                }}));
            }}
        }}
        
        function addPlaceToItinerary(id, placeId) {{
            // Extract the index from the id (format: place_X)
            const index = parseInt(id.split('_')[1]);
            if (!isNaN(index) && index >= 0 && index < window.currentRecommendations.place_details.length) {{
                const place = window.currentRecommendations.place_details[index];
                
                // Create a custom event to trigger the Python function
                const place_data = {{
                    type: 'place',
                    id: id,
                    place_id: placeId || place.place_id || '',
                    name: place.name || 'Unknown Place',
                    address: place.formatted_address || place.vicinity || 'No address available',
                    rating: place.rating || 'No rating',
                    url: place.url || place.maps_url || '#'
                }};
                
                // Dispatch the event to Gradio
                document.dispatchEvent(new CustomEvent('add_to_itinerary', {{
                    detail: JSON.stringify(place_data)
                }}));
            }}
        }}
        </script>
        """
        
        # Add the JavaScript to the main content
        main_content_with_buttons += js_for_itinerary
        
        return main_content_with_buttons, timeline_content, map_html, place_info_html, render_itinerary(itinerary_state), itinerary_state
    
    # If it's a place, find similar places
    elif place_to_regenerate['type'] == 'place':
        location = inputs.get('location', "")
        if not location or not is_maps_available():
            return "Location not provided or Maps API not available.", "", "", "", render_itinerary(itinerary_state), itinerary_state
        
        # Search for similar places
        from utilities.map_tools import search_places, get_place_details
        
        # Use the place name as the search query
        search_results = search_places(location, place_to_regenerate['name'])
        
        if not search_results or len(search_results) == 0:
            return "No similar places found.", "", "", "", render_itinerary(itinerary_state), itinerary_state
        
        # Get details for the first result that's not the same as the current place
        new_place = None
        for result in search_results:
            place_id = result.get('place_id')
            place_details = get_place_details(place_id)
            
            # Skip if it's the same place
            if place_details.get('name') == place_to_regenerate['name']:
                continue
            
            new_place = {
                "type": "place",
                "id": place_to_regenerate['id'],  # Keep the same ID
                "name": place_details.get('name', 'Unknown Place'),
                "address": place_details.get('formatted_address', place_details.get('vicinity', 'No address available')),
                "rating": place_details.get('rating', 'No rating'),
                "url": place_details.get('url', place_details.get('maps_url', '#')),
                "place_id": place_id  # Add the place_id
            }
            
            # Preserve time if it was set
            if 'start_time' in place_to_regenerate:
                new_place['start_time'] = place_to_regenerate['start_time']
            if 'end_time' in place_to_regenerate:
                new_place['end_time'] = place_to_regenerate['end_time']
            
            break
        
        if not new_place:
            return "No alternative places found.", "", "", "", render_itinerary(itinerary_state), itinerary_state
        
        # If the old place had a place_id, update the marker color back to blue
        old_place_id = place_to_regenerate.get('place_id', '')
        update_old_marker_script = ""
        if old_place_id:
            update_old_marker_script = f"""
            <script>
            try {{
                // Update old marker color back to blue
                if (typeof updateMarkerColor === 'function') {{
                    updateMarkerColor("{old_place_id}", "blue");
                }}
            }} catch (e) {{
                console.error("Error updating old marker color:", e);
            }}
            </script>
            """
        
        # Replace the old place with the new one
        for i, item in enumerate(itinerary_state):
            if item['id'] == place_id:
                itinerary_state[i] = new_place
                break
        
        # Update the new marker color to green
        update_new_marker_script = ""
        if new_place.get('place_id'):
            update_new_marker_script = f"""
            <script>
            try {{
                // Update new marker color to green
                if (typeof updateMarkerColor === 'function') {{
                    updateMarkerColor("{new_place['place_id']}", "green");
                }}
            }} catch (e) {{
                console.error("Error updating new marker color:", e);
            }}
            </script>
            """
        
        # Format place details for display
        place_info_html = """
        <div class="recommended-places-header">
            <h3>Alternative Place</h3>
        </div>
        <div class="place-card">
            <h4 class="place-name">{0}</h4>
            <p><strong>Address:</strong> {1}</p>
            <p><strong>Rating:</strong> {2}/5</p>
            <p><a href="{3}" target="_blank" class="maps-button">View on Google Maps</a></p>
        </div>
        """.format(new_place['name'], new_place['address'], new_place['rating'], new_place['url'])
        
        return f"Replaced {place_to_regenerate['name']} with {new_place['name']}", "", "", place_info_html, render_itinerary(itinerary_state) + update_old_marker_script + update_new_marker_script, itinerary_state
    
    return "Item type not supported for regeneration.", "", "", "", render_itinerary(itinerary_state), itinerary_state

def export_itinerary_as_pdf(itinerary_state):
    """Export the itinerary as a PDF"""
    if not itinerary_state:
        return "Your itinerary is empty. Add items before exporting."
    
    # Create a formatted HTML version of the itinerary for printing
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your Perfect Event Itinerary</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #4f46e5;
                text-align: center;
                border-bottom: 2px solid #818cf8;
                padding-bottom: 10px;
            }
            .itinerary-item {
                margin-bottom: 20px;
                padding: 15px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            .itinerary-item-title {
                color: #4f46e5;
                margin-top: 0;
                margin-bottom: 10px;
                font-size: 18px;
            }
            .timeline-entry {
                margin-bottom: 8px;
                padding-left: 10px;
                border-left: 2px solid #4f46e5;
            }
            .itinerary-item-cost {
                font-weight: bold;
                color: #10b981;
                margin-top: 10px;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                font-size: 12px;
                color: #6b7280;
            }
        </style>
    </head>
    <body>
        <h1>Your Perfect Event Itinerary</h1>
        <p>Generated on: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """</p>
    """
    
    for item in itinerary_state:
        if item['type'] == 'event':
            # Format the timeline for display
            timeline_html = ""
            for line in item['timeline'].strip().split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-'):
                    # It's a time entry, format it specially
                    line = line.replace('-', '•', 1).strip()
                    timeline_html += f'<div class="timeline-entry">{line}</div>'
                else:
                    timeline_html += f'<div>{line}</div>'
            
            html += f"""
            <div class="itinerary-item">
                <h3 class="itinerary-item-title">{item['title']}</h3>
                <div class="itinerary-item-description">
                    {timeline_html}
                </div>
                <div class="itinerary-item-cost">
                    Total Cost: ${item['cost']}
                </div>
            </div>
            """
        elif item['type'] == 'place':
            html += f"""
            <div class="itinerary-item">
                <h3 class="itinerary-item-title">{item['name']}</h3>
                <div class="itinerary-item-description">
                    <p><strong>Address:</strong> {item['address']}</p>
                    <p><strong>Rating:</strong> {item['rating']}/5</p>
                    <p><a href="{item['url']}" target="_blank">View on Google Maps</a></p>
                </div>
            </div>
            """
    
    html += """
        <div class="footer">
            Created with Perfect Event Generator
        </div>
    </body>
    </html>
    """
    
    # Return the HTML that will be used for printing
    return html

def share_itinerary(itinerary_state):
    """Generate a shareable link for the itinerary"""
    if not itinerary_state:
        return "Your itinerary is empty. Add items before sharing."
    
    # In a real application, you would save the itinerary to a database and generate a unique URL
    # For this demo, we'll just create a data URL that can be copied
    
    # Create a simplified JSON representation of the itinerary
    itinerary_data = []
    for item in itinerary_state:
        if item['type'] == 'event':
            itinerary_data.append({
                "type": "event",
                "title": item['title'],
                "cost": item['cost']
            })
        elif item['type'] == 'place':
            itinerary_data.append({
                "type": "place",
                "name": item['name'],
                "address": item['address']
            })
    
    # Create a shareable link (in a real app, this would be a proper URL)
    share_html = f"""
    <div style="padding: 20px; background-color: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb; margin-top: 20px;">
        <h3 style="color: #4f46e5; margin-top: 0;">Share Your Itinerary</h3>
        <p>Copy the link below to share your itinerary:</p>
        <div style="position: relative;">
            <input id="share-link" type="text" value="https://perfectevent.example/share/{hash(json.dumps(itinerary_data))}" 
                   style="width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 14px;" readonly>
            <button onclick="copyShareLink()" style="position: absolute; right: 5px; top: 5px; background-color: #4f46e5; color: white; border: none; border-radius: 4px; padding: 5px 10px; cursor: pointer;">
                Copy
            </button>
        </div>
        <p style="font-size: 12px; color: #6b7280; margin-top: 10px;">
            Note: This is a demo link and doesn't actually work. In a real application, this would be a permanent link to your itinerary.
        </p>
    </div>
    
    <script>
    function copyShareLink() {{
        const shareLink = document.getElementById('share-link');
        shareLink.select();
        document.execCommand('copy');
        
        // Show a copied message
        const button = shareLink.nextElementSibling;
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        setTimeout(() => {{
            button.textContent = originalText;
        }}, 2000);
    }}
    </script>
    """
    
    return share_html

# Define Gradio interface
with gr.Blocks(
    title="Perfect Event Generator", 
    theme=gr.themes.Default(
        primary_hue="indigo",
        secondary_hue="blue",
        neutral_hue="slate",
        text_size=gr.themes.sizes.text_md,
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"]
    ), 
    css=custom_css
) as app:
    # State variables for itinerary
    itinerary_state = gr.State([])
    current_recommendations = gr.State({})
    last_inputs = gr.State({})
    
    # Add the logo at the top
    # logo_path = "static/images/logo.png"
    # with gr.Row(elem_classes="logo-container-row"):
    #     gr.Image(value=logo_path, show_label=False, container=False, height=100, width=100, elem_classes="centered-logo")
    
    gr.Markdown("# Perfect Event Generator")
    gr.Markdown("Enter your preferences and get personalized event ideas!")
    
    # Add API key status notice
    api_status_html = ""
    if not is_openai_available():
        api_status_html += """
        <div style="padding: 15px; margin-bottom: 20px; background-color: #fff3f3; border-radius: 8px; border: 1px solid #ffcccb;">
            <h3 style="color: #d9534f; margin-top: 0;"><i class="fas fa-exclamation-triangle"></i> OpenAI API Key Missing</h3>
            <p>The OpenAI API key is not configured. Event generation will not work.</p>
            <p>Please add your OpenAI API key to the .env file to enable event generation.</p>
        </div>
        """
    if not is_maps_available():
        api_status_html += """
        <div style="padding: 15px; margin-bottom: 20px; background-color: #fff3f3; border-radius: 8px; border: 1px solid #ffcccb;">
            <h3 style="color: #d9534f; margin-top: 0;"><i class="fas fa-exclamation-triangle"></i> Google Maps API Key Missing</h3>
            <p>The Google Maps API key is not configured. Location-based recommendations will not work.</p>
            <p>Please add your Google Maps API key to the .env file to enable location features.</p>
        </div>
        """
    
    if api_status_html:
        gr.HTML(api_status_html)
    
    # Main input section with 3 columns
    with gr.Row():
        # First column - Basic preferences
        with gr.Column(scale=1):
            gr.Markdown("### Basic Preferences")
            
            # Add event type selection
            event_type = gr.Dropdown(
                label="Event Type",
                choices=[
                    "First Date", 
                    "Casual Dating", 
                    "Married Date", 
                    "Night with the Girls", 
                    "Night with the Boys",
                    "Family Outing",
                    "Afterwork Meetup",
                    "Hookup"
                ],
                value="Casual Dating",
                elem_classes="mobile-friendly-dropdown"
            )
            
            time_available = gr.Slider(
                label="Time Available (hours)",
                minimum=1,
                maximum=12,
                value=4,
                step=0.5,
                info="Slide to select how many hours you have available",
                elem_classes="mobile-friendly-slider"
            )
            
            # Add date and time preference options
            with gr.Accordion("Specific Date/Time Preferences (Optional)", open=False):
                time_preference = gr.Dropdown(
                    label="When would you like to go?",
                    choices=[
                        "Anytime",
                        "Today",
                        "Tomorrow", 
                        "This weekend",
                        "Next weekend",
                        "Anytime in the next 7 days",
                        "Anytime in the next 30 days",
                        "Specific dates"
                    ],
                    value="Anytime",
                    elem_classes="mobile-friendly-dropdown"
                )
                
                with gr.Group(visible=False) as specific_dates_group:
                    specific_date1 = gr.Textbox(
                        label="Date Option 1",
                        placeholder="e.g., Friday, April 19",
                        elem_classes="mobile-friendly-input"
                    )
                    specific_time1 = gr.Textbox(
                        label="Time Option 1",
                        placeholder="e.g., Evening, 7 PM, Afternoon",
                        elem_classes="mobile-friendly-input"
                    )
                    
                    specific_date2 = gr.Textbox(
                        label="Date Option 2 (Optional)",
                        placeholder="e.g., Saturday, April 20",
                        elem_classes="mobile-friendly-input"
                    )
                    specific_time2 = gr.Textbox(
                        label="Time Option 2 (Optional)",
                        placeholder="e.g., Morning, All day, 1-5 PM",
                        elem_classes="mobile-friendly-input"
                    )
                    
                    specific_date3 = gr.Textbox(
                        label="Date Option 3 (Optional)",
                        placeholder="e.g., Sunday, April 21",
                        elem_classes="mobile-friendly-input"
                    )
                    specific_time3 = gr.Textbox(
                        label="Time Option 3 (Optional)",
                        placeholder="e.g., Lunch time, 2-4 PM",
                        elem_classes="mobile-friendly-input"
                    )
                
                # Add JavaScript handler to show/hide specific dates based on dropdown
                time_preference.change(
                    fn=lambda x: {"visible": x == "Specific dates"},
                    inputs=[time_preference],
                    outputs=[specific_dates_group]
                )
            
            budget = gr.Slider(
                label="Budget ($)",
                minimum=0,
                maximum=500,
                value=100,
                step=10,
                info="Slide to select your budget in dollars",
                elem_classes="mobile-friendly-slider"
            )
            
            physical_activity = gr.Slider(
                label="Physical Activity Level (1-10)",
                minimum=1,
                maximum=10,
                value=5,
                step=1,
                info="1 = Very low, 10 = Very high",
                elem_classes="mobile-friendly-slider"
            )
            
            vibe = gr.Dropdown(
                label="Desired Vibe (select multiple)",
                choices=["Romantic", "Adventurous", "Relaxed", "Fun", "Cultural", "Intellectual", "Sophisticated", "Energetic"],
                multiselect=True,
                value=["Fun", "Relaxed"],
                elem_classes="mobile-friendly-dropdown"
            )
            
            location_type = gr.Dropdown(
                label="Location Type (select multiple)",
                choices=["Indoors", "Outdoors", "Urban", "Nature", "Beach", "Mountains", "Countryside"],
                multiselect=True,
                value=["Indoors", "Outdoors"],
                elem_classes="mobile-friendly-dropdown"
            )
            
            location = gr.Textbox(
                label="Your Location (optional, for place recommendations)",
                placeholder="e.g., San Francisco, CA",
                info="Enter your city, state, country for location-specific suggestions and maps",
                elem_classes="mobile-friendly-input location-input"
            )
            
            with gr.Row():
                gr.Button("📍 Use My Current Location", elem_id="get-location-btn", elem_classes="location-btn")
        
        # Second column - Partner preferences (dynamic label based on event type)
        with gr.Column(scale=1, elem_id="partner-preferences-column"):
            partner_prefs_markdown = gr.Markdown("### Participant Preferences", elem_id="prefs_header")
            
            partner_likes = gr.Textbox(
                label="What do they like?",
                placeholder="e.g., Italian food, live music, art galleries",
                lines=2,
                elem_classes="mobile-friendly-input",
                elem_id="likes_field"
            )
            
            partner_dislikes = gr.Textbox(
                label="What do they dislike?",
                placeholder="e.g., crowds, spicy food, horror movies",
                lines=2,
                elem_classes="mobile-friendly-input",
                elem_id="dislikes_field"
            )
            
            partner_hobbies = gr.Textbox(
                label="Interests/Hobbies",
                placeholder="e.g., hiking, photography, board games",
                lines=2,
                elem_classes="mobile-friendly-input",
                elem_id="hobbies_field"
            )
            
            partner_personality = gr.Textbox(
                label="Personality traits",
                placeholder="e.g., introverted, adventurous, analytical",
                lines=2,
                elem_classes="mobile-friendly-input",
                elem_id="personality_field"
            )
        
        # Third column - Your preferences and misc
        with gr.Column(scale=1):
            gr.Markdown("### Your Preferences & Additional Info")
            self_preferences = gr.Textbox(
                label="Your Preferences (optional)",
                placeholder="e.g., I prefer casual settings, would like to avoid loud places",
                lines=2,
                elem_classes="mobile-friendly-input"
            )
            
            misc_input = gr.Textbox(
                label="Any Other Details (optional)",
                placeholder="e.g., special occasion, accessibility requirements, etc.",
                lines=2,
                elem_classes="mobile-friendly-input"
            )
            
            # Add some spacing
            gr.Markdown("<br>")
            gr.Markdown("<br>")
            
            # Generate button at the bottom of the third column
            generate_button = gr.Button("Generate Event Ideas", variant="primary", elem_classes="generate-btn", size="lg")
    
    # Create the layout for outputs
    with gr.Row() as output_container:
        # Main content on the left (2/3 width)
        with gr.Column(scale=2):
            output = gr.Markdown(elem_classes=["output-text"], visible=True)
        
        # Timeline on the right (1/3 width)
        with gr.Column(scale=1):
            timeline_output = gr.HTML(elem_classes=["timeline-output"])
    
    # Itinerary section
    with gr.Row() as itinerary_container:
        with gr.Column():
            itinerary_output = gr.HTML(elem_classes=["itinerary-output"], label="Your Itinerary")
            
            with gr.Row():
                export_btn = gr.Button("Export Itinerary as PDF", elem_classes=["export-btn"])
                share_btn = gr.Button("Share Itinerary", elem_classes=["share-btn"])
                regenerate_btn = gr.Button("Regenerate Recommendations", elem_classes=["regenerate-btn"])
    
    # Map in full width
    with gr.Row() as map_container:
        map_output = gr.HTML(elem_classes=["map-output"])
    
    # Place details in full width
    with gr.Row() as place_container:
        place_info = gr.HTML(elem_classes=["place-info"], show_label=False)
    
    # Add the CSS to the page
    gr.HTML(f"<style>{css}</style>")
    
    # Add the JavaScript
    gr.HTML(f"""<script>
    function updateUIForEventType(eventType) {{
        // Get elements
        const partnerColumn = document.getElementById('partner-preferences-column');
        const partnerHeader = document.getElementById('prefs_header');
        const partnerLikes = document.getElementById('likes_field');
        const partnerDislikes = document.getElementById('dislikes_field');
        const partnerHobbies = document.getElementById('hobbies_field');
        const partnerPersonality = document.getElementById('personality_field');
        
        // Update headers and placeholders based on event type
        if (eventType === "Family Outing") {{
            partnerHeader.textContent = "Family Preferences";
            partnerLikes.querySelector('label').textContent = "What does your family like?";
            partnerDislikes.querySelector('label').textContent = "What does your family dislike?";
            partnerHobbies.querySelector('label').textContent = "Family interests/activities";
            partnerPersonality.querySelector('label').textContent = "Family dynamic";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Parks, family-friendly restaurants...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Long wait times, very noisy places...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Board games, movie nights, hiking...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Kids ages, energy levels, interests...";
        }} 
        else if (eventType === "Night with the Girls" || eventType === "Night with the Boys") {{
            partnerHeader.textContent = "Group Preferences";
            partnerLikes.querySelector('label').textContent = "What do your friends like?";
            partnerDislikes.querySelector('label').textContent = "What do your friends dislike?";
            partnerHobbies.querySelector('label').textContent = "Group interests/activities";
            partnerPersonality.querySelector('label').textContent = "Group dynamic";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Wine, spa days, shopping...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Noisy venues, long walks...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Yoga, book clubs, cooking...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Creative, social, energetic...";
        }}
        else if (eventType === "Afterwork Meetup") {{
            partnerHeader.textContent = "Colleague Preferences";
            partnerLikes.querySelector('label').textContent = "What do your colleagues like?";
            partnerDislikes.querySelector('label').textContent = "What do your colleagues dislike?";
            partnerHobbies.querySelector('label').textContent = "Group interests/activities";
            partnerPersonality.querySelector('label').textContent = "Work relationships";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Happy hours, casual dining...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Work talk, formal settings...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Networking, team sports...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Mix of personalities, department culture...";
        }}
        else if (eventType === "Married Date") {{
            partnerHeader.textContent = "Spouse Preferences";
            partnerLikes.querySelector('label').textContent = "What does your spouse like?";
            partnerDislikes.querySelector('label').textContent = "What does your spouse dislike?";
            partnerHobbies.querySelector('label').textContent = "Spouse's interests/hobbies";
            partnerPersonality.querySelector('label').textContent = "Spouse's personality traits";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Fine dining, quiet evenings...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Over-planned activities, crowds...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Gardening, reading, crafts...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Thoughtful, intellectual, homebody...";
        }}
        else if (eventType === "Hookup") {{
            partnerHeader.textContent = "Partner Preferences";
            partnerLikes.querySelector('label').textContent = "What do they like?";
            partnerDislikes.querySelector('label').textContent = "What do they dislike?";
            partnerHobbies.querySelector('label').textContent = "Interests/Turn-ons";
            partnerPersonality.querySelector('label').textContent = "Personality/Vibe";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Dancing, specific drinks, music...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Small talk, crowded venues...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Spontaneity, confidence, physical touch...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Flirty, laid-back, adventurous...";
        }}
        else {{
            // Default for casual dating, first date
            partnerHeader.textContent = "Partner Preferences";
            partnerLikes.querySelector('label').textContent = "What does your partner like?";
            partnerDislikes.querySelector('label').textContent = "What does your partner dislike?";
            partnerHobbies.querySelector('label').textContent = "Partner's interests/hobbies";
            partnerPersonality.querySelector('label').textContent = "Partner's personality traits";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Art, music, specific cuisines, sports...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Crowds, certain foods, activities they avoid...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Photography, hiking, cooking, gaming...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Introverted, adventurous, detail-oriented...";
        }}
    }}
    
    // Set up the event listener once the DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {{
        setTimeout(function() {{
            const dropdown = document.querySelector('select[data-testid="dropdown"]');
            if (dropdown) {{
                dropdown.addEventListener('change', function() {{
                    updateUIForEventType(this.value);
                }});
                // Initial update
                updateUIForEventType("Casual Dating");
            }}
        }}, 1000);
    }});
    </script>""")
    
    # Add JavaScript for geolocation
    gr.HTML("""
    <script>
    function setupGeolocation() {
        const locationBtn = document.getElementById('get-location-btn');
        if (locationBtn) {
            // Remove any existing click handlers to prevent duplicates
            locationBtn.removeEventListener('click', getLocation);
            // Add the click handler
            locationBtn.addEventListener('click', getLocation);
            console.log('Geolocation button handler set up');
        } else {
            console.error('Geolocation button not found');
        }
    }

    function getLocation() {
        console.log('Geolocation requested');
        if (navigator.geolocation) {
            // Show loading state
            const locationBtn = document.getElementById('get-location-btn');
            const originalText = locationBtn.textContent;
            locationBtn.textContent = "Getting location...";
            locationBtn.disabled = true;
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    console.log('Geolocation success:', position);
                    // Success callback
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    
                    // Use reverse geocoding to get address from coordinates
                    reverseGeocode(latitude, longitude);
                },
                function(error) {
                    console.error('Geolocation error:', error);
                    // Error callback
                    const locationBtn = document.getElementById('get-location-btn');
                    locationBtn.textContent = originalText;
                    locationBtn.disabled = false;
                    
                    let errorMessage = "Unable to retrieve your location. ";
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage += "Location access was denied. Please check your browser permissions.";
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage += "Location information is unavailable.";
                            break;
                        case error.TIMEOUT:
                            errorMessage += "The request to get location timed out.";
                            break;
                        case error.UNKNOWN_ERROR:
                            errorMessage += "An unknown error occurred.";
                            break;
                    }
                    
                    alert(errorMessage);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    }
    
    function reverseGeocode(latitude, longitude) {
        console.log('Reverse geocoding:', latitude, longitude);
        // Use a free reverse geocoding service
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10`)
            .then(response => response.json())
            .then(data => {
                console.log('Reverse geocoding success:', data);
                const locationBtn = document.getElementById('get-location-btn');
                locationBtn.textContent = "📍 Use My Current Location";
                locationBtn.disabled = false;
                
                // Extract location information
                let location = "";
                
                if (data.address) {
                    const address = data.address;
                    
                    // Build location string based on available address components
                    const components = [];
                    
                    // Add city/town/village
                    if (address.city) components.push(address.city);
                    else if (address.town) components.push(address.town);
                    else if (address.village) components.push(address.village);
                    
                    // Add state/province
                    if (address.state) components.push(address.state);
                    
                    // Add country
                    if (address.country) components.push(address.country);
                    
                    location = components.join(", ");
                }
                
                if (!location) {
                    location = `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
                }
                
                // Find the location input field - more reliably by looking for the element with location-input class
                const locationInput = document.querySelector('.location-input textarea, .location-input input');
                
                if (locationInput) {
                    // Set the value
                    locationInput.value = location;
                    
                    // Trigger an input event to ensure Gradio recognizes the change
                    const event = new Event('input', { bubbles: true });
                    locationInput.dispatchEvent(event);
                    
                    // Also trigger a change event for good measure
                    const changeEvent = new Event('change', { bubbles: true });
                    locationInput.dispatchEvent(changeEvent);
                    
                    console.log('Location input updated to:', location);
                } else {
                    console.error('Location input field not found');
                    // Fallback to the old method
                    const locationInputs = document.querySelectorAll('input, textarea');
                    for (let input of locationInputs) {
                        if (input.placeholder && (
                            input.placeholder.includes("San Francisco") || 
                            input.placeholder.includes("location") ||
                            input.placeholder.toLowerCase().includes("city")
                        )) {
                            input.value = location;
                            
                            // Trigger events
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            
                            console.log('Location input found and updated using fallback method');
                            break;
                        }
                    }
                }
            })
            .catch(error => {
                console.error("Error during reverse geocoding:", error);
                const locationBtn = document.getElementById('get-location-btn');
                locationBtn.textContent = "📍 Use My Current Location";
                locationBtn.disabled = false;
                
                alert("Unable to determine your location address. Please enter it manually.");
            });
    }

    // Set up the geolocation button handler when the page loads
    document.addEventListener('DOMContentLoaded', setupGeolocation);
    
    // Also set up the handler after a short delay to ensure Gradio has initialized
    setTimeout(setupGeolocation, 1000);
    
    // And set it up again after a longer delay in case the UI is slow to load
    setTimeout(setupGeolocation, 3000);
    </script>
    """)
    
    # Set up event handler for event type changes without the problematic _js parameter
    event_type.change(
        fn=lambda x: None,  # Dummy function that doesn't do anything in Python
        inputs=[event_type],
        outputs=[]
    )
    
    # Set up the click event
    def handle_generate(
        event_type, time_available, time_preference, specific_date1, specific_time1, 
        specific_date2, specific_time2, specific_date3, specific_time3,
        budget, vibe, location_type, physical_activity, 
        partner_likes, partner_dislikes, partner_hobbies, partner_personality,
        self_preferences, misc_input, location, itinerary_state, current_recommendations
    ):
        # Process date/time preferences
        date_time_info = ""
        if time_preference != "Anytime":
            date_time_info = f"Time Preference: {time_preference}\n"
            
            if time_preference == "Specific dates":
                date_time_info += "Preferred Dates:\n"
                
                if specific_date1 and specific_time1:
                    date_time_info += f"- {specific_date1} at {specific_time1}\n"
                
                if specific_date2 and specific_time2:
                    date_time_info += f"- {specific_date2} at {specific_time2}\n"
                    
                if specific_date3 and specific_time3:
                    date_time_info += f"- {specific_date3} at {specific_time3}\n"
        
        # If user provided date/time preferences, add to misc_input
        if date_time_info:
            if misc_input:
                misc_input += "\n\n" + date_time_info
            else:
                misc_input = date_time_info
        
        # Store inputs for regeneration
        inputs = {
            "event_type": event_type,
            "time_available": time_available,
            "time_preference": time_preference,
            "specific_date1": specific_date1,
            "specific_time1": specific_time1,
            "specific_date2": specific_date2,
            "specific_time2": specific_time2,
            "specific_date3": specific_date3,
            "specific_time3": specific_time3,
            "budget": budget,
            "vibe": vibe,
            "location_type": location_type,
            "physical_activity": physical_activity,
            "partner_likes": partner_likes,
            "partner_dislikes": partner_dislikes,
            "partner_hobbies": partner_hobbies,
            "partner_personality": partner_personality,
            "self_preferences": self_preferences,
            "misc_input": misc_input,
            "location": location
        }
        
        # Extract place IDs from itinerary for map highlighting
        itinerary_place_ids = []
        for item in itinerary_state:
            if item['type'] == 'place' and 'place_id' in item:
                itinerary_place_ids.append(item['place_id'])
        
        main_content, timeline_content, map_html, place_details = generate_event_ideas(
            time_available, budget, vibe, location_type, physical_activity, 
            partner_likes, partner_dislikes, partner_hobbies, partner_personality,
            self_preferences, misc_input, location, event_type,
            itinerary_place_ids=itinerary_place_ids
        )
        
        # Extract event ideas from the content
        event_ideas = []
        
        # Extract titles and descriptions
        title_pattern = r'## Event Idea: (.*?)[\r\n]'
        titles = re.findall(title_pattern, main_content)
        
        # Extract timeline sections
        timeline_pattern = r'### Timeline:(.*?)(?=###|$)'
        timeline_matches = re.findall(timeline_pattern, main_content, re.DOTALL)
        
        # Extract cost information
        cost_pattern = r'\*\*Total Cost\*\*: \$([\d.]+)'
        costs = re.findall(cost_pattern, main_content)
        
        # Extract why it's a good fit
        fit_pattern = r'\*\*Why It\'s a Good Fit\*\*: (.*?)[\r\n]'
        fits = re.findall(fit_pattern, main_content)
        
        # Combine the extracted information
        for i in range(len(titles)):
            if i < len(timeline_matches) and i < len(costs) and i < len(fits):
                event_ideas.append({
                    "title": titles[i],
                    "timeline": timeline_matches[i].strip(),
                    "cost": costs[i],
                    "fit": fits[i],
                    "id": f"event_{i}"
                })
        
        # Store the recommendations and inputs
        current_recommendations_data = {
            "event_ideas": event_ideas,
            "place_details": place_details,
            "inputs": inputs
        }
        
        # Add buttons to add events to itinerary
        main_content_with_buttons = main_content
        for i, idea in enumerate(event_ideas):
            button_html = f"""
            <button onclick="addToItinerary('{idea['id']}')" class="add-to-itinerary-btn">
                Add to Itinerary
            </button>
            """
            # Add the button after each event idea title
            pattern = f"## Event Idea: {re.escape(idea['title'])}"
            replacement = f"## Event Idea: {idea['title']}\n{button_html}"
            main_content_with_buttons = re.sub(pattern, replacement, main_content_with_buttons)
        
        # Format place details for display
        place_info_html = ""
        if place_details:
            place_info_html = """
            <div class="recommended-places-header">
                <h3>Recommended Places</h3>
            </div>
            """
            
            for i, place in enumerate(place_details):
                name = place.get('name', 'Unknown Place')
                address = place.get('formatted_address', place.get('vicinity', 'No address available'))
                rating = place.get('rating', 'No rating')
                maps_url = place.get('url', place.get('maps_url', '#'))
                
                # Get busy status if available
                busy_status = ""
                if 'opening_hours' in place:
                    if place['opening_hours'].get('open_now', False):
                        busy_status = "Currently open"
                    else:
                        busy_status = "Currently closed"
                
                place_info_html += f"""
                <div class="place-card">
                    <h4 class="place-name">{name}</h4>
                    <p><strong>Address:</strong> {address}</p>
                    <p><strong>Rating:</strong> {rating}/5</p>
                    {f"<p><strong>Status:</strong> {busy_status}</p>" if busy_status else ""}
                    <p><a href="{maps_url}" target="_blank" class="maps-button">View on Google Maps</a></p>
                    <button onclick="addPlaceToItinerary('place_{i}', '{place.get('place_id', '')}')" class="add-to-itinerary-btn">
                        Add to Itinerary
                    </button>
                """
                
                # Add website if available
                if place.get('website'):
                    place_info_html += f"""
                    <p><strong>Website:</strong> <a href="{place['website']}" target="_blank" class="website-link">{place['website']}</a></p>
                    """
                
                # Add phone if available
                if place.get('formatted_phone_number'):
                    place_info_html += f"""
                    <p><strong>Phone:</strong> {place['formatted_phone_number']}</p>
                    """
                
                # Add opening hours if available
                if 'opening_hours' in place and 'weekday_text' in place['opening_hours']:
                    place_info_html += "<p><strong>Opening Hours:</strong></p><ul class='hours-list'>"
                    for day in place['opening_hours']['weekday_text']:
                        place_info_html += f"<li>{day}</li>"
                    place_info_html += "</ul>"
                
                # Add reviews if available
                if 'reviews' in place and place['reviews']:
                    place_info_html += "<p><strong>Top Review:</strong></p>"
                    review = place['reviews'][0]
                    author = review.get('author_name', 'Anonymous')
                    review_rating = review.get('rating', 'No rating')
                    text = review.get('text', 'No comment')
                    time = review.get('relative_time_description', '')
                    
                    place_info_html += f"""
                    <div class="review-box">
                        <p><strong>{author}</strong> - {review_rating}/5 ({time})</p>
                        <p>{text}</p>
                    </div>
                    """
                
                place_info_html += "</div>"
        
        # Render the current itinerary
        itinerary_html = render_itinerary(itinerary_state)
        
        # Add JavaScript for adding items to itinerary
        js_for_itinerary = f"""
        <script>
        // Store the current recommendations
        window.currentRecommendations = {json.dumps(current_recommendations_data)};
        
        function addToItinerary(id) {{
            // Find the event in the recommendations
            const event = window.currentRecommendations.event_ideas.find(e => e.id === id);
            if (event) {{
                // Create a custom event to trigger the Python function
                const event_data = {{
                    type: 'event',
                    id: id,
                    title: event.title,
                    timeline: event.timeline,
                    cost: event.cost,
                    fit: event.fit
                }};
                
                // Dispatch the event to Gradio
                document.dispatchEvent(new CustomEvent('add_to_itinerary', {{
                    detail: JSON.stringify(event_data)
                }}));
            }}
        }}
        
        function addPlaceToItinerary(id, placeId) {{
            // Extract the index from the id (format: place_X)
            const index = parseInt(id.split('_')[1]);
            if (!isNaN(index) && index >= 0 && index < window.currentRecommendations.place_details.length) {{
                const place = window.currentRecommendations.place_details[index];
                
                // Create a custom event to trigger the Python function
                const place_data = {{
                    type: 'place',
                    id: id,
                    place_id: placeId || place.place_id || '',
                    name: place.name || 'Unknown Place',
                    address: place.formatted_address || place.vicinity || 'No address available',
                    rating: place.rating || 'No rating',
                    url: place.url || place.maps_url || '#'
                }};
                
                // Dispatch the event to Gradio
                document.dispatchEvent(new CustomEvent('add_to_itinerary', {{
                    detail: JSON.stringify(place_data)
                }}));
            }}
        }}
        </script>
        """
        
        # Add the JavaScript to the main content
        main_content_with_buttons += js_for_itinerary
        
        return main_content_with_buttons, timeline_content, map_html, place_info_html, itinerary_html, current_recommendations_data
    
    generate_button.click(
        fn=handle_generate,
        inputs=[
            event_type,
            time_available, 
            time_preference,
            specific_date1,
            specific_time1,
            specific_date2,
            specific_time2,
            specific_date3,
            specific_time3,
            budget, 
            vibe, 
            location_type, 
            physical_activity, 
            partner_likes,
            partner_dislikes,
            partner_hobbies,
            partner_personality,
            self_preferences,
            misc_input,
            location,
            itinerary_state,
            current_recommendations
        ],
        outputs=[output, timeline_output, map_output, place_info, itinerary_output, current_recommendations]
    )
    
    # Set up custom event handlers for itinerary management
    itinerary_js_handlers = gr.HTML("""
    <script>
    // Set up event listeners for custom events
    document.addEventListener('add_to_itinerary', function(e) {
        // Find the hidden add item button and trigger it
        const addButton = document.querySelector('button[aria-label="Add Item"]');
        if (addButton) {
            // Set the value in the associated textbox
            const textbox = addButton.closest('.gradio-button').nextElementSibling;
            if (textbox) {
                textbox.value = e.detail;
                textbox.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Click the button
                addButton.click();
            }
        }
    });
    
    document.addEventListener('remove_from_itinerary', function(e) {
        // Find the hidden remove item button and trigger it
        const removeButton = document.querySelector('button[aria-label="Remove Item"]');
        if (removeButton) {
            // Set the value in the associated textbox
            const textbox = removeButton.closest('.gradio-button').nextElementSibling;
            if (textbox) {
                textbox.value = e.detail;
                textbox.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Click the button
                removeButton.click();
            }
        }
    });
    
    document.addEventListener('update_item_time', function(e) {
        // Find the hidden update time button and trigger it
        const updateButton = document.querySelector('button[aria-label="Update Time"]');
        if (updateButton) {
            // Set the value in the associated textbox
            const textbox = updateButton.closest('.gradio-button').nextElementSibling;
            if (textbox) {
                textbox.value = e.detail;
                textbox.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Click the button
                updateButton.click();
            }
        }
    });
    
    document.addEventListener('update_itinerary_order', function(e) {
        // Find the hidden update order button and trigger it
        const updateButton = document.querySelector('button[aria-label="Update Order"]');
        if (updateButton) {
            // Set the value in the associated textbox
            const textbox = updateButton.closest('.gradio-button').nextElementSibling;
            if (textbox) {
                textbox.value = e.detail;
                textbox.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Click the button
                updateButton.click();
            }
        }
    });
    
    document.addEventListener('regenerate_place', function(e) {
        // Find the hidden regenerate place button and trigger it
        const regenerateButton = document.querySelector('button[aria-label="Regenerate Place"]');
        if (regenerateButton) {
            // Set the value in the associated textbox
            const textbox = regenerateButton.closest('.gradio-button').nextElementSibling;
            if (textbox) {
                textbox.value = e.detail;
                textbox.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Click the button
                regenerateButton.click();
            }
        }
    });
    
    console.log('Itinerary event handlers loaded');
    </script>
    """)
    
    # Add the custom event handlers
    app.load(lambda: None, None, itinerary_js_handlers)
    
    # Instead of using JavaScript handlers that don't work well in tests,
    # we can mock these actions by having the add/remove functions directly
    # callable from test environments. The actual event handlers will be 
    # handled by the frontend code in production.
    
    # Mock button handlers for testing
    add_item_button = gr.Button("Add Item", visible=False)
    add_item_button.click(
        fn=add_to_itinerary,
        inputs=[itinerary_state, gr.Textbox(visible=False)],
        outputs=[itinerary_output, itinerary_state]
    )
    
    remove_item_button = gr.Button("Remove Item", visible=False)
    remove_item_button.click(
        fn=remove_from_itinerary,
        inputs=[itinerary_state, gr.Textbox(visible=False)],
        outputs=[itinerary_output, itinerary_state]
    )
    
    update_time_button = gr.Button("Update Time", visible=False)
    update_time_button.click(
        fn=update_item_time,
        inputs=[itinerary_state, gr.Textbox(visible=False)],
        outputs=[itinerary_output, itinerary_state]
    )
    
    update_order_button = gr.Button("Update Order", visible=False)
    update_order_button.click(
        fn=update_itinerary_order,
        inputs=[itinerary_state, gr.Textbox(visible=False)],
        outputs=[itinerary_output, itinerary_state]
    )
    
    regenerate_place_button = gr.Button("Regenerate Place", visible=False)
    regenerate_place_button.click(
        fn=regenerate_place,
        inputs=[itinerary_state, current_recommendations, gr.Textbox(visible=False)],
        outputs=[output, timeline_output, map_output, place_info, itinerary_output, itinerary_state]
    )
    
    # Set up the regenerate button
    regenerate_btn.click(
        fn=regenerate_recommendations,
        inputs=[current_recommendations, itinerary_state],
        outputs=[output, timeline_output, map_output, place_info, current_recommendations]
    )
    
    # Set up the export button
    export_btn.click(
        fn=export_itinerary_as_pdf,
        inputs=[itinerary_state],
        outputs=[gr.HTML(label="Printable Itinerary")]
    )
    
    # Set up the share button
    share_btn.click(
        fn=share_itinerary,
        inputs=[itinerary_state],
        outputs=[gr.HTML(label="Share Link")]
    )
    
    gr.Markdown("### How to use")
    gr.Markdown("""
    1. Select the type of event (casual dating, married, first date, etc.)
    2. Adjust the slider for your available time (in hours)
    3. **[OPTIONAL] Specify date and time preferences:**
       - Choose a general time frame like "This weekend" or "Next weekend"
       - OR select "Specific dates" to enter up to 3 exact date and time options
    4. Set your budget using the slider (up to $500)
    5. Pick the vibe(s) you're looking for
    6. Select preferred location type(s)
    7. Set your preferred level of physical activity (1-10)
    8. **Enter your location for area-specific suggestions and interactive maps**
    9. Fill in the optional partner preference fields
    10. Add your own preferences (optional)
    11. Include any miscellaneous information if needed
    12. Click 'Generate Event Ideas' to get personalized recommendations with timeline and cost breakdown
    """)
    
    # Add footer
    gr.HTML('<div class="footer">Perfect Event Generator - Created with ❤️</div>')
    
    # Add JavaScript to handle conditional visibility of participants field
    gr.HTML("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Set up the relationship type change handler
        setupRelationshipTypeHandler();
        observeRelationshipTypeChanges();
    });
    
    function setupRelationshipTypeHandler() {
        const relationshipDropdown = document.querySelector('select[data-testid="dropdown"]');
        if (relationshipDropdown) {
            relationshipDropdown.addEventListener('change', function() {
                toggleParticipantsVisibility(this.value);
            });
            
            // Initial check
            toggleParticipantsVisibility(relationshipDropdown.value);
        }
    }
    
    function toggleParticipantsVisibility(value) {
        const participantsContainer = document.querySelector('input[aria-label="Number of Participants"]').closest('.gradio-container');
        
        if (value === "Night with the Girls" || value === "Night with the Boys" || value === "Afterwork") {
            participantsContainer.style.display = 'block';
        } else {
            participantsContainer.style.display = 'none';
        }
    }
    
    function observeRelationshipTypeChanges() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    for (let i = 0; i < mutation.addedNodes.length; i++) {
                        const node = mutation.addedNodes[i];
                        if (node.querySelector && node.querySelector('select[data-testid="dropdown"]')) {
                            setupRelationshipTypeHandler();
                            break;
                        }
                    }
                }
            });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    }
    </script>
    """)
    
    # Add JavaScript to handle clickable places
    gr.HTML("""
    <script>
    // Wait for DOM to be fully loaded and then set up observers
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM fully loaded');
        setupPlaceClickHandlers();
        observeDOMChanges();
    });
    
    // Function to set up click handlers for clickable places
    function setupPlaceClickHandlers() {
        console.log('Setting up click handlers');
        const placeElements = document.querySelectorAll('.clickable-place');
        console.log('Found ' + placeElements.length + ' clickable places');
        
        placeElements.forEach(element => {
            // Remove any existing click handlers first
            element.removeEventListener('click', togglePlaceDetails);
            // Add new click handler
            element.addEventListener('click', togglePlaceDetails);
        });
    }
    
    // Toggle place details visibility
    function togglePlaceDetails(e) {
        e.preventDefault();
        const placeId = this.getAttribute('data-place-id');
        const placeDetails = document.getElementById(placeId);
        
        if (!placeDetails) {
            console.error('Place details not found for ID: ' + placeId);
            return;
        }
        
        // Toggle visibility
        if (placeDetails.style.display === 'none' || !placeDetails.style.display) {
            placeDetails.style.display = 'block';
        } else {
            placeDetails.style.display = 'none';
        }
    }
    
    // Observe DOM changes to set up handlers for dynamically added elements
    function observeDOMChanges() {
        console.log('Setting up MutationObserver');
        const observer = new MutationObserver(function(mutations) {
            let shouldSetupHandlers = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    for (let i = 0; i < mutation.addedNodes.length; i++) {
                        const node = mutation.addedNodes[i];
                        if (node.classList && 
                            (node.classList.contains('timeline-container') || 
                             node.querySelector && node.querySelector('.clickable-place'))) {
                            shouldSetupHandlers = true;
                            break;
                        }
                    }
                }
            });
            
            if (shouldSetupHandlers) {
                console.log('Found new content with clickable places');
                setupPlaceClickHandlers();
            }
        });
        
        // Start observing the document with the configured parameters
        observer.observe(document.body, { childList: true, subtree: true });
    }
    
    // Function to update marker color on the map
    function updateMarkerColor(placeId, color) {
        console.log('Updating marker color for', placeId, 'to', color);
        // Find the map iframe
        const mapIframe = document.querySelector('.map-output iframe');
        if (!mapIframe) {
            console.error('Map iframe not found');
            return;
        }
        
        // Send a message to the iframe
        try {
            mapIframe.contentWindow.postMessage({
                action: 'updateMarkerColor',
                placeId: placeId,
                color: color
            }, '*');
        } catch (e) {
            console.error('Error sending message to map iframe:', e);
        }
    }
    </script>
    """)

# Launch the app with server settings for Docker
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7861) 