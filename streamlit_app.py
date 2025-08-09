import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Show app title and description.
st.set_page_config(page_title="MLF CREDIT MANAGEMENT QUERY SYSTEM", page_icon="🎫")
st.title("🎫 MLF CREDIT MANAGEMENT QUERY SYSTEM")

# Add role selector at the top
st.sidebar.header("🔐 User Access")
user_role = st.sidebar.selectbox(
    "Select your role:",
    ["Branch Manager", "CM Staff"],
    help="Choose your role to access appropriate features"
)

st.write(
    """
    Please submit your queries by adding a ticket below. For queries that require templates such as Mobile Money, Change of Product or First RM, please upload the excel files.
    """
)

# Create a random Pandas dataframe with existing tickets.
if "df" not in st.session_state:

    # Set seed for reproducibility.
    np.random.seed(42)

    # Make up some fake issue descriptions.
    issue_descriptions = [
        "Network connectivity issues in the office",
        "Software application crashing on startup",
        "Printer not responding to print commands",
        "Email server downtime",
        "Data backup failure",
        "Login authentication problems",
        "Website performance degradation",
        "Security vulnerability identified",
        "Hardware malfunction in the server room",
        "Employee unable to access shared files",
        "Database connection failure",
        "Mobile application not syncing data",
        "VoIP phone system issues",
        "VPN connection problems for remote employees",
        "System updates causing compatibility issues",
        "File server running out of storage space",
        "Intrusion detection system alerts",
        "Inventory management system errors",
        "Customer data not loading in CRM",
        "Collaboration tool not sending notifications",
    ]

    # Generate the dataframe with 100 rows/tickets.
    data = {
        "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
        "Issue": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "Date Submitted": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
        "Attached Files": ["" for _ in range(100)],
        "CM Notes": ["" for _ in range(100)],
    }
    df = pd.DataFrame(data)

    # Save the dataframe in session state (a dictionary-like object that persists across
    # page runs). This ensures our data is persisted when the app updates.
    st.session_state.df = df

# Initialize file storage in session state
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}


# Show a section to add a new ticket.
st.header("Submit a Query")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_ticket_form"):
    issue = st.text_area("Describe the issue")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("Submit")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    recent_ticket_number = int(max(st.session_state.df.ID.split("-")[1]))
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue": issue,
                "Status": "Open",
                "Priority": priority,
                "Date Submitted": today,
                "Attached Files": "",
                "CM Notes": "",
            }
        ]
    )

    # Show a little success message.
    st.write("Ticket submitted! Here are the ticket details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Show section to upload Excel/CSV files.
st.header("Upload Template Files")
st.write("Upload Excel (.xlsx, .xls) or CSV files for queries that require templates such as Mobile Money, Change of Product, or First RM.")

uploaded_file = st.file_uploader(
    "Choose a file",
    type=['csv', 'xlsx', 'xls'],
    help="Upload any CSV or Excel file. The data will be added to your tickets dataset as-is."
)

if uploaded_file is not None:
    try:
        # Determine file type and read accordingly
        if uploaded_file.name.endswith('.csv'):
            df_uploaded = pd.read_csv(uploaded_file)
        else:
            df_uploaded = pd.read_excel(uploaded_file)
        
        # Show preview of uploaded data
        st.write("**Preview of uploaded data:**")
        st.dataframe(df_uploaded.head(), use_container_width=True, hide_index=True)
        
        # Generate IDs for new tickets if not present
        if 'ID' not in df_uploaded.columns:
            recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
            df_uploaded['ID'] = [f"TICKET-{recent_ticket_number + i + 1}" for i in range(len(df_uploaded))]
        
        # Add new columns if they don't exist
        if 'Attached Files' not in df_uploaded.columns:
            df_uploaded['Attached Files'] = uploaded_file.name
        if 'CM Notes' not in df_uploaded.columns:
            df_uploaded['CM Notes'] = ""
        
        # Store the uploaded file in session state
        for query_id in df_uploaded['ID']:
            st.session_state.uploaded_files[query_id] = {
                'filename': uploaded_file.name,
                'file_data': uploaded_file.getvalue(),
                'file_type': uploaded_file.type
            }
        
        # Show final data to be added
        st.write("**Data to be added:**")
        st.dataframe(df_uploaded, use_container_width=True, hide_index=True)
        
        # Add upload button
        if st.button("Add uploaded tickets"):
            # Append to existing dataframe
            st.session_state.df = pd.concat([df_uploaded, st.session_state.df], axis=0)
            st.success(f"Successfully added {len(df_uploaded)} tickets with attached file: {uploaded_file.name}")
            
            # Clear the uploaded file
            st.rerun()
                
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        st.write("Please make sure your file is properly formatted and try again.")

# Show section to view and edit existing tickets in a table.
st.header("Existing Queries")
st.write(f"Number of queries: `{len(st.session_state.df)}`")

# Add file download and notes functionality for CM Staff
if user_role == "CM Staff":
    st.subheader("📁 File Management & Notes")
    
    # File download section
    st.write("**Download attached files:**")
    queries_with_files = [query_id for query_id in st.session_state.df["ID"] 
                         if query_id in st.session_state.uploaded_files]
    
    if queries_with_files:
        for query_id in queries_with_files:
            file_info = st.session_state.uploaded_files[query_id]
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{query_id}**: {file_info['filename']}")
            with col2:
                st.download_button(
                    label="📥 Download",
                    data=file_info['file_data'],
                    file_name=file_info['filename'],
                    mime=file_info['file_type'],
                    key=f"download_{query_id}"
                )
    else:
        st.write("No files attached to queries yet.")
    
    # Notes section
    st.write("**Add notes for Branch Managers to see:**")
    with st.form("add_cm_notes_form"):
        selected_query = st.selectbox(
            "Select query to add notes:",
            options=st.session_state.df["ID"].tolist(),
            help="Choose a query ID to add notes visible to Branch Managers"
        )
        notes = st.text_area(
            "CM Notes (visible to Branch Managers):",
            help="Add notes about this query that Branch Managers can see"
        )
        add_notes = st.form_submit_button("Add Notes")
    
    if add_notes and notes.strip():
        # Update the notes for the selected query
        query_index = st.session_state.df[st.session_state.df["ID"] == selected_query].index[0]
        st.session_state.df.loc[query_index, "CM Notes"] = notes
        st.success(f"✅ Notes added to {selected_query}")
        st.rerun()
    
    # Add status change tracking
    st.subheader("📊 Status Change Summary")
    
    # Count queries by status
    status_counts = st.session_state.df["Status"].value_counts()
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Open", status_counts.get("Open", 0))
    with col2:
        st.metric("In Progress", status_counts.get("In Progress", 0))
    with col3:
        st.metric("On Hold", status_counts.get("On Hold", 0))
    with col4:
        st.metric("Resolved", status_counts.get("Resolved", 0))
    with col5:
        st.metric("Closed", status_counts.get("Closed", 0))

if user_role == "CM Staff":
    st.info(
        "You can edit the queries by double clicking on a cell. Note how the plots below "
        "update automatically! You can also sort the table by clicking on the column headers.",
        icon="✍️",
    )
else:
    st.info(
        "You can view your queries and their current status. The table below shows all queries "
        "and you can sort by clicking on the column headers.",
        icon="👁️",
    )

# Show different interfaces based on user role
if user_role == "CM Staff":
    st.info("🔧 **CM Staff Mode**: You can edit query statuses and priorities. Changes are saved automatically.", icon="🔧")
    
    # Show the tickets dataframe with `st.data_editor` for CM Staff
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                help="Query status - CM Staff can change this",
                options=["Open", "In Progress", "Closed", "Resolved", "On Hold"],
                required=True,
            ),
            "Priority": st.column_config.SelectboxColumn(
                "Priority",
                help="Priority level - CM Staff can change this",
                options=["High", "Medium", "Low", "Critical"],
                required=True,
            ),
            "CM Notes": st.column_config.TextColumn(
                "CM Notes",
                help="Notes from CM Staff visible to Branch Managers"
            ),
        },
        # Disable editing the ID, Date Submitted, and Attached Files columns.
        disabled=["ID", "Date Submitted", "Attached Files"],
        key="cm_staff_editor"
    )
    
    # Save changes automatically
    if edited_df is not None and not edited_df.equals(st.session_state.df):
        # Track what changed
        changed_queries = []
        for idx, row in edited_df.iterrows():
            if not st.session_state.df.iloc[idx].equals(row):
                changed_queries.append(row["ID"])
        
        st.session_state.df = edited_df
        
        if changed_queries:
            st.success(f"✅ Query statuses updated successfully for: {', '.join(changed_queries)}")
            
            # Show what changed
            with st.expander("📋 View Changes Made"):
                for query_id in changed_queries:
                    new_row = edited_df[edited_df["ID"] == query_id].iloc[0]
                    st.write(f"**{query_id}**: Status: {new_row['Status']}, Priority: {new_row['Priority']}")
        
