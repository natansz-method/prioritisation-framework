import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Define CSV file name for persistence
CSV_FILE = "group_data.csv"

# Predefined groups and colors
group_colors = {"Group 1": "blue", "Group 2": "green", "Group 3": "red"}
average_color = "violet"  # Set average points color to pink
group_names = list(group_colors.keys())
num_solutions = 16  # Fixed number of solutions, labeled 1 to 16

# Function to create a new CSV file with default values if it doesn't exist
def initialize_csv():
    data = []
    for group in group_names:
        for solution in range(1, num_solutions + 1):
            # Default complexity and value at center [5, 5]
            data.append([group, solution, 5, 5])
    df = pd.DataFrame(data, columns=["Group", "Solution", "Complexity", "Value"])
    df.set_index(["Group", "Solution"], inplace=True)
    df.to_csv(CSV_FILE)

# Load existing data from CSV file if it exists, or initialize a new DataFrame
if "all_groups_points" not in st.session_state:
    if os.path.exists(CSV_FILE):
        # Load data from CSV
        df = pd.read_csv(CSV_FILE)
        # Convert the DataFrame to the required nested dictionary format
        st.session_state.all_groups_points = {
            group: {
                int(solution): [row["Complexity"], row["Value"]]
                for solution, row in group_df.groupby("Solution").first().iterrows()
            }
            for group, group_df in df.groupby("Group")
        }
    else:
        # Initialize CSV file with default values if it doesn't exist
        initialize_csv()
        st.session_state.all_groups_points = {group: {i: [5, 5] for i in range(1, num_solutions + 1)} for group in group_names}

# Function to save current session state to CSV
def save_to_csv():
    # Convert session state data to DataFrame
    data = []
    for group, solutions in st.session_state.all_groups_points.items():
        for solution, (complexity, value) in solutions.items():
            data.append([group, solution, complexity, value])
    df = pd.DataFrame(data, columns=["Group", "Solution", "Complexity", "Value"])
    df.set_index(["Group", "Solution"], inplace=True)
    df.to_csv(CSV_FILE)

# Sidebar input for adding values for each group
st.sidebar.header("Input Scores for Each Group")
selected_group = st.sidebar.selectbox("Select Group to Add/Update Scores", group_names)

# Ensure the selected group has entries in session state and initialize if missing
if selected_group not in st.session_state.all_groups_points:
    st.session_state.all_groups_points[selected_group] = {i: [5, 5] for i in range(1, num_solutions + 1)}

# Update session state with new input values for the selected group and save to CSV
for i in range(1, num_solutions + 1):
    # Fetch current complexity and value, defaulting to [5, 5] if missing
    current_values = st.session_state.all_groups_points[selected_group].get(i, [5, 5])
    current_complexity = current_values[0]
    current_value = current_values[1]
    x = st.sidebar.slider(f"Complexity for Solution {i}", 0.0, 10.0, float(current_complexity), 0.1, key=f"{selected_group}_x_{i}")
    y = st.sidebar.slider(f"Value for Solution {i}", 0.0, 10.0, float(current_value), 0.1, key=f"{selected_group}_y_{i}")
    st.session_state.all_groups_points[selected_group][i] = [x, y]  # Update session state

save_to_csv()  # Save all changes to CSV

# Function to calculate average points across selected groups
def calculate_average_points(selected_groups):
    average_points = {}
    point_counts = {i: 0 for i in range(1, num_solutions + 1)}
    
    for group in selected_groups:
        group_points = st.session_state.all_groups_points[group]
        for label, coords in group_points.items():
            x, y = coords
            if label not in average_points:
                average_points[label] = [0, 0]
            average_points[label][0] += x
            average_points[label][1] += y
            point_counts[label] += 1
    
    # Calculate the average for each solution
    for label, coords in average_points.items():
        count = point_counts[label]
        average_points[label] = [coord / count for coord in coords]
    
    return average_points

