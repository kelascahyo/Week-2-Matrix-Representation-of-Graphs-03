# app.py
import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
import numpy as np
import json

# Page Setup
st.set_page_config(page_title="High School Graph AI Course", layout="wide")

st.title("🕸️ Interactive Graph AI Crash Course")
st.write("Welcome! This dashboard uses **NetworkX** (Python's graph brain) and **D3.js** (JavaScript's physics engine) to show you exactly how computers see networks.")

# --- CREATE A CORE GRAPH TO USE ACROSS EXAMPLES ---
# Let's create a classic high school scenario: 4 friends
# 0: Tom, 1: Jerry, 2: Spike, 3: Tyke
G = nx.Graph()
names = {0: "Tom", 1: "Jerry", 2: "Spike", 3: "Tyke"}
G.add_nodes_from(names.keys())
core_edges = [(0, 1), (1, 2), (2, 3), (0, 2)] # Tom-Jerry, Jerry-Spike, Spike-Tyke, Tom-Spike
G.add_edges_from(core_edges)

# Package data for D3.js FORCE GRAPH
d3_data = {
    "nodes": [{"id": str(n), "name": names[n]} for n in G.nodes()],
    "links": [{"source": str(u), "target": str(v)} for u, v in G.edges()]
}

# Shared D3.js Visualizer Function
def render_d3_graph(data_dict, height=250):
    d3_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{ margin: 0; background-color: transparent; }}
            .node {{ fill: #FF4B4B; stroke: #FFF; stroke-width: 2.5px; cursor: grab; }}
            .link {{ stroke: #555; stroke-opacity: 0.6; stroke-width: 3px; }}
            text {{ font-family: sans-serif; font-size: 14px; font-weight: bold; fill: #31333F; }}
        </style>
    </head>
    <body>
        <svg width="400" height="{height}"></svg>
        <script>
            const data = {json.dumps(data_dict)};
            const svg = d3.select("svg");
            const width = +svg.attr("width"), height = +svg.attr("height");

            const sim = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links).id(d => d.id).distance(80))
                .force("charge", d3.forceManyBody().strength(-150))
                .force("center", d3.forceCenter(width / 2, height / 2));

            const link = svg.append("g").selectAll("line").data(data.links).enter().append("line").attr("class", "link");
            const node = svg.append("g").selectAll("circle").data(data.nodes).enter().append("circle").attr("class", "node").attr("r", 14)
                .call(d3.drag().on("start", dragS).on("drag", dragging).on("end", dragE));
            const text = svg.append("g").selectAll("text").data(data.nodes).enter().append("text").attr("dx", 18).attr("dy", 5).text(d => d.name);

            sim.on("tick", () => {{
                link.attr("x1", d => d.source.x).attr("y1", d => d.source.y).attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                node.attr("cx", d => d.x).attr("cy", d => d.y);
                text.attr("x", d => d.x).attr("y", d => d.y);
            }});

            function dragS(e, d) {{ if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }}
            function dragging(e, d) {{ d.fx = e.x; d.fy = e.y; }}
            function dragE(e, d) {{ if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }}
        </script>
    </body>
    </html>
    """
    components.html(d3_html, height=height+20, scrolling=False)

# --- NAVIGATION TABS ---
tab_concepts, tab_math = st.tabs(["🧩 Core Concepts", "🧮 The Math Focus"])

# ==========================================
# TAB 1: CORE CONCEPTS
# ==========================================
with tab_concepts:
    
    # 1. Adjacency Matrix
    st.header("1. Adjacency Matrix (The Grid)")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("""
        **The Narrative:** Think of this like a Battleship grid or a distance chart. Because computers don't have eyes, they can't 'see' the lines connecting our characters. Instead, we build a grid where every row and column represents a person. If two people are friends, we drop a `1` at their intersection. If they aren't, it stays a `0`.
        """)
        st.markdown("**NetworkX Generated Adjacency Matrix:**")
        st.code(str(nx.to_numpy_array(G, dtype=int)))
    with col2:
        st.markdown("**The Visual Network:**")
        render_d3_graph(d3_data)

    st.write("---")

    # 2. Edge List
    st.header("2. Edge List (The Cheat Sheet)")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("""
        **The Narrative:** Grids are nice, but writing down a bunch of zeros feels like wasted effort. What if we just write down a clean, straightforward cheat sheet of who is connected to whom? An Edge List does exactly that. It's just a simple list of pairs.
        """)
        st.markdown("**NetworkX Extracted Edge List:**")
        st.code(str(list(G.edges())))
    with col2:
        # Static representation showing name mapping
        st.markdown("**What it represents:**")
        st.json([f"{names[u]} ↔️ {names[v]}" for u, v in G.edges()])

    st.write("---")

    # 3. Sparse Matrices
    st.header("3. Sparse Matrices (Saving Computer Memory)")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("""
        **The Narrative:** Imagine you have 1,000 followers on social media. That's a lot! But there are *billions* of people on the platform you don't follow. If the computer built a complete grid (Adjacency Matrix) for the whole internet, it would contain trillions of useless `0`s and instantly crash your computer. 
        
        A **Sparse Matrix** is a clever programming trick. It tells the computer: *'Assume the whole world is full of zeros. I will only save the memory addresses where the 1s are hiding.'*
        """)
        # Getting a true SciPy sparse layout representation
        sparse_rep = nx.to_scipy_sparse_array(G)
        st.markdown("**How the computer saves a Sparse Matrix (Coordinate Format):**")
        st.code(str(sparse_rep))
    with col2:
        st.metric(label="Total Connections Maintained", value=len(G.edges()))
        st.caption("Instead of holding a 4x4 grid (16 entries), a sparse matrix only cares about these 4 active connection positions!")

    st.write("---")

    # 4. Feature Matrices
    st.header("4. Feature Matrices (The Profile Data)")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("""
        **The Narrative:** Knowing who talks to whom is only half the battle. To actually use AI, we need to know *who these nodes are*. A Feature Matrix is a completely separate spreadsheet that tracks personal profiles. Row 0 belongs to Node 0 (Tom), Row 1 belongs to Node 1 (Jerry), and so on.
        """)
        
        # Simulating data features: [Age, Gamers (1=Yes/0=No), City Code]
        feature_matrix = np.array([
            [16, 1, 101],  # Tom
            [15, 1, 101],  # Jerry
            [18, 0, 102],  # Spike
            [14, 0, 102]   # Tyke
        ])
        st.markdown("**The Feature Spreadsheet Matrix:**")
        st.code(str(feature_matrix))
    with col2:
        st.markdown("**Profile Legend:**")
        st.dataframe({
            "Name": ["Tom", "Jerry", "Spike", "Tyke"],
            "Age": [16, 15, 18, 14],
            "Is Gamer": ["Yes", "Yes", "No", "No"],
            "City ID": [101, 101, 102, 102]
        })

    st.write("---")

    # 5. Laplacian Matrix
    st.header("5. Laplacian Matrix (The Graph Physics)")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("""
        **The Narrative:** This is where things get beautiful. If you count up how many friends each person has (their 'Degree') and subtract our Adjacency Matrix grid from it, you get the Laplacian Matrix. 
        
        In graph physics, the Laplacian acts like an internal structural map showing hills and valleys. It physically tells us how easily information can flow through the network or if certain groups are completely isolated in their own social echo chambers.
        """)
        st.markdown("**NetworkX Calculated Laplacian Matrix ($L = D - A$):**")
        st.code(str(nx.laplacian_matrix(G).toarray()))
    with col2:
        st.markdown("**Friend Counts (Degree Matrix Values):**")
        for node_idx, deg in G.degree():
            st.write(f"📊 {names[node_idx]} has {deg} connection(s)")


# ==========================================
# TAB 2: THE MATH FOCUS
# ==========================================
with tab_math:
    st.header("🧮 How Graph AIs Actually Think")
    
    # 1. Message Propagation & Matrix Multiplication
    st.subheader("Message Propagation & Matrix Multiplication (Passing Notes)")
    st.write("""
    **The Narrative:** Imagine you want to pick a movie to watch. Instead of looking at global reviews, you ask your immediate friends what their favorite movie genre is, blend their choices with your own preference, and update your choice. In Graph AI, this is called **Message Passing**.
    
    When an AI runs this process, it uses **Matrix Multiplication**. By multiplying our Adjacency Matrix (who knows who) by our Feature Matrix (their profiles), the computer calculates this note-passing step for *every single person in the network simultaneously* in a single millisecond!
    """)
    
    # Simple interactive showcase of feature aggregation
    feature_opinions = np.array([[10], [20], [30], [40]]) # Custom simple values for Tom, Jerry, Spike, Tyke
    adj = nx.to_numpy_array(G, dtype=int)
    propagated = np.dot(adj, feature_opinions)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown("**Adjacency Matrix ($A$)**")
        st.code(str(adj))
    with col_m2:
        st.markdown("**Friend Opinions ($X$)**")
        st.code(str(feature_opinions))
    with col_m3:
        st.markdown("**Aggregated Output ($A \cdot X$)**")
        st.code(str(propagated))
        st.caption("Look at Row 3 (Tyke). Tyke is only connected to Spike (value 30). So Tyke's aggregated incoming message value is exactly 30!")

    st.write("---")

    # 2. Eigenvectors
    st.subheader("Eigenvectors (The Vibe Check)")
    col_eig1, col_eig2 = st.columns([2, 1])
    with col_eig1:
        st.write("""
        **The Narrative:** If you look at a massive graph of a school with 5,000 students, it just looks like a giant, messy hairball. You can't see what's going on with your bare eyes. 
        
        **Eigenvectors** are the ultimate 'vibe check' math tool. Without ever drawing a visual picture, calculating the eigenvectors of a graph matrix mathematically flags the core structural 'backbones' of the network. It tells the computer exactly who the key influencers are and how cliques naturally cluster together based purely on structural patterns.
        """)
        
        # Calculate real mathematical eigenvectors of the adjacency matrix using NumPy
        eigenvalues, eigenvectors = np.linalg.eigh(adj)
        # Take the top principal structural eigenvector
        top_eigenvector = eigenvectors[:, -1]
        
        st.markdown("**Calculated Structural Importance Values (Top Eigenvector Vector Columns):**")
        for i, val in enumerate(top_eigenvector):
            st.write(f"🔑 **{names[i]}**: {val:.4f}")
    with col_eig2:
        st.markdown("**What the AI infers:**")
        st.info("Notice how Tom and Spike naturally show higher numbers? That's because they are the structural anchors holding our little 4-node network together!")