else:
    st.info("👤 **Branch Manager Mode**: You can view your queries and their current status. Contact CM Staff for status changes.", icon="👤")
    
    # Show CM Notes prominently for Branch Managers
    st.subheader("📝 Notes from CM Staff")
    queries_with_notes = st.session_state.df[st.session_state.df["CM Notes"].str.strip() != ""]
    if not queries_with_notes.empty:
        for _, row in queries_with_notes.iterrows():
            with st.expander(f"📋 {row['ID']} - {row['Status']}"):
                st.write(f"**Issue:** {row['Issue']}")
                st.write(f"**CM Notes:** {row['CM Notes']}")
                if row['Attached Files']:
                    st.write(f"**Attached File:** {row['Attached Files']}")
    else:
        st.write("No notes from CM Staff yet.")
    
    # Show attached files for download
    st.subheader("📁 Attached Files")
    queries_with_files = [query_id for query_id in st.session_state.df["ID"] 
                         if query_id in st.session_state.uploaded_files]
    if queries_with_files:
        for query_id in queries_with_files:
            file_info = st.session_state.uploaded_files[query_id]
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{query_id}**: {file_info['filename']}")
            with col2:
                st.download_button(
                    label="📥 Download",
                    data=file_info['file_data'],
                    file_name=file_info['filename'],
                    mime=file_info['file_type'],
                    key=f"branch_download_{query_id}"
                )
    else:
        st.write("No files attached to queries yet.")
    
    # Show read-only view for Branch Managers
    st.subheader("📊 All Queries")
    st.dataframe(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn(
                "Status",
                help="Current status of your query"
            ),
            "Priority": st.column_config.TextColumn(
                "Priority",
                help="Priority level of your query"
            ),
            "CM Notes": st.column_config.TextColumn(
                "CM Notes",
                help="Notes from CM Staff about your query"
            ),
            "Attached Files": st.column_config.TextColumn(
                "Attached Files",
                help="Files attached to your query"
            ),
        }
    )
    
    # Use the original dataframe for statistics since it's not editable
    edited_df = st.session_state.df

# Show some metrics and charts about the ticket.
st.header("Query Statistics")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
col1.metric(label="Number of open queries", value=num_open_tickets, delta=10)
col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
col3.metric(label="Average resolution time (hours)", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("##### Query status per month")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Current query priorities")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