# Function to plot points on the styled grid
def plot_points_on_styled_grid(selected_groups, show_average=False, hide_groups=False):
    # Set up the plot with a larger figure size
    fig, ax = plt.subplots(figsize=(10, 10))  # Increased size for a larger view
    ax.set_xlim(-0.2, 10.2)
    ax.set_ylim(-0.2, 10.2)

    # Remove the box frame around the plot
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Move x and y axes to the center
    ax.axhline(5, color='black', linewidth=1, zorder=1)
    ax.axvline(5, color='black', linewidth=1, zorder=1)

    # Add arrows to the axes
    ax.annotate('', xy=(10, 5), xytext=(0, 5), arrowprops=dict(arrowstyle="->", color='black', lw=1.5), zorder=1)
    ax.annotate('', xy=(5, 10), xytext=(5, 0), arrowprops=dict(arrowstyle="->", color='black', lw=1.5), zorder=1)

    # Label axes with 'High' and 'Low' indicators
    ax.text(11.8, 5, 'High Complexity', ha='center', va='center', fontsize=18, fontweight='bold')
    ax.text(-1.8, 5, 'Low Complexity', ha='center', va='center', fontsize=18, fontweight='bold')
    ax.text(5, 10.3, 'High Value', ha='center', va='center', fontsize=18, fontweight='bold')
    ax.text(5, -0.3, 'Low Value', ha='center', va='center', fontsize=18, fontweight='bold')

    # Draw concentric circles for radial axes
    for radius in [2.5, 5]:
        circle = plt.Circle((5, 5), radius, color='lightgray', fill=False, linewidth=0.5, zorder=0)
        ax.add_artist(circle)

    # Plot each selected group's points with its assigned color if not hiding
    if not hide_groups or not show_average:
        for group in selected_groups:
            color = group_colors[group]
            for label, coords in st.session_state.all_groups_points[group].items():
                x, y = coords
                # Plot square points with a higher zorder so they appear above the grid lines
                ax.scatter(x, y, color=color, s=300, marker='s', zorder=2)
                # Overlay the label on top of the square point
                ax.text(x, y, str(label), color='white', fontsize=10, ha='center', va='center', zorder=3, fontweight="bold")

    # Plot average points if show_average is True
    if show_average:
        average_points = calculate_average_points(selected_groups)
        for label, coords in average_points.items():
            x, y = coords
            ax.scatter(x, y, color=average_color, s=300, marker='o', zorder=3)
            ax.text(x, y, str(label), color='black', fontsize=10, ha='center', va='center', fontweight='bold')

    return fig

# Main interface to toggle group visibility and average
st.header("View Groups and Average")
selected_view_groups = st.multiselect("Select Group(s) to View", group_names, default=[])
show_average = st.checkbox("Show Average", value=False)
hide_groups = st.checkbox("Hide Group Values when Showing Average", value=False)

# Plot the selected groups and average if toggled on
st.pyplot(plot_points_on_styled_grid(selected_view_groups, show_average, hide_groups))

# Display DataFrame with complexity and value scores for each solution
table_data = []
for solution in range(1, num_solutions + 1):
    row = {"Solution": solution}
    for group in group_names:
        complexity, value = st.session_state.all_groups_points[group][solution]
        row[f"{group}_Complexity"] = complexity
        row[f"{group}_Value"] = value
    
    # Calculate average complexity and value
    avg_complexity = sum(row[f"{group}_Complexity"] for group in group_names) / len(group_names)
    avg_value = sum(row[f"{group}_Value"] for group in group_names) / len(group_names)
    row["Average_Complexity"] = avg_complexity
    row["Average_Value"] = avg_value

    # Calculate Value/Complexity Score
    row["Value/Complexity Score"] = avg_value / avg_complexity if avg_complexity != 0 else 0
    table_data.append(row)

# Convert to DataFrame and display with sorting
df_table = pd.DataFrame(table_data)
st.dataframe(df_table)

