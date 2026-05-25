# app.py
import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
import json

st.set_page_config(page_title="High School Graph AI Course", layout="wide")

st.title("🕸️ Week 2: Turning Graphs into AI-Readable Math!")
st.write("Use the checkboxes to connect nodes. Watch how Python turns your visual lines into a grid of 0s and 1s!")

# Step 1: User creates the graph connections
st.header("Step 1: Create Your Social Network Connections")
num_nodes = st.slider("How many people (nodes) in your network?", min_value=3, max_value=6, value=4)

edges = []
cols = st.columns(3)
col_idx = 0

# Generate checkboxes for every possible connection pair
for i in range(num_nodes):
    for j in range(i + 1, num_nodes):
        with cols[col_idx % 3]:
            # Default connect a few nodes so it isn't empty at the start
            default_connect = (i == 0 or j == i + 1)
            if st.checkbox(f"Connect Node {i} ↔️ Node {j}", value=default_connect, key=f"edge_{i}_{j}"):
                edges.append((i, j))
        col_idx += 1

# Step 2: NetworkX processes the data math behind the scenes
G = nx.Graph()
G.add_nodes_from(range(num_nodes))
G.add_edges_from(edges)

# Create the binary math matrix
numpy_matrix = nx.to_numpy_array(G, dtype=int)

# Package data for the interactive D3 visualizer
d3_data = {
    "nodes": [{"id": str(n), "name": f"Node {n}"} for n in G.nodes()],
    "links": [{"source": str(u), "target": str(v)} for u, v in G.edges()]
}

st.write("---")
layout_col1, layout_col2 = st.columns(2)

with layout_col1:
    st.header("Step 2: What the Computer Sees (Math)")
    
    st.markdown("**1. The Adjacency Matrix Grid**")
    st.caption("Look closely: a '1' means connected, a '0' means open air!")
    st.code(str(numpy_matrix))
    
    st.markdown("**2. The Edge List Cheat Sheet**")
    st.code(str(list(G.edges())))

with layout_col2:
    st.header("Step 3: Interactive Live Graph Visual")
    st.caption("You can click and drag these nodes around! The physics are driven by D3.js.")
    
    # Injection of raw interactive JavaScript D3 canvas inside our application page
    d3_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{ margin: 0; background-color: transparent; }}
            .node {{ fill: #FF4B4B; stroke: #FFF; stroke-width: 2.5px; cursor: grab; }}
            .node:active {{ cursor: grabbing; }}
            .link {{ stroke: #555; stroke-opacity: 0.6; stroke-width: 3px; }}
            text {{ font-family: sans-serif; font-size: 14px; font-weight: bold; fill: #31333F; }}
        </style>
    </head>
    <body>
        <svg width="450" height="280"></svg>
        <script>
            const data = {json.dumps(d3_data)};
            const svg = d3.select("svg");
            const width = +svg.attr("width"), height = +svg.attr("height");

            const sim = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links).id(d => d.id).distance(90))
                .force("charge", d3.forceManyBody().strength(-200))
                .force("center", d3.forceCenter(width / 2, height / 2));

            const link = svg.append("g").selectAll("line").data(data.links).enter().append("line").attr("class", "link");
            const node = svg.append("g").selectAll("circle").data(data.nodes).enter().append("circle").attr("class", "node").attr("r", 15)
                .call(d3.drag().on("start", dragS).on("drag", dragging).on("end", dragE));
            const text = svg.append("g").selectAll("text").data(data.nodes).enter().append("text").attr("dx", 20).attr("dy", 5).text(d => d.name);

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
    components.html(d3_html, height=300, scrolling=False)
